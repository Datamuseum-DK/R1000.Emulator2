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
		|	uint8_t bhreg;
		|	unsigned rreg;
		|	unsigned lreg;
		|	unsigned treg;
		|	bool hint_last;
		|	bool hint_t_last;
		|	bool last_late_cond;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_TCLR"
        yield "PIN_COND"
        yield "PIN_LCOND"
        yield "PIN_BADH"
        yield "BUS_BRTIM"
        yield "BUS_BRTYP"
        yield "PIN_MPRND"

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom43, sizeof state->prom43,
		|	    "PA043-02");
		|	load_programmable(this->name(),
		|	    state->prom44, sizeof state->prom44,
		|	    "PA044-01");
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	bool bad_hint = PIN_BADH=>;
		|
		|	bool brtm3;
		|	unsigned btimm;
		|	if (bad_hint) {
		|		btimm = 2;
		|		brtm3 = ((state->bhreg) >> 5) & 1;
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
		|	if (state->bhreg & 0x20) adr |= 0x20;
		|	if (state->bhreg & 0x40) adr |= 0x80;
		|	if (state->bhreg & 0x80) adr |= 0x100;
		|	unsigned rom = state->prom43[adr];
		|
		|	bool wanna_dispatch = !(((rom >> 5) & 1) && !output.uasel);
		|	output.wdisp  = wanna_dispatch;
		|	output.rtn    = !(((rom >> 3) & 1) ||  output.uasel);
		|	output.pushbr =    (rom >> 1) & 1;
		|	output.push   = !(((rom >> 0) & 1) ||
		|		        !(((rom >> 2) & 1) || !output.uasel));
		|
		|	if (PIN_CLK.posedge()) {
		|		adr = 0;
		|		if (PIN_UEVENT=>) adr |= 0x02;
		|		if (PIN_MEVENT=>) adr |= 0x04;
		|		adr |= btimm << 3;
		|		adr |= br_type << 5;
		|		rom = state->prom44[adr];
		|
		|		if (PIN_SCLKE=>) {
		|			rom |= 0x2;
		|		} else {
		|			rom ^= 0x2;
		|		}
		|		unsigned mode = 3;
		|		if (!PIN_BHCKE=>) {
		|			mode = 0;
		|			state->bhreg = rom;
		|		}
		|
		|		state->hint_last = (state->bhreg >> 1) & 1;
		|		state->hint_t_last = (state->bhreg >> 0) & 1;
		|	}
		|	output.dtime = !(!bad_hint && (state->bhreg & 0x10));
		|	output.dbhint = !(!bad_hint || (state->bhreg & 0x08));
		|	bool bhint2 = (!bad_hint || (state->bhreg & 0x08));
		|	output.dmdisp = !(!bad_hint || (state->bhreg & 0x04));
		|	if (!bad_hint) {
		|		output.mpcmb = PIN_MPRND=>;
		|	} else {
		|		output.mpcmb = !((state->bhreg >> 2) & 1);
		|	}
       		| 
		|	if (!PIN_TCLR=>) {
		|		state->treg = 0;
		|		output.fo7 = false;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		if (PIN_SSTOP=> && PIN_BHEN=> && bhint2) {
		|			unsigned restrt_rnd;
		|			BUS_RRND_READ(restrt_rnd);
		|			if (!wanna_dispatch) {
		|				state->rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->rreg = (restrt_rnd & 0x3) << 1;
		|			} else {
		|				state->rreg &= 0xa;
		|			}
		|			if (PIN_MEV=>) {
		|				state->rreg &= ~0x2;
		|			}
		|			BUS_TIN_READ(state->treg);
		|			state->treg ^= 0x4;
		|		} else if (PIN_SSTOP=> && PIN_BHEN=>) {
		|			state->rreg <<= 1;
		|			state->rreg &= 0xe;
		|			state->rreg |= 0x1;
		|			state->treg <<= 1;
		|			state->treg &= 0xe;
		|			state->treg |= 0x1;
		|		}
		|		output.rq = state->rreg;
		|		output.fo7 = state->treg >> 3;
		|
		|		unsigned lin;
		|		BUS_LIN_READ(lin);
		|
		|		if (!PIN_SCLKE=>) {
		|			state->lreg = lin;
		|		}
		|
		|		if ((lin & 0x4) && !PIN_SCLKE=>) {
		|			state->last_late_cond = PIN_COND=>;
		|		}
		|
		|		switch(state->lreg & 0x6) {
		|		case 0x0:
		|		case 0x4:
		|			output.ldc = (state->lreg >> 3) & 1;
		|			break;
		|		case 0x2:
		|			output.ldc = (state->lreg >> 0) & 1;
		|			break;
		|		case 0x6:
		|			output.ldc = state->last_late_cond;
		|			break;
		|		}
		|	}
		|
		|	bool last_cond_late = (state->lreg >> 2) & 1;
		|	if (state->hint_last) {
		|		output.bhp = false;
		|	} else if (!last_cond_late && !state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		output.bhp = e_or_ml_cond;
		|	} else if (!last_cond_late &&  state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		output.bhp = !e_or_ml_cond;
		|	} else if ( last_cond_late && !state->hint_t_last) {
		|		output.bhp = state->last_late_cond;
		|	} else if ( last_cond_late &&  state->hint_t_last) {
		|		output.bhp = !state->last_late_cond;
		|	}
		|	output.bhn = !output.bhp;
		|		
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSUDEC", PartModel("XSUDEC", XSUDEC))
