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
		|	bool invalidate_csa = !(PIN_CSAHIT=> && !mp_tcsa_tp);
		|	unsigned hit_offs;
		|	BUS_HITOF_READ(hit_offs);
		|
		|	unsigned adr;
		|	if (mp_tcsa_tp) {
		|		adr = mp_tcsa_sr;
		|		adr |= 0x100;
		|	} else {
		|		BUS_HITOF_READ(adr);
		|	}
		|	adr ^= 0xf;
		|	unsigned csacntl = mp_csa_cntl;
		|	adr |= csacntl << 4;
		|
		|	if (mp_tcsa_ic)
		|		adr |= (1<<7);
		|
		|	unsigned q = state->pa060[adr];
		|
		|	bool load_ctl_top = (q >> 3) & 0x1;
		|	bool load_top_bot = (q >> 2) & 0x1;
		|	bool sel_constant = (q >> 1) & 0x1;
		|	bool minus_one = (q >> 0) & 0x1;
		|
		|if (0) {
		|	mp_load_top = !(load_top_bot && ((csacntl >> 1) & 1));
		|	mp_load_bot = !(load_top_bot && ((csacntl >> 2) & 1));
		|	mp_pop_down = load_ctl_top && mp_tcsa_tp;
		|
		|	if (!invalidate_csa) {
		|		mp_csa_offs = 0xf;
		|	} else if (!sel_constant && !minus_one) {
		|		mp_csa_offs = 0x1;
		|	} else if (!sel_constant && minus_one) {
		|		mp_csa_offs = 0xf;
		|	} else {
		|		mp_csa_offs = hit_offs;
		|	}
		|	mp_csa_nve = q >> 4;
		|}
		|
		|	if (PIN_CSACLK.posedge()) {
		|		mp_tcsa_sr = q >> 4;
		|		mp_tcsa_tp = PIN_TFPRED=>;
		|		mp_tcsa_ic = invalidate_csa;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCSA", PartModel("XTCSA", XTCSA))
