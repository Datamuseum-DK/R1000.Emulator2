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


from part import PartModel, PartFactory

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

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t typ, val, tmp, cbo = 0, cbi;
		|
		|	BUS_T_READ(typ);
		|	BUS_V_READ(val);
		|
		|	if (!PIN_GEN=>) {
		|		BUS_CBI_READ(cbi);
		|		cbi ^= BUS_CBI_MASK;
		|	} else {
		|		cbi = 0;
		|	}
		|
		|	output.pt = odd_parity64(typ) ^ 0xff;
		|
		|	output.pv = odd_parity64(val) ^ 0xff;
		|
		|''')

        for tmask, vmask, invert in self.getmasks():
            file.fmt('\n\ttmp = (typ & 0x%016xULL) ^ (val & 0x%016xULL);\n' % (tmask, vmask))
            file.fmt('''
		|	tmp = odd_parity(odd_parity64(tmp)) & 0x1;
		|	cbo <<= 1;
		|	cbo |= tmp;
		|''')
            if invert:
                file.fmt('\tcbo ^= 1;\n')

        file.fmt('''
		|	output.cbo = cbo ^ cbi;
		|	output.err = output.cbo != 0;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XECC", PartModel("XECC", XECC))
