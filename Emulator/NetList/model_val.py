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
   VAL C-bus mux
   =============

'''

from part import PartModelDQ, PartFactory

class VAL(PartFactory):
    ''' VAL C-bus mux '''

    autopin = True

    def state(self, file):

        file.fmt('''
		|	uint64_t rfram[1<<10];		// Z013
		|	uint64_t a, b, c;
		|	uint64_t wdr;
		|	uint64_t zerocnt;
		|	uint64_t malat, mblat, mprod, msrc;
		|	uint64_t nalu, alu;
		|	unsigned count;
		|	unsigned csa_offset;
		|	unsigned topreg;
		|	unsigned botreg;
		|	bool csa_hit;
		|	bool csa_write;
		|	unsigned cadr;
		|	bool amsb, bmsb, cmsb, mbit, last_cond;
		|	bool isbin, sub_else_add, ovren, carry_middle;
		|	bool coh;
		|	bool wen;
		|	bool cwe;
		|	uint64_t *wcsram;
		|	uint64_t uir;
		|
		|#define VUIR_A		((state->uir >> (39-5)) & 0x3f)
		|#define VUIR_B		((state->uir >> (39-11)) & 0x3f)
		|#define VUIR_FRM	((state->uir >> (39-16)) & 0x1f)
		|#define VUIR_SEL	((state->uir >> (39-18)) & 0x3)
		|#define VUIR_RAND	((state->uir >> (39-22)) & 0xf)
		|#define VUIR_C		((state->uir >> (39-28)) & 0x3f)
		|#define VUIR_MSRC	((state->uir >> (39-32)) & 0xf)
		|#define VUIR_AFNC	((state->uir >> (39-37)) & 0x1f)
		|#define VUIR_CSRC	((state->uir >> (39-38)) & 0x1)
		|''')


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), pa010, sizeof pa010, "PA010");
		|	load_programmable(this->name(), pa011, sizeof pa011, "PA011");
		|	state->wcsram = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
		|	state->csa_hit = true;
		|	state->csa_write = true;
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned rand = 0;
		|	uint8_t pa010[512];
		|	uint8_t pa011[512];
		|	bool thiscond = false;
		|
		|	bool ovrsgn(void);
		|	void val_cond(void);
		|	bool fiu_cond(void);
		|	void find_a(void);
		|	void find_b(void);
		|	void val_h1(void);
		|	void val_q2(void);
		|	void val_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|
		|bool
		|SCM_«mmm» ::
		|ovrsgn(void)
		|{
		|	bool a0 = state->amsb;
		|	bool b0 = state->bmsb;
		|	bool se = state->isbin;
		|	return (!(
		|		(se && (a0 ^ b0)) ||
		|		(!se && !a0)
		|	));
		|}
		|
		|void
		|SCM_«mmm» ::
		|val_cond(void)
		|{
		|	unsigned csel = mp_cond_sel;
		|	if ((csel & 0x78) == 0x58)
		|		csel ^= 0x58;
		|	switch(csel) {
		|	case 0x00:	// L VAL_ALU_ZERO
		|		thiscond = (state->nalu != 0);
		|		break;
		|	case 0x01:	// L VAL_ALU_NONZERO
		|		thiscond = (state->nalu == 0);
		|		break;
		|	case 0x02:	// L VAL_ALU_A_LT_OR_LE_B
		|		thiscond = !(
		|			(state->bmsb && (state->amsb ^ state->bmsb)) ||
		|			(!state->coh && (ovrsgn() ^ state->sub_else_add))
		|		);
		|		break;
		|	case 0x03:	// SPARE
		|		thiscond = true;
		|		break;
		|	case 0x04:	// E VAL_LOOP_COUNTER_ZERO
		|		thiscond = state->count != 0x3ff;
		|		break;
		|	case 0x05:	// SPARE
		|		thiscond = true;
		|		break;
		|	case 0x06:	// L VAL_ALU_NONZERO
		|		thiscond = (state->nalu == 0);
		|		break;
		|	case 0x07:	// L VAL_ALU_32_CO
		|		thiscond = state->carry_middle;
		|		break;
		|	case 0x08:	// L VAL_ALU_CARRY
		|		thiscond = !state->coh;
		|		break;
		|	case 0x09:	// L VAL_ALU_OVERFLOW
		|		thiscond = state->ovren || !(ovrsgn() ^ state->sub_else_add ^ (!state->coh) ^ state->cmsb);
		|		break;
		|	case 0x0a:	// L VAL_ALU_LT_ZERO
		|		thiscond = state->cmsb;
		|		break;
		|	case 0x0b:	// L VAL_ALU_LE_ZERO
		|		thiscond = !state->cmsb || (state->nalu == 0);
		|		break;
		|	case 0x0c:	// ML VAL_SIGN_BITS_EQUAL
		|		thiscond = (state->amsb ^ state->bmsb);
		|		break;
		|	case 0x0d:	// SPARE
		|		thiscond = true;
		|		break;
		|	case 0x0e:	// SPARE
		|		thiscond = true;
		|		break;
		|	case 0x0f:	// E VAL_PREVIOUS
		|		thiscond = state->last_cond;
		|		break;
		|	case 0x10:	// L VAL_ALU_32_ZERO
		|		thiscond = (state->nalu >> 32);
		|		break;
		|	case 0x11:	// L VAL_ALU_40_ZERO
		|		thiscond = (state->nalu >> 16);
		|		break;
		|	case 0x12:	// L VAL_ALU_MIDDLE_ZERO
		|		thiscond = (state->nalu & 0xffff0000ULL);
		|		break;
		|	case 0x13:	// E VAL_Q_BIT
		|		thiscond = mp_q_bit;
		|		break;
		|	case 0x14:	// SPARE
		|		thiscond = true;
		|		break;
		|	case 0x15:	// E VAL_M_BIT
		|		thiscond = state->mbit;
		|		break;
		|	case 0x16:	// E VAL_TRUE
		|		thiscond = false;
		|		break;
		|	case 0x17:	// E VAL_FALSE
		|		thiscond = true;
		|		break;
		|	default:
		|		break;
		|	}
		|	switch (csel >> 3) {
		|	case 0x0:
		|		mp_condxf = !thiscond;
		|		break;
		|	case 0x1:
		|		mp_condxe = !thiscond;
		|		break;
		|	case 0x2:
		|		mp_condxd = !thiscond;
		|		break;
		|	default:
		|		break;
		|	}
		|}
		|
		|bool
		|SCM_«mmm» ::
		|fiu_cond(void)
		|{
		|	unsigned csel = mp_cond_sel;
		|	bool fcond;
		|	switch (csel) {
		|	case 0x00:
		|		fcond = state->nalu == 0;
		|		break;
		|	case 0x01:
		|		fcond = state->nalu != 0;
		|		break;
		|	case 0x02:
		|		if (state->amsb ^ state->bmsb) {
		|			fcond = state->bmsb;
		|		} else {
		|			fcond = !state->coh;
		|		}
		|		break;
		|	case 0x0f:
		|	case 0x16:		// Undocumented
		|		fcond = state->last_cond;
		|		break;
		|	default:
		|		ALWAYS_TRACE(
		|			<< std::hex << "BAD FIUCOND"
		|			<< " csel " << csel
		|		);
		|		fcond = true;
		|		// assert(false);
		|		break;
		|	}
		|	return (!fcond);
		|}
		|
		|void
		|SCM_«mmm» ::
		|find_a(void)
		|{
		|	unsigned uira = VUIR_A;
		|	if (uira == 0x28) {
		|		state->a = state->count;
		|		state->a |= ~0x3ff;
		|	} else if (uira == 0x29) {
		|		unsigned mdst;
		|		bool prod_16 = rand != 0xd;
		|		bool prod_32 = rand != 0xe;
		|		mdst = prod_32 << 1;
		|		mdst |= prod_16;
		|		switch(mdst) {
		|		case 0: state->a = 0; break;
		|		case 1: state->a = state->mprod << 32; break;
		|		case 2: state->a = state->mprod << 16; break;
		|		case 3: state->a = state->mprod <<  0; break;
		|		}
		|		state->a = ~state->a;
		|	} else if (uira == 0x2a) {
		|		state->a = state->zerocnt;
		|	} else if (uira == 0x2b) {
		|		state->a = ~0ULL;
		|	} else {
		|		unsigned aadr = 0;
		|		if (uira == 0x2c) {
		|			aadr = state->count;
		|		} else if (uira <= 0x1f) {
		|			aadr = VUIR_FRM << 5;
		|			aadr |= uira & 0x1f;
		|		} else if (uira <= 0x2f) {
		|			aadr |= (uira + state->topreg + 1) & 0xf;
		|		} else {
		|			aadr |= uira & 0x1f;
		|		}
		|		state->a = state->rfram[aadr];
		|	}
		|	state->amsb = state->a >> 63;
		|}
		|
		|void
		|SCM_«mmm» ::
		|find_b(void)
		|{
		|	unsigned uirb = VUIR_B;
		|	bool oe, oe7;
		|	if (uirb != 0x29) {
		|		oe = false;
		|	} else if (!state->csa_hit && !mp_valv_oe) { 
		|		oe = false;
		|	} else {
		|		oe = true;
		|	}
		|
		|	oe7 = oe || (rand == 0x6);
		|
		|	unsigned badr = 0;
		|	if (!oe || !oe7) {
		|		if (uirb == 0x2c) {
		|			badr = state->count;
		|		} else if (uirb <= 0x1f) {
		|			badr = VUIR_FRM << 5;
		|			badr |= uirb & 0x1f;
		|		} else if (uirb <= 0x27) {
		|			unsigned btos = (uirb & 0xf) + state->topreg + 1;
		|			badr |= btos & 0xf;
		|		} else if (uirb <= 0x2b) {
		|			unsigned csa = state->botreg + (uirb&1);
		|			if (!(uirb & 2)) {
		|				csa += state->csa_offset;
		|			}
		|			badr |= csa & 0xf;
		|		} else if (uirb <= 0x2f) {
		|			unsigned btos = (uirb & 0xf) + state->topreg + 1;
		|			badr |= btos & 0xf;
		|		} else {
		|			badr |= uirb & 0x1f;
		|		}
		|	}
		|	state->b = 0;
		|	if (!oe) {
		|		state->b |= state->rfram[badr] & ~0xffULL;
		|	} else {
		|		state->b |= ~mp_val_bus & ~0xffULL;
		|	}
		|	if (!oe7) {
		|		state->b |= state->rfram[badr] & 0xffULL;
		|	} else {
		|		state->b |= ~mp_val_bus & 0xffULL;
		|	}
		|	state->bmsb = state->b >> 63;
		|}
		| 
		|void
		|SCM_«mmm» ::
		|val_q2(void)
		|{
		|
		|	bool divide = rand != 0xb;
		|	unsigned uirc = VUIR_C;
		|	if (mp_fiu_oe != 0x02) {
		|		find_a();
		|	}
		|	if (mp_valv_oe) {
		|		find_b();
		|	}
		|	state->wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|	if (state->cwe && uirc != 0x28)
		|		state->wen = !state->wen;
		|
		|	state->msrc = VUIR_MSRC;
		|	bool start_mult = rand != 0xc;
		|	if (!start_mult) {
		|		state->malat = ~state->a;
		|		state->mblat = ~state->b;
		|	}
		|
		|	struct f181 f181l, f181h;
		|	unsigned tmp, proma, alur;
		|
		|	tmp = VUIR_RAND;
		|	if (tmp < 8) {
		|		alur = 7;
		|	} else {
		|		alur = 15 - tmp;
		|	}
		|
		|	proma = VUIR_AFNC;
		|	proma |= alur << 5;
		|	if (
		|		!(
		|			(state->last_cond && divide) ||
		|			(mp_q_bit && !divide)
		|		)
		|	) {
		|		proma |= 0x100;
		|	}
		|
		|	tmp = pa011[proma];			// S0-4.LOW
		|	state->isbin = (tmp >> 1) & 1;			// IS_BINARY
		|	f181l.ctl = (tmp >> 4) & 0xf;
		|	f181l.ctl |= ((tmp >> 3) & 1) << 4;
		|	f181l.ctl |= 1 << 5;
		|	f181l.ci = (pa011[proma] >> 2) & 1;	// ALU.C15
		|	f181l.a = state->a & 0xffffffff;
		|	f181l.b = state->b & 0xffffffff;
		|	f181_alu(&f181l);
		|	state->carry_middle = f181l.co;
		|	state->nalu = f181l.o;
		|
		|	tmp = pa010[proma];			// S0-4.HIGH
		|	state->ovren = (tmp >> 1) & 1;			// OVR.EN~
		|	state->sub_else_add = (tmp >> 2) & 1;			// SUB_ELSE_ADD
		|	f181h.ctl = (tmp >> 4) & 0xf;
		|	f181h.ctl |= ((tmp>>3) & 1) << 4;
		|	f181h.ctl |= 1 << 5;
		|	f181h.ci = f181l.co;
		|	f181h.a = state->a >> 32;
		|	f181h.b = state->b >> 32;
		|	f181_alu(&f181h);
		|	state->coh = f181h.co;
		|	state->nalu |= ((uint64_t)f181h.o) << 32;
		|	state->alu = ~state->nalu;
		|	state->cmsb = state->alu >> 63;
		|	if (mp_adr_oe & 0x2) {
		|		uint64_t alu = state->alu;
		|
		|		if (mp_spc_bus != 4) {
		|			alu |=0xf8000000ULL;
		|		}
		|		mp_adr_bus = alu ^ ~0ULL;
		|	}
		|
		|	uint64_t fiu = 0, mux = 0;
		|	bool c_source = VUIR_CSRC;
		|	bool split_c_src = rand == 0x4;
		|	if (split_c_src || !c_source) {
		|		fiu = ~mp_fiu_bus;
		|	}
		|	if (!c_source && (rand == 3 || rand == 6)) {
		|		fiu &= ~1ULL;
		|		fiu |= fiu_cond();
		|	}
		|	if (c_source || split_c_src) {
		|		unsigned sel = VUIR_SEL;
		|		switch (sel) {
		|		case 0x0:
		|			mux = state->alu << 1;
		|			mux |= 1;
		|			break;
		|		case 0x1:
		|			mux = state->alu >> 16;
		|			mux |= 0xffffULL << 48;
		|			break;
		|		case 0x2:
		|			mux = state->alu;
		|			break;
		|		case 0x3:
		|			mux = state->wdr;
		|			break;
		|		}
		|	}
		|	if (!split_c_src && !c_source) {
		|		state->c = fiu;
		|	} else if (!split_c_src) {
		|		state->c = mux;
		|	} else if (c_source) {
		|		state->c = fiu & 0xffffffffULL;
		|		state->c |= mux & 0xffffffffULL << 32;
		|	} else {
		|		state->c = mux & 0xffffffffULL;
		|		state->c |= fiu & 0xffffffffULL << 32;
		|	}
		|
		|	state->cadr = 0;
		|	if (uirc <= 0x1f) {
		|		// FRAME:REG
		|		state->cadr |= uirc & 0x1f;
		|		state->cadr |= VUIR_FRM << 5;
		|	} else if (uirc <= 0x27) {
		|		// 0x20 = TOP-1
		|		// …
		|		// 0x27 = TOP-8
		|		state->cadr = (state->topreg + (uirc & 0x7) + 1) & 0xf;
		|	} else if (uirc == 0x28) {
		|		// 0x28 LOOP COUNTER (RF write disabled)
		|	} else if (uirc == 0x29 && state->cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		unsigned sum = state->botreg + state->csa_offset + 1;
		|		state->cadr |= sum & 0xf;
		|	} else if (uirc == 0x29 && !state->cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		state->cadr |= uirc & 0x1f;
		|		state->cadr |= VUIR_FRM << 5;
		|	} else if (uirc <= 0x2b) {
		|		// 0x2a BOT
		|		// 0x2b BOT-1
		|		state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|		state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|	} else if (uirc == 0x2c) {
		|		// 0x28 = LOOP_REG
		|		state->cadr = state->count;
		|	} else if (uirc == 0x2d) {
		|		// 0x2d SPARE
		|		assert (uirc != 0x2d);
		|	} else if (uirc <= 0x2f) {
		|		// 0x2e = TOP+1
		|		// 0x2f = TOP
		|		state->cadr = (state->topreg + (uirc & 0x1) + 0xf) & 0xf;
		|	} else if (uirc <= 0x3f) {
		|		// GP[0…F]
		|		state->cadr |= 0x10 | (uirc & 0x0f);
		|	} else {
		|		assert(uirc <= 0x3f);
		|	}
		|	val_cond();
		|}
		|
		|void
		|SCM_«mmm» ::
		|val_q4(void)
		|{
		|	bool sclken = (PIN_STS=> && PIN_RMS=> && !PIN_FREZE=>);
		|	bool csa_clk = sclken;
		|	bool uirsclk = !PIN_SFS=>;
		|	bool divide = rand != 0xb;
		|	unsigned uirc = VUIR_C;
		|	if (csa_clk) {
		|		bool xor0c = state->mbit ^ (!state->coh);
		|		bool xor0d = mp_q_bit ^ xor0c;
		|		bool caoi0b = !(
		|			((!divide) && xor0d) ||
		|			(divide && state->coh)
		|		);
		|		mp_nxt_q_bit = caoi0b;
		|	}
		|
		|	if (uirsclk) {
		|		state->csa_hit = mp_csa_hit;
		|		state->csa_write = mp_csa_wr;
		|		state->cwe = !(state->csa_hit || state->csa_write);
		|	}
		|
		|	bool awe = (PIN_RMS && !PIN_FREZE=>);
		|	if (awe && !state->wen) {
		|		state->rfram[state->cadr] = state->c;
		|	}
		|	uint32_t a;
		|	switch (state->msrc >> 2) {
		|	case 0: a = (state->malat >> 48) & 0xffff; break;
		|	case 1: a = (state->malat >> 32) & 0xffff; break;
		|	case 2: a = (state->malat >> 16) & 0xffff; break;
		|	case 3: a = (state->malat >>  0) & 0xffff; break;
		|	}
		|	uint32_t b;
		|	switch (state->msrc & 3) {
		|	case 0: b = (state->mblat >> 48) & 0xffff; break;
		|	case 1: b = (state->mblat >> 32) & 0xffff; break;
		|	case 2: b = (state->mblat >> 16) & 0xffff; break;
		|	case 3: b = (state->mblat >>  0) & 0xffff; break;
		|	}
		|	state->mprod = a * b;
		|	unsigned csmux3 = mp_csa_offs ^ 0xf;
		|
		|	if (sclken) {
		|		if (rand == 0x5) {
		|			uint64_t count2 = 0x40 - flsll(~state->alu);
		|			state->zerocnt = ~count2;
		|		}
		|		if (!mp_load_wdr) {
		|			state->wdr = ~mp_val_bus;
		|		}
		|		if (uirc == 0x28) {
		|			state->count = state->c;
		|	} else if (rand == 0x2 || !divide) {
		|			state->count += 1;
		|		} else if (rand == 0x1) {
		|			state->count += 0x3ff;
		|		}
		|		state->count &= 0x3ff;
		|
		|		bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|		bot_mux_sel = mp_load_bot;
		|		add_mux_sel = mp_load_top;
		|		top_mux_sel = !(add_mux_sel && mp_pop_down);
		|
		|		unsigned csmux0;
		|		if (add_mux_sel)
		|			csmux0 = state->botreg;
		|		else
		|			csmux0 = state->topreg;
		|
		|		unsigned csalu0 = csmux3 + csmux0 + 1;
		|
		|		if (!bot_mux_sel)
		|			state->botreg = csalu0;
		|		if (top_mux_sel)
		|			state->topreg = csalu0;
		|
		|		state->mbit = state->cmsb;
		|	}
		|	if (uirsclk) {
		|		state->csa_offset = csmux3;
		|		state->uir = state->wcsram[mp_nua_bus] ^ 0xffff800000ULL;
		|	}
		|	if (csa_clk)
		|		state->last_cond = thiscond;
		|}
		|
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_H2.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	rand = VUIR_RAND;
		|
		|	if (PIN_H2.negedge()) {
		|		if (mp_fiu_oe == 0x2) {
		|			find_a();
		|			mp_fiu_bus = ~state->a;
		|		}
		|		if (!mp_valv_oe) {
		|			find_b();
		|			mp_val_bus = ~state->b;
		|		}
		|		val_cond();
		|	} else if (PIN_Q2.posedge())
		|		val_q2();
		|	else if (PIN_Q4.posedge())
		|		val_q4();
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("VAL", PartModelDQ("VAL", VAL))
