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
		|	uint8_t pa060[512];
		|	uint8_t sr;
		|	bool inval_csa;
		|	bool tf_pred;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->pa060, sizeof state->pa060, "PA060");
		|''')

    def sensitive(self):
        yield "BUS_HITOF"
        yield "BUS_CSACT"
        yield "PIN_CSACLK.pos()"
        yield "PIN_CSAHIT"

    def doit(self, file):

        file.fmt('''
		|
		|	bool invalidate_csa = !(PIN_CSAHIT=> && !state->tf_pred);
		|	unsigned hit_offs;
		|	BUS_HITOF_READ(hit_offs);
		|
		|	unsigned adr;
		|	if (state->tf_pred) {
		|		adr = state->sr;
		|		adr |= 0x100;
		|	} else {
		|		BUS_HITOF_READ(adr);
		|	}
		|	adr ^= 0xf;
		|	unsigned csacntl;
		|	BUS_CSACT_READ(csacntl);
		|	adr |= csacntl << 4;
		|
		|	if (state->inval_csa)
		|		adr |= (1<<7);
		|
		|	unsigned q = state->pa060[adr];
		|	bool load_ctl_top = (q >> 3) & 0x1;
		|	bool load_top_bot = (q >> 2) & 0x1;
		|	bool sel_constant = (q >> 1) & 0x1;
		|	bool minus_one = (q >> 0) & 0x1;
		|
		|	output.ldtop = !(load_top_bot && ((csacntl >> 1) & 1));
		|	output.ldbot = !(load_top_bot && ((csacntl >> 2) & 1));
		|	output.popdn = load_ctl_top && state->tf_pred;
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
		|		state->sr = output.nve;
		|		state->inval_csa = invalidate_csa;
		|		state->tf_pred = PIN_TFPRED=>;
		|	}
		|	output.nve = q >> 4;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCSA", PartModel("XTCSA", XTCSA))
