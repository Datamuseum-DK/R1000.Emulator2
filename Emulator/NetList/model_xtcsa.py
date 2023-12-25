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
   TYP CSA logic
   =============

'''

from part import PartModel, PartFactory

class XTCSA(PartFactory):
    ''' TYP CSA logic '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t elprom[512];
		|	uint8_t sr;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->elprom, sizeof state->elprom,
		|	    "PA060");
		|''')
        super().init(file)

    def xxsensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	bool invlast = (state->sr >> 1) & 1;
		|	bool pdc1 = state->sr & 1;
		|	bool invalidate_csa = !(PIN_CSAHIT=> && !pdc1);
		|	unsigned hit_offs;
		|	BUS_HITOF_READ(hit_offs);
		|
		|	unsigned adr;
		|	if (pdc1) {
		|		adr = state->sr >> 4;
		|		adr |= 0x100;
		|	} else {
		|		BUS_HITOF_READ(adr);
		|	}
		|	adr ^= 0xf;
		|	unsigned csacntl;
		|	BUS_CSACT_READ(csacntl);
		|	adr |= csacntl << 4;
		|
		|	if (invlast)
		|		adr |= (1<<7);
		|
		|	output.nve = state->elprom[adr] >> 4;
		|	unsigned q = state->elprom[adr];
		|	bool load_ctl_top = (q >> 3) & 0x1;
		|	bool load_top_bot = (q >> 2) & 0x1;
		|	bool sel_constant = (q >> 1) & 0x1;
		|	bool minus_one = (q >> 0) & 0x1;
		|
		|	output.ldtop = !(load_top_bot && ((csacntl >> 1) & 1));
		|	output.ldbot = !(load_top_bot && ((csacntl >> 2) & 1));
		|	output.popdn = load_ctl_top && pdc1;
		|
		|	if (!invalidate_csa) {
		|		output.csaof = 0xf;
		|	} else if (!sel_constant && !minus_one) {
		|		output.csaof = 0x1;
		|	} else if (!sel_constant && minus_one) {
		|		output.csaof = 0xf;
		|	} else {
		|		output.csaof = hit_offs;
		|	}
		|
		|	if (PIN_CSACLK.posedge()) {
		|		if (PIN_UIRSL0=>) {
		|			state->sr = state->output.nve << 4;
		|			if (load_ctl_top) state->sr |= 0x8;
		|			if (load_top_bot) state->sr |= 0x4;
		|			if (invalidate_csa) state->sr |= 0x2;
		|			if (PIN_TFPRED=>) state->sr |= 0x1;
		|		} else {
		|			state->sr >>= 1;
		|			if (PIN_DIAG14=>)
		|				state->sr |= 0x80;
		|		}
		|		output.pdcyc1 = state->sr & 0x01;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCSA", PartModel("XTCSA", XTCSA))
