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

    #autopin = True

    def state(self, file):

        file.fmt('''
		|	uint64_t *val_rfram;
		|	uint64_t val_a, val_b, val_c;
		|	uint64_t val_wdr;
		|	uint64_t val_zerocnt;
		|	uint64_t val_malat, val_mblat, val_mprod, val_msrc;
		|	uint64_t val_nalu, val_alu;
		|	unsigned val_count;
		|	unsigned val_csa_offset;
		|	unsigned val_topreg;
		|	unsigned val_botreg;
		|	bool val_csa_hit;
		|	bool val_csa_write;
		|	unsigned val_cadr;
		|	bool val_amsb, val_bmsb, val_cmsb, val_mbit, val_last_cond;
		|	bool val_isbin, val_sub_else_add, val_ovren, val_carry_middle;
		|	bool val_coh;
		|	bool val_wen;
		|	bool val_cwe;
		|	uint64_t *val_wcsram;
		|	uint64_t val_uir;
		|	unsigned val_rand;
		|	uint8_t val_pa010[512];
		|	uint8_t val_pa011[512];
		|	bool val_thiscond;
		|
		|#define UIR_VAL_A		((state->val_uir >> (39-5)) & 0x3f)
		|#define UIR_VAL_B		((state->val_uir >> (39-11)) & 0x3f)
		|#define UIR_VAL_FRM	((state->val_uir >> (39-16)) & 0x1f)
		|#define UIR_VAL_SEL	((state->val_uir >> (39-18)) & 0x3)
		|#define UIR_VAL_RAND	((state->val_uir >> (39-22)) & 0xf)
		|#define UIR_VAL_C		((state->val_uir >> (39-28)) & 0x3f)
		|#define UIR_VAL_MSRC	((state->val_uir >> (39-32)) & 0xf)
		|#define UIR_VAL_AFNC	((state->val_uir >> (39-37)) & 0x1f)
		|#define UIR_VAL_CSRC	((state->val_uir >> (39-38)) & 0x1)
		|''')


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->val_pa010, sizeof state->val_pa010, "PA010");
		|	load_programmable(this->name(), state->val_pa011, sizeof state->val_pa011, "PA011");
		|	state->val_wcsram = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
		|	state->val_rfram = (uint64_t*)CTX_GetRaw("VAL_RF", sizeof(uint64_t) << 10);
		|	state->val_csa_hit = true;
		|	state->val_csa_write = true;
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|
		|	bool ovrsgn(void);
		|	void val_cond(void);
		|	bool fiu_cond(void);
		|	void val_find_a(void);
		|	void val_find_b(void);
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
		|	bool a0 = state->val_amsb;
		|	bool b0 = state->val_bmsb;
		|	bool se = state->val_isbin;
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
		|		state->val_thiscond = (state->val_nalu != 0);
		|		break;
		|	case 0x01:	// L VAL_ALU_NONZERO
		|		state->val_thiscond = (state->val_nalu == 0);
		|		break;
		|	case 0x02:	// L VAL_ALU_A_LT_OR_LE_B
		|		state->val_thiscond = !(
		|			(state->val_bmsb && (state->val_amsb ^ state->val_bmsb)) ||
		|			(!state->val_coh && (ovrsgn() ^ state->val_sub_else_add))
		|		);
		|		break;
		|	case 0x03:	// SPARE
		|		state->val_thiscond = true;
		|		break;
		|	case 0x04:	// E VAL_LOOP_COUNTER_ZERO
		|		state->val_thiscond = state->val_count != 0x3ff;
		|		break;
		|	case 0x05:	// SPARE
		|		state->val_thiscond = true;
		|		break;
		|	case 0x06:	// L VAL_ALU_NONZERO
		|		state->val_thiscond = (state->val_nalu == 0);
		|		break;
		|	case 0x07:	// L VAL_ALU_32_CO
		|		state->val_thiscond = state->val_carry_middle;
		|		break;
		|	case 0x08:	// L VAL_ALU_CARRY
		|		state->val_thiscond = !state->val_coh;
		|		break;
		|	case 0x09:	// L VAL_ALU_OVERFLOW
		|		state->val_thiscond = state->val_ovren || !(ovrsgn() ^ state->val_sub_else_add ^ (!state->val_coh) ^ state->val_cmsb);
		|		break;
		|	case 0x0a:	// L VAL_ALU_LT_ZERO
		|		state->val_thiscond = state->val_cmsb;
		|		break;
		|	case 0x0b:	// L VAL_ALU_LE_ZERO
		|		state->val_thiscond = !state->val_cmsb || (state->val_nalu == 0);
		|		break;
		|	case 0x0c:	// ML VAL_SIGN_BITS_EQUAL
		|		state->val_thiscond = (state->val_amsb ^ state->val_bmsb);
		|		break;
		|	case 0x0d:	// SPARE
		|		state->val_thiscond = true;
		|		break;
		|	case 0x0e:	// SPARE
		|		state->val_thiscond = true;
		|		break;
		|	case 0x0f:	// E VAL_PREVIOUS
		|		state->val_thiscond = state->val_last_cond;
		|		break;
		|	case 0x10:	// L VAL_ALU_32_ZERO
		|		state->val_thiscond = (state->val_nalu >> 32);
		|		break;
		|	case 0x11:	// L VAL_ALU_40_ZERO
		|		state->val_thiscond = (state->val_nalu >> 16);
		|		break;
		|	case 0x12:	// L VAL_ALU_MIDDLE_ZERO
		|		state->val_thiscond = (state->val_nalu & 0xffff0000ULL);
		|		break;
		|	case 0x13:	// E VAL_Q_BIT
		|		state->val_thiscond = mp_q_bit;
		|		break;
		|	case 0x14:	// SPARE
		|		state->val_thiscond = true;
		|		break;
		|	case 0x15:	// E VAL_M_BIT
		|		state->val_thiscond = state->val_mbit;
		|		break;
		|	case 0x16:	// E VAL_TRUE
		|		state->val_thiscond = false;
		|		break;
		|	case 0x17:	// E VAL_FALSE
		|		state->val_thiscond = true;
		|		break;
		|	default:
		|		break;
		|	}
		|	switch (csel >> 3) {
		|	case 0x0:
		|		mp_condxf = !state->val_thiscond;
		|		break;
		|	case 0x1:
		|		mp_condxe = !state->val_thiscond;
		|		break;
		|	case 0x2:
		|		mp_condxd = !state->val_thiscond;
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
		|		fcond = state->val_nalu == 0;
		|		break;
		|	case 0x01:
		|		fcond = state->val_nalu != 0;
		|		break;
		|	case 0x02:
		|		if (state->val_amsb ^ state->val_bmsb) {
		|			fcond = state->val_bmsb;
		|		} else {
		|			fcond = !state->val_coh;
		|		}
		|		break;
		|	case 0x0f:
		|	case 0x16:		// Undocumented
		|		fcond = state->val_last_cond;
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
		|val_find_a(void)
		|{
		|	unsigned uira = UIR_VAL_A;
		|	if (uira == 0x28) {
		|		state->val_a = state->val_count;
		|		state->val_a |= ~0x3ff;
		|	} else if (uira == 0x29) {
		|		unsigned mdst;
		|		bool prod_16 = state->val_rand != 0xd;
		|		bool prod_32 = state->val_rand != 0xe;
		|		mdst = prod_32 << 1;
		|		mdst |= prod_16;
		|		switch(mdst) {
		|		case 0: state->val_a = 0; break;
		|		case 1: state->val_a = state->val_mprod << 32; break;
		|		case 2: state->val_a = state->val_mprod << 16; break;
		|		case 3: state->val_a = state->val_mprod <<  0; break;
		|		}
		|		state->val_a = ~state->val_a;
		|	} else if (uira == 0x2a) {
		|		state->val_a = state->val_zerocnt;
		|	} else if (uira == 0x2b) {
		|		state->val_a = ~0ULL;
		|	} else {
		|		unsigned aadr = 0;
		|		if (uira == 0x2c) {
		|			aadr = state->val_count;
		|		} else if (uira <= 0x1f) {
		|			aadr = UIR_VAL_FRM << 5;
		|			aadr |= uira & 0x1f;
		|		} else if (uira <= 0x2f) {
		|			aadr |= (uira + state->val_topreg + 1) & 0xf;
		|		} else {
		|			aadr |= uira & 0x1f;
		|		}
		|		state->val_a = state->val_rfram[aadr];
		|	}
		|	state->val_amsb = state->val_a >> 63;
		|}
		|
		|void
		|SCM_«mmm» ::
		|val_find_b(void)
		|{
		|	unsigned uirb = UIR_VAL_B;
		|	bool oe, oe7;
		|	if (uirb != 0x29) {
		|		oe = false;
		|	} else if (!state->val_csa_hit && !mp_valv_oe) { 
		|		oe = false;
		|	} else {
		|		oe = true;
		|	}
		|
		|	oe7 = oe || (state->val_rand == 0x6);
		|
		|	unsigned badr = 0;
		|	if (!oe || !oe7) {
		|		if (uirb == 0x2c) {
		|			badr = state->val_count;
		|		} else if (uirb <= 0x1f) {
		|			badr = UIR_VAL_FRM << 5;
		|			badr |= uirb & 0x1f;
		|		} else if (uirb <= 0x27) {
		|			unsigned btos = (uirb & 0xf) + state->val_topreg + 1;
		|			badr |= btos & 0xf;
		|		} else if (uirb <= 0x2b) {
		|			unsigned csa = state->val_botreg + (uirb&1);
		|			if (!(uirb & 2)) {
		|				csa += state->val_csa_offset;
		|			}
		|			badr |= csa & 0xf;
		|		} else if (uirb <= 0x2f) {
		|			unsigned btos = (uirb & 0xf) + state->val_topreg + 1;
		|			badr |= btos & 0xf;
		|		} else {
		|			badr |= uirb & 0x1f;
		|		}
		|	}
		|	state->val_b = 0;
		|	if (!oe) {
		|		state->val_b |= state->val_rfram[badr] & ~0xffULL;
		|	} else {
		|		state->val_b |= ~mp_val_bus & ~0xffULL;
		|	}
		|	if (!oe7) {
		|		state->val_b |= state->val_rfram[badr] & 0xffULL;
		|	} else {
		|		state->val_b |= ~mp_val_bus & 0xffULL;
		|	}
		|	state->val_bmsb = state->val_b >> 63;
		|}
		| 
		|void
		|SCM_«mmm» ::
		|val_h1(void)
		|{
		|	state->val_rand = UIR_VAL_RAND;
		|	if (mp_fiu_oe == 0x2) {
		|		val_find_a();
		|		mp_fiu_bus = ~state->val_a;
		|	}
		|	if (!mp_valv_oe) {
		|		val_find_b();
		|		mp_val_bus = ~state->val_b;
		|	}
		|	val_cond();
		|}
		| 
		|void
		|SCM_«mmm» ::
		|val_q2(void)
		|{
		|
		|	bool divide = state->val_rand != 0xb;
		|	unsigned uirc = UIR_VAL_C;
		|	if (mp_fiu_oe != 0x02) {
		|		val_find_a();
		|	}
		|	if (mp_valv_oe) {
		|		val_find_b();
		|	}
		|	state->val_wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|	if (state->val_cwe && uirc != 0x28)
		|		state->val_wen = !state->val_wen;
		|
		|	state->val_msrc = UIR_VAL_MSRC;
		|	bool start_mult = state->val_rand != 0xc;
		|	if (!start_mult) {
		|		state->val_malat = ~state->val_a;
		|		state->val_mblat = ~state->val_b;
		|	}
		|
		|	struct f181 f181l, f181h;
		|	unsigned tmp, proma, alur;
		|
		|	tmp = UIR_VAL_RAND;
		|	if (tmp < 8) {
		|		alur = 7;
		|	} else {
		|		alur = 15 - tmp;
		|	}
		|
		|	proma = UIR_VAL_AFNC;
		|	proma |= alur << 5;
		|	if (
		|		!(
		|			(state->val_last_cond && divide) ||
		|			(mp_q_bit && !divide)
		|		)
		|	) {
		|		proma |= 0x100;
		|	}
		|
		|	tmp = state->val_pa011[proma];			// S0-4.LOW
		|	state->val_isbin = (tmp >> 1) & 1;			// IS_BINARY
		|	f181l.ctl = (tmp >> 4) & 0xf;
		|	f181l.ctl |= ((tmp >> 3) & 1) << 4;
		|	f181l.ctl |= 1 << 5;
		|	f181l.ci = (state->val_pa011[proma] >> 2) & 1;	// ALU.C15
		|	f181l.a = state->val_a & 0xffffffff;
		|	f181l.b = state->val_b & 0xffffffff;
		|	f181_alu(&f181l);
		|	state->val_carry_middle = f181l.co;
		|	state->val_nalu = f181l.o;
		|
		|	tmp = state->val_pa010[proma];			// S0-4.HIGH
		|	state->val_ovren = (tmp >> 1) & 1;			// OVR.EN~
		|	state->val_sub_else_add = (tmp >> 2) & 1;			// SUB_ELSE_ADD
		|	f181h.ctl = (tmp >> 4) & 0xf;
		|	f181h.ctl |= ((tmp>>3) & 1) << 4;
		|	f181h.ctl |= 1 << 5;
		|	f181h.ci = f181l.co;
		|	f181h.a = state->val_a >> 32;
		|	f181h.b = state->val_b >> 32;
		|	f181_alu(&f181h);
		|	state->val_coh = f181h.co;
		|	state->val_nalu |= ((uint64_t)f181h.o) << 32;
		|	state->val_alu = ~state->val_nalu;
		|	state->val_cmsb = state->val_alu >> 63;
		|	if (mp_adr_oe & 0x2) {
		|		uint64_t alu = state->val_alu;
		|		// XXX: there is a race here, if TYP gets the space from typ_b only in Q2
		|		if (mp_spc_bus != 4) {
		|			alu |=0xf8000000ULL;
		|		}
		|		mp_adr_bus = ~alu;
		|	}
		|
		|	uint64_t fiu = 0, mux = 0;
		|	bool c_source = UIR_VAL_CSRC;
		|	bool split_c_src = state->val_rand == 0x4;
		|	if (split_c_src || !c_source) {
		|		fiu = ~mp_fiu_bus;
		|	}
		|	if (!c_source && (state->val_rand == 3 || state->val_rand == 6)) {
		|		fiu &= ~1ULL;
		|		fiu |= fiu_cond();
		|	}
		|	if (c_source || split_c_src) {
		|		unsigned sel = UIR_VAL_SEL;
		|		switch (sel) {
		|		case 0x0:
		|			mux = state->val_alu << 1;
		|			mux |= 1;
		|			break;
		|		case 0x1:
		|			mux = state->val_alu >> 16;
		|			mux |= 0xffffULL << 48;
		|			break;
		|		case 0x2:
		|			mux = state->val_alu;
		|			break;
		|		case 0x3:
		|			mux = state->val_wdr;
		|			break;
		|		}
		|	}
		|	if (!split_c_src && !c_source) {
		|		state->val_c = fiu;
		|	} else if (!split_c_src) {
		|		state->val_c = mux;
		|	} else if (c_source) {
		|		state->val_c = fiu & 0xffffffffULL;
		|		state->val_c |= mux & 0xffffffffULL << 32;
		|	} else {
		|		state->val_c = mux & 0xffffffffULL;
		|		state->val_c |= fiu & 0xffffffffULL << 32;
		|	}
		|
		|	state->val_cadr = 0;
		|	if (uirc <= 0x1f) {
		|		// FRAME:REG
		|		state->val_cadr |= uirc & 0x1f;
		|		state->val_cadr |= UIR_VAL_FRM << 5;
		|	} else if (uirc <= 0x27) {
		|		// 0x20 = TOP-1
		|		// …
		|		// 0x27 = TOP-8
		|		state->val_cadr = (state->val_topreg + (uirc & 0x7) + 1) & 0xf;
		|	} else if (uirc == 0x28) {
		|		// 0x28 LOOP COUNTER (RF write disabled)
		|	} else if (uirc == 0x29 && state->val_cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		unsigned sum = state->val_botreg + state->val_csa_offset + 1;
		|		state->val_cadr |= sum & 0xf;
		|	} else if (uirc == 0x29 && !state->val_cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		state->val_cadr |= uirc & 0x1f;
		|		state->val_cadr |= UIR_VAL_FRM << 5;
		|	} else if (uirc <= 0x2b) {
		|		// 0x2a BOT
		|		// 0x2b BOT-1
		|		state->val_cadr |= (state->val_botreg + (uirc & 1)) & 0xf;
		|		state->val_cadr |= (state->val_botreg + (uirc & 1)) & 0xf;
		|	} else if (uirc == 0x2c) {
		|		// 0x28 = LOOP_REG
		|		state->val_cadr = state->val_count;
		|	} else if (uirc == 0x2d) {
		|		// 0x2d SPARE
		|		assert (uirc != 0x2d);
		|	} else if (uirc <= 0x2f) {
		|		// 0x2e = TOP+1
		|		// 0x2f = TOP
		|		state->val_cadr = (state->val_topreg + (uirc & 0x1) + 0xf) & 0xf;
		|	} else if (uirc <= 0x3f) {
		|		// GP[0…F]
		|		state->val_cadr |= 0x10 | (uirc & 0x0f);
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
		|	bool sclken = (mp_clock_stop && mp_ram_stop && !mp_freeze);
		|	bool csa_clk = sclken;
		|	bool uirsclk = !mp_sf_stop;
		|	bool divide = state->val_rand != 0xb;
		|	unsigned uirc = UIR_VAL_C;
		|	if (csa_clk) {
		|		bool xor0c = state->val_mbit ^ (!state->val_coh);
		|		bool xor0d = mp_q_bit ^ xor0c;
		|		bool caoi0b = !(
		|			((!divide) && xor0d) ||
		|			(divide && state->val_coh)
		|		);
		|		mp_nxt_q_bit = caoi0b;
		|	}
		|
		|	if (uirsclk) {
		|		state->val_csa_hit = mp_csa_hit;
		|		state->val_csa_write = mp_csa_wr;
		|		state->val_cwe = !(state->val_csa_hit || state->val_csa_write);
		|	}
		|
		|	bool awe = (mp_ram_stop && !mp_freeze);
		|	if (awe && !state->val_wen) {
		|		state->val_rfram[state->val_cadr] = state->val_c;
		|	}
		|	uint32_t a;
		|	switch (state->val_msrc >> 2) {
		|	case 0: a = (state->val_malat >> 48) & 0xffff; break;
		|	case 1: a = (state->val_malat >> 32) & 0xffff; break;
		|	case 2: a = (state->val_malat >> 16) & 0xffff; break;
		|	case 3: a = (state->val_malat >>  0) & 0xffff; break;
		|	}
		|	uint32_t b;
		|	switch (state->val_msrc & 3) {
		|	case 0: b = (state->val_mblat >> 48) & 0xffff; break;
		|	case 1: b = (state->val_mblat >> 32) & 0xffff; break;
		|	case 2: b = (state->val_mblat >> 16) & 0xffff; break;
		|	case 3: b = (state->val_mblat >>  0) & 0xffff; break;
		|	}
		|	state->val_mprod = a * b;
		|	unsigned csmux3 = mp_csa_offs ^ 0xf;
		|
		|	if (sclken) {
		|		if (state->val_rand == 0x5) {
		|			uint64_t count2 = 0x40 - flsll(~state->val_alu);
		|			state->val_zerocnt = ~count2;
		|		}
		|		if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
		|			state->val_wdr = ~mp_val_bus;
		|		}
		|		if (uirc == 0x28) {
		|			state->val_count = state->val_c;
		|	} else if (state->val_rand == 0x2 || !divide) {
		|			state->val_count += 1;
		|		} else if (state->val_rand == 0x1) {
		|			state->val_count += 0x3ff;
		|		}
		|		state->val_count &= 0x3ff;
		|
		|		bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|		bot_mux_sel = mp_load_bot;
		|		add_mux_sel = mp_load_top;
		|		top_mux_sel = !(add_mux_sel && mp_pop_down);
		|
		|		unsigned csmux0;
		|		if (add_mux_sel)
		|			csmux0 = state->val_botreg;
		|		else
		|			csmux0 = state->val_topreg;
		|
		|		unsigned csalu0 = csmux3 + csmux0 + 1;
		|
		|		if (!bot_mux_sel)
		|			state->val_botreg = csalu0;
		|		if (top_mux_sel)
		|			state->val_topreg = csalu0;
		|
		|		state->val_mbit = state->val_cmsb;
		|	}
		|	if (uirsclk) {
		|		state->val_csa_offset = csmux3;
		|		state->val_uir = state->val_wcsram[mp_nua_bus] ^ 0xffff800000ULL;
		|	}
		|	if (csa_clk)
		|		state->val_last_cond = state->val_thiscond;
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
		|
		|	if (PIN_H2.negedge()) {
		|		val_h1();
		|	} else if (PIN_Q2.posedge())
		|		val_q2();
		|	else if (PIN_Q4.posedge())
		|		val_q4();
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("VAL", PartModelDQ("VAL", VAL))
