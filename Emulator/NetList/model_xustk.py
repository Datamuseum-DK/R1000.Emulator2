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
   Micro Stack
   ===========

'''

from part import PartModelDQ, PartFactory

class XUSTK(PartFactory):
    ''' Micro Stack '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint16_t nxtuadr;	// Z029
		|	uint16_t curuadr;	// Z029
		|	uint16_t ram[16];
		|	uint16_t topu;
		|	uint16_t adr;
		|	unsigned fiu;
		|	unsigned other;
		|	unsigned late_u;
		|	unsigned prev;
		|	unsigned uei;
		|	unsigned uev;
		|
		|	uint8_t prom43[512];
		|	uint8_t prom44[512];
		|	uint8_t bhreg;
		|	unsigned rreg;
		|	unsigned lreg;
		|	unsigned treg;
		|	bool hint_last;
		|	bool hint_t_last;
		|	bool last_late_cond;
		|	bool uadr_mux, preturn, push_br, push;
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

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_QFOE"
        yield "PIN_QVOE"

        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LCLK.pos()"
        yield "PIN_ACLK.pos()"
        yield "PIN_DV_U"
        # yield "PIN_BAD_HINT"

        yield "PIN_TCLR"
        yield "PIN_COND"
        yield "BUS_BRTIM"
        yield "BUS_BRTYP"
        yield "PIN_MPRND"

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned group_sel(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|unsigned
		|SCM_«mmm» ::
		|group_sel(void)
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	unsigned retval;
		|	switch(br_type) {
		|	case 0x0: retval = 3; break;
		|	case 0x1: retval = 3; break;
		|	case 0x2: retval = 3; break;
		|	case 0x3: retval = 3; break;
		|	case 0x4: retval = 3; break;
		|	case 0x5: retval = 3; break;
		|	case 0x6: retval = 3; break;
		|	case 0x7: retval = 3; break;
		|	case 0x8: retval = 2; break;
		|	case 0x9: retval = 2; break;
		|	case 0xa: retval = 2; break;
		|	case 0xb: retval = 0; break;
		|	case 0xc: retval = 1; break;
		|	case 0xd: retval = 1; break;
		|	case 0xe: retval = 1; break;
		|	case 0xf: retval = 0; break;
		|	}
		|	if (state->uadr_mux) {
		|		retval |= 4;
		|	}
		|	return (retval);
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|{
		|	bool q2pos = PIN_Q2.posedge();
		|	bool stkclk = PIN_Q4.posedge() && PIN_SSTOP=> && output.macro_hic;
		|	bool uevent = output.u_event;
		|
		|	if (q2pos) {
		|		state->ram[(state->adr + 1) & 0xf] = state->topu;
		|	}
		|
		|	if (stkclk) {
		|		bool xwrite;
		|		bool pop;
		|		bool stkinpsel_0;
		|		bool stkinpsel_1;
		|		if (uevent) {
		|			xwrite = true;
		|			pop = true;
		|			stkinpsel_0 = true;
		|			stkinpsel_1 = true;
		|		} else if (!state->push) {
		|			xwrite = true;
		|			pop = false;
		|			stkinpsel_0 = !state->push_br;
		|			stkinpsel_1 = output.bhp;
		|		} else {
		|			xwrite = !PIN_PUSHRND=>;
		|			pop = !!(state->preturn || PIN_POPRND=>);
		|			stkinpsel_0 = false;
		|			stkinpsel_1 = true;
		|		}
		|
		|		unsigned stkinpsel = 0;
		|		if (stkinpsel_0) stkinpsel |= 2;
		|		if (stkinpsel_1) stkinpsel |= 1;
		|
		|		if (xwrite) {
		|			switch(stkinpsel) {
		|			case 0:
		|				BUS_BRN_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 1:
		|				BUS_DF_READ(state->topu);
		|				state->topu &= 0xffff;
		|				break;
		|			case 2:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 3:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			}
		|		} else if (pop) {
		|			state->topu = state->ram[state->adr];
		|		}
		|		output.svlat = !((state->topu >> 14) & 0x1);
		|
		|		if (PIN_CSR=> && PIN_STOP=>) {
		|			state->adr = xwrite;
		|		} else if (xwrite || pop) {
		|			if (xwrite) {
		|				state->adr = (state->adr + 1) & 0xf;
		|			} else {
		|				state->adr = (state->adr + 0xf) & 0xf;
		|			}
		|		}
		|		output.ssz = state->adr == 0;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = state->topu ^ 0xffff;
		|		output.qf ^= 0xffff;
		|	}
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = state->topu ^ 0xffff;
		|		output.qv ^= BUS_QV_MASK;
		|	}
		|
		|	unsigned data = 0, sel;
		|	bool macro_hic = true;
		|	bool u_event = true;
		|
		|	if (PIN_FIU_CLK.posedge()) {
		|		BUS_DF_READ(state->fiu);
		|		state->fiu &= 0x3fff;
		|	}	
		|
		|	if (PIN_LCLK.posedge()) {
		|		BUS_LATE_READ(state->late_u);
		|		sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|		case 7:
		|			data = state->curuadr;
		|			data += 1;
		|			break;
		|		case 1:
		|		case 2:
		|		case 3:
		|			BUS_BRN_READ(data);
		|			break;
		|		case 4:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 5:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 6:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		default:
		|			abort();
		|		}
		|		state->other = data;
		|	}
		|
		|	if (!PIN_DV_U) {
		|		data = state->nxtuadr;
		|	} else if (output.bhp) {
		|		data = state->other;
		|	} else if (PIN_LMAC=>) {
		|		// Not tested by expmon_test_seq ?
		|		data = state->late_u << 3;
		|		data ^= (7 << 3);
		|		data |= 0x0140;
		|		macro_hic = false;
		|	} else if (state->uei != 0) {
		|		data = state->uev;
		|		data <<= 3;
		|		data |= 0x0180;
		|		u_event = false;
		|	} else {
		|		sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 2:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		case 3:
		|		case 4:
		|			data = state->curuadr;
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|	}
		|	if (q2pos) {
		|
		|		output.nu = data;
		|	}
		|
		|	output.macro_hic = macro_hic;
		|	output.u_event = !u_event;
		|	output.u_eventnot = u_event;
		|
		|	if (PIN_ACLK.posedge()) {
		|		BUS_UEI_READ(state->uei);
		|		state->uei <<= 1;
		|		state->uei |= 1;
		|		state->uei ^= 0xffff;
		|		state->uev = 16 - fls(state->uei);
		|		output.uevp = state->uei == 0;
		|
		|		if (PIN_SSTOP=> && PIN_DMODE=>) {
		|			state->curuadr = output.nu;
		|		}
		|	}
		|}
		|''')

        file.fmt('''
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	bool bad_hint = output.bhp;
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
		|	case 0: state->uadr_mux = !PIN_COND=>; break;
		|	case 1: state->uadr_mux = !output.ldc; break;
		|	case 2: state->uadr_mux = false; break;
		|	case 3: state->uadr_mux = true; break;
		|	}
		|	if (brtm3)
		|		state->uadr_mux = !state->uadr_mux;
		|
		|	unsigned adr = 0;
		|	if (bad_hint) adr |= 0x01;
		|	adr |= (br_type << 1);
		|	if (state->bhreg & 0x20) adr |= 0x20;
		|	if (state->bhreg & 0x40) adr |= 0x80;
		|	if (state->bhreg & 0x80) adr |= 0x100;
		|	unsigned rom = state->prom43[adr];
		|
		|	bool wanna_dispatch = !(((rom >> 5) & 1) && !state->uadr_mux);
		|	output.wdisp  = wanna_dispatch;
		|	state->preturn = !(((rom >> 3) & 1) ||  state->uadr_mux);
		|	state->push_br =    (rom >> 1) & 1;
		|	state->push   = !(((rom >> 0) & 1) ||
		|		        !(((rom >> 2) & 1) || !state->uadr_mux));
		|
		|	if (PIN_ACLK.posedge()) {
		|		adr = 0;
		|		if (output.u_eventnot) adr |= 0x02;
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
		|	if (PIN_ACLK.posedge()) {
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
		|		lin &= 0x7;
		|		lin |= output.ldc << 3;
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
		|}
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XUSTK", PartModelDQ("XUSTK", XUSTK))

class XSUDEC(PartFactory):
    ''' SEQ uins decode '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

