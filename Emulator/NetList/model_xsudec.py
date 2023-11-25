#!/usr/local/bin/python3
#
# Copyright (c) 2023 Poul-Henning Kamp
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
   SEQ uins decode
   ===============

'''

from part import PartModel, PartFactory

class XSUDEC(PartFactory):
    ''' SEQ uins decode '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t prom43[512];
		|	uint8_t prom44[512];
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom43, sizeof state->prom43,
		|	    "PA043-02");
		|	load_programmable(this->name(),
		|	    state->prom44, sizeof state->prom44,
		|	    "PA044-01");
		|''')
        super().init(file)

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|
		|	bool bad_hint = PIN_BADH=>;
		|
		|	unsigned group_sel;
		|	switch(br_type) {
		|	case 0x0: group_sel = 3; break;
		|	case 0x1: group_sel = 3; break;
		|	case 0x2: group_sel = 3; break;
		|	case 0x3: group_sel = 3; break;
		|	case 0x4: group_sel = 3; break;
		|	case 0x5: group_sel = 3; break;
		|	case 0x6: group_sel = 3; break;
		|	case 0x7: group_sel = 3; break;
		|	case 0x8: group_sel = 2; break;
		|	case 0x9: group_sel = 2; break;
		|	case 0xa: group_sel = 2; break;
		|	case 0xb: group_sel = 0; break;
		|	case 0xc: group_sel = 1; break;
		|	case 0xd: group_sel = 1; break;
		|	case 0xe: group_sel = 1; break;
		|	case 0xf: group_sel = 0; break;
		|	}
		|	output.gsel = group_sel;
		|
		|	bool brtm3;
		|	unsigned btimm;
		|	if (bad_hint) {
		|		btimm = 2;
		|		brtm3 = PIN_BRBH3=>;
		|	} else {
		|		BUS_BRTIM_READ(btimm);
		|		brtm3 = br_type & 1;
		|	}
		|
		|	switch (btimm) {
		|	case 0: output.uasel = !PIN_COND=>; break;
		|	case 1: output.uasel = !PIN_LCOND=>; break;
		|	case 2: output.uasel = false; break;
		|	case 3: output.uasel = true; break;
		|	}
		|	if (brtm3)
		|		output.uasel = !output.uasel;
		|
		|	unsigned adr = 0;
		|	if (bad_hint) adr |= 0x01;
		|	adr |= (br_type << 1);
		|	if (PIN_BRBH3=>) adr |= 0x20;
		|	if (PIN_BRBH1=>) adr |= 0x80;
		|	if (PIN_BRBH0=>) adr |= 0x100;
		|	unsigned rom = state->prom43[adr];
		|
		|	output.wdisp  = !(((rom >> 5) & 1) && !output.uasel);
		|	output.casen  = !(((rom >> 4) & 1) && !output.uasel);
		|	output.rtn    = !(((rom >> 3) & 1) ||  output.uasel);
		|	output.pushbr =    (rom >> 1) & 1;
		|	output.push   = !(((rom >> 0) & 1) ||
		|		        !(((rom >> 2) & 1) || !output.uasel));
		|
		|	adr = 0;
		|	if (PIN_UEVENT=>) adr |= 0x02;
		|	if (PIN_MEVENT=>) adr |= 0x04;
		|	adr |= btimm << 3;
		|	adr |= br_type << 5;
		|	rom = state->prom44[adr];
		|
		|	if (PIN_SCLKEN=>) {
		|		rom |= 0x2;
		|	} else {
		|		rom ^= 0x2;
		|	}
		|	output.rom = rom;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSUDEC", PartModel("XSUDEC", XSUDEC))
