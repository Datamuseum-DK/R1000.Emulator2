#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
# All rights reserved.
#
# Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

'''
   128bit ECC checker/generator
   ============================

'''

CBITS = '''
           TYP:0                                                     TYP:63 VAL:0                                                     VAL:63 CHECKBIT
    ECCG16 --------------------------------++++++++++++++++++++++++++++++++ --------------------------------++++++++++++++++++++++++++++++++ +--------
    ECCG17 ++++++++++++++++++++++++++++++++-------------------------------- --------------------------------++++++++++++++++++++++++++++++++ -+-------
    ECCG28 ++++++++-----++---+++-+--+++--+-++++++++-----++---+++-+--+++--+- ++++++++-------+-----+-+--+-+-+----++---+-+-+--++++---++++-+---- --+------
    ECCG29 +++++++++++++-++++---+-------+--+++++++++++++-++++---+-------+-- -+------++++++++-------++----++-----+++++--+-++----+---+--++---+ ---+-----
    ECCG44 ++-----+++++++++--++--+++---+-++++-----+++++++++--++--+++-----++ ---+---+----+++---++++--++++------------++++++++---++++------++- ----+----
    ECCG45 -----++++--+---++++++++++++----+-----++++--+---++++++++++++-+--+ --+--++----+--+-++++++++-----+---++----+--------++++++++----+--+ -----+---
    ECCG46 +-++--+-++--+---++----+-+++++++++-++--+-++--+---++----+-++++++++ ----+-+--++------++---+-+++++++++-++--+--+----++--+-+----++-++-- ------+--
    ECCG61 -++-++----+-++-++-+-++-++-++++---++-++----+-++-++-+-++-++-++++-- +---++-++-+-+--++---+-+--+-----+++---+----+--+---+---+--++++++++ -------+-
    ECCG62 ---++----+++-++--+-+++-+-+-+++++---++----+++-++--+-+++-+-+-+++++ ++++----++-+-+--++-+-------++--+++++++++-+-++---+-------+-----+- --------+
'''


from part import PartModelDQ, PartFactory

class XECC(PartFactory):
    ''' IOC Full ECC/Parity implementation '''

    autopin = True

    def getmasks(self):
        invert = [0, 0, 0, 0, 1, 1, 1, 0, 0]
        for i in CBITS.split("\n"):
            if not "ECCG" in i:
                continue
            j = i.split()
            tmask = int(j[1].replace("-", "0").replace("+", "1"), 2)
            vmask = int(j[2].replace("-", "0").replace("+", "1"), 2)
            yield tmask, vmask, invert.pop(0)

    def state(self, file):
        file.fmt('''
		|	uint8_t elprom[512];
		|	uint8_t eidrg;
		|	unsigned cbreg1;
		|	unsigned cbreg2;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->elprom, sizeof state->elprom,
		|	    "PA115-01");
		|''')
        super().init(file)

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "write_event",
            "PIN_Q2.posedge_event()",
            "PIN_Q4.posedge_event()",
            "PIN_QTOE",
        )

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_QTOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t typ, val, tmp, cbo = 0, cbi;
		|
		|	BUS_T_READ(typ);
		|	BUS_V_READ(val);
		|
		|	if (!PIN_TVEN=>) {
		|		BUS_DC_READ(cbi);
		|	} else {
		|		cbi = 0;
		|	}
		|
		|''')

        for tmask, vmask, invert in self.getmasks():
            file.fmt('\n\ttmp = (typ & 0x%016xULL) ^ (val & 0x%016xULL);\n' % (tmask, vmask))
            file.fmt('''
		|	cbo <<= 1;
		|	cbo |= (uint64_t)__builtin_parityll(tmp);
		|''')
            if invert:
                file.fmt('\tcbo ^= 1;\n')

        file.fmt('''
		|	bool q4_pos = PIN_Q4.posedge();
		|
		|	if (q4_pos && !PIN_CSTP=> && !PIN_LDCB=>) {
		|		state->cbreg2 = (typ >> 7) & 0x1ff;
		|	}
		|
		|	cbo ^= cbi;
		|	output.z_qc = PIN_QCOE=>;
		|	if (!output.z_qc) {
		|		if (!PIN_DROT=>)
		|			output.qc = state->cbreg2;
		|		else
		|			output.qc = cbo;
		|	}
		|	output.err = cbo != 0;
		|
		|	if (!PIN_TVEN=> && state->eidrg != state->elprom[cbo]) {
		|		idle_next = &write_event;
		|	} else if (!PIN_LDCB=>) {
		|		idle_next = &write_event;
		|	}
		|
		|	if (q4_pos && !PIN_TVEN=>) {
		|		state->eidrg = state->elprom[cbo];
		|		output.cber = (state->eidrg & 0x81) != 0x81;
		|		output.mber = state->eidrg & 1;
		|		BUS_DC_READ(state->cbreg1);
		|		state->cbreg1 ^= BUS_DC_MASK;
		|	}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		output.qt = state->eidrg >> 1;
		|		output.qt |= state->cbreg1 << 7;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XECC", PartModelDQ("XECC", XECC))
