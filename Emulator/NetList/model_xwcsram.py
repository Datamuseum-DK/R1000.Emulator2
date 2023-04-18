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
   Writable Control Store RAM
   ==========================

'''


from part import PartModel, PartFactory

class XWCSRAM(PartFactory):

    ''' Writable Control Store RAM '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|''')

    def sensitive(self):
        yield "BUS_A_SENSITIVE()"
        yield "PIN_WE"
        if "POUT" in self.comp:
            yield "BUS_D_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr;
		|	BUS_A_READ(adr);
		|
		|''')

        if "APERR" in self.comp:
            file.fmt('''
		|	uint32_t a, b;
		|
		|	a = adr & 0x40ff;
		|	a = (a ^ (a >> 8)) & 0xff;
		|	a = (a ^ (a >> 4)) & 0x0f;
		|	a = (a ^ (a >> 2)) & 0x03;
		|	a = (a ^ (a >> 1)) & 0x01;
		|	b = adr & 0xbf00;
		|	b = (b ^ (b >> 8)) & 0xff;
		|	b = (b ^ (b >> 4)) & 0x0f;
		|	b = (b ^ (b >> 2)) & 0x03;
		|	b = (b ^ (b >> 1)) & 0x01;
		|
		|	PIN_APERR<=(!a && !b);
		|
		|	adr &= 0x3fff;
		|
		|''')

        assert "WE" in self.comp
        assert not self.comp.nodes["WE"].net.is_pu()
        file.fmt('''
		|	if (PIN_WE.posedge()) {
		|		BUS_D_READ(state->ram[adr]);
		|		TRACE(
		|		    << " w a " << BUS_A_TRACE()
		|		    << " d " << BUS_D_TRACE()
		|		    << " we " << PIN_WE?
		|		    << " adr " << std::hex << adr
		|		    << " data " << std::hex << (unsigned)state->ram[adr]
		|		);
		|	} else {
		|		TRACE(
		|		    << " r a " << BUS_A_TRACE()
		|		    << " we " << PIN_WE?
		|		    << " adr " << std::hex << adr
		|		    << " data " << std::hex << (unsigned)state->ram[adr]
		|		);
		|	}
		|	BUS_Q_WRITE(state->ram[adr]);
		|''')

        if "POUT" in self.comp:
            file.fmt('''
		|	uint64_t par;
		|	BUS_D_READ(par);
		|	par = (par ^ (par >> 32)) & 0xffffffff;
		|	par = (par ^ (par >> 16)) & 0xffff;
		|	par = (par ^ (par >> 8)) & 0xff;
		|	par = (par ^ (par >> 4)) & 0xf;
		|	par = (par ^ (par >> 2)) & 0x3;
		|	par = (par ^ (par >> 1)) & 0x1;
		|
		|	PIN_POUT<=(!(par ^ PIN_PIN=>));
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XWCSRAM", PartModel("XWCSRAM", XWCSRAM))
    part_lib.add_part("XWCSRAM16", PartModel("XWCSRAM16", XWCSRAM))
    part_lib.add_part("XWCSRAM39", PartModel("XWCSRAM39", XWCSRAM))
    part_lib.add_part("XWCSRAM40", PartModel("XWCSRAM40", XWCSRAM))
    part_lib.add_part("XWCSRAM42", PartModel("XWCSRAM42", XWCSRAM))
    part_lib.add_part("XWCSRAM47", PartModel("XWCSRAM47", XWCSRAM))
