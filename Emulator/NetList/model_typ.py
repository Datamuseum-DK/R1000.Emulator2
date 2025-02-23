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
   TYP C-bus mux
   =============

'''

from part import PartModelDQ, PartFactory

class TYP(PartFactory):
    ''' TYP C-bus mux '''

    autopin = True

    def extra(self, file):
        file.fmt('''
		|
		|#define A_LSB BUS64_LSB
		|#define B_LSB BUS64_LSB
		|#define A_BITS(n) (state->typ_a >> A_LSB(n))
		|#define B_BITS(n) (state->typ_b >> B_LSB(n))
		|#define A_BIT(n) (A_BITS(n) & 1)
		|#define B_BIT(n) (B_BITS(n) & 1)
		|#define A_LIT() (state->typ_a & 0x7f)
		|#define B_LIT() (state->typ_b & 0x7f)
		|''')

    def state(self, file):
 
        file.fmt('''
		|	uint64_t *typ_rfram;
		|	uint8_t typ_pa010[512], typ_pa068[512], typ_pa059[512];
		|	uint64_t typ_a, typ_b, c, typ_nalu, typ_alu;
		|	uint64_t typ_wdr;
		|	uint64_t typ_count;
		|	unsigned typ_csa_offset;
		|	unsigned typ_topreg;
		|	unsigned typ_botreg;
		|	bool typ_csa_hit;
		|	bool typ_csa_write;
		|	unsigned typ_aadr;
		|	unsigned typ_badr;
		|	unsigned typ_cadr;
		|	bool typ_cond;
		|	bool typ_almsb;
		|	bool typ_coh;
		|	bool typ_com;
		|	uint32_t typ_ofreg;
		|	bool typ_ppriv;
		|	bool typ_last_cond;
		|	bool typ_wen;
		|	bool typ_is_binary;
		|	bool typ_sub_else_add;
		|	bool typ_ovr_en;
		|	uint64_t *typ_wcsram;
		|	uint64_t typ_uir;
		|
		|#define UIR_TYP_A		((state->typ_uir >> 41) & 0x3f)
		|#define UIR_TYP_B		((state->typ_uir >> 35) & 0x3f)
		|#define UIR_TYP_FRM	((state->typ_uir >> 30) & 0x1f)
		|#define UIR_TYP_RAND	((state->typ_uir >> 24) & 0xf)
		|#define UIR_TYP_C		((state->typ_uir >> 18) & 0x3f)
		|#define UIR_TYP_CLIT	(((state->typ_uir >> (46-16)) & 0x1f) | (((state->typ_uir >> (46-18) & 0x3)<<5)))
		|#define UIR_TYP_UPVC	((state->typ_uir >> 15) & 0x7)
		|#define UIR_TYP_SEL	((state->typ_uir >> 14) & 0x1)
		|#define UIR_TYP_AFNC	((state->typ_uir >> 9) & 0x1f)
		|#define UIR_TYP_CSRC	((state->typ_uir >> 8) & 0x1)
		|#define UIR_TYP_MCTL	((state->typ_uir >> 4) & 0xf)
		|#define UIR_TYP_CCTL	((state->typ_uir >> 1) & 0x7)
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->typ_pa010, sizeof state->typ_pa010, "PA010");
		|	load_programmable(this->name(), state->typ_pa068, sizeof state->typ_pa068, "PA068");
		|	load_programmable(this->name(), state->typ_pa059, sizeof state->typ_pa059, "PA059-01");
		|	state->typ_wcsram = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);
		|	state->typ_rfram = (uint64_t*)CTX_GetRaw("TYP_RF", sizeof(uint64_t) << 10);
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned rand = 0, frm = 0;
		|
		|	bool bin_op_pass(void);
		|	bool priv_path_eq(void);
		|	bool a_op_pass(void);
		|	bool b_op_pass(void);
		|	bool clev(void);
		|	void typ_cond(unsigned condsel, unsigned when);
		|	void cond_a(bool val);
		|	void cond_b(bool val);
		|	void cond_c(bool val);
		|	void cond_d(bool val);
		|	void cond_e(bool val);
		|	void find_a(void);
		|	void find_b(void);
		|	void typ_q2(void);
		|	void typ_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|
		|bool
		|SCM_«mmm» ::
		|bin_op_pass(void)
		|{
		|	bool dp = !(A_BIT(35) && B_BIT(35));
		|	bool abim = !(!(A_BITS(31) == state->typ_ofreg) | dp);
		|	bool bbim = !(!(B_BITS(31) == state->typ_ofreg) | dp);
		|
		|	return (!(
		|		(abim && bbim) ||
		|		(bbim && A_BIT(34)) ||
		|		(abim && B_BIT(34)) ||
		|		(A_BIT(34) && A_BIT(35) && B_BIT(34) && B_BIT(35))
		|	));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|priv_path_eq(void)
		|{
		|	return (!(
		|		(A_BITS(31) == B_BITS(31)) &&
		|		((A_BITS(56) & 0xfffff) == (B_BITS(56) & 0xfffff))
		|	));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|a_op_pass(void)
		|{
		|	return (!(A_BIT(35) && ((A_BITS(31) == state->typ_ofreg) || A_BIT(34))));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|b_op_pass(void)
		|{
		|	return (!(B_BIT(35) && ((B_BITS(31) == state->typ_ofreg) || B_BIT(34))));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|clev(void)
		|{
		|	return (!(
		|		(!(rand != 0x4) && !(A_LIT() != UIR_TYP_CLIT)) ||
		|		(!(rand != 0x6) && !(A_LIT() != B_LIT())) ||
		|		(!(rand != 0x5) && !(B_LIT() != UIR_TYP_CLIT)) ||
		|		(!(rand != 0x7) && !(A_LIT() != B_LIT()) && !(B_LIT() != UIR_TYP_CLIT))
		|	));
		|}
		|
		|void SCM_«mmm» :: cond_a(bool val) { state->typ_cond = val; mp_condxc = !val; };
		|void SCM_«mmm» :: cond_b(bool val) { state->typ_cond = val; mp_condxb = !val; };
		|void SCM_«mmm» :: cond_c(bool val) { state->typ_cond = val; mp_condxa = !val; };
		|void SCM_«mmm» :: cond_d(bool val) { state->typ_cond = val; mp_condx9 = !val; };
		|void SCM_«mmm» :: cond_e(bool val) { state->typ_cond = val; mp_condx8 = !val; };
		|
		|void
		|SCM_«mmm» ::
		|typ_cond(unsigned condsel, unsigned when)
		|{
		|
		|	if ((condsel >> 3) == 0xb)
		|		condsel &= ~0x40;
		|
		|	switch(condsel) {
		|	case 0x18:	// L - TYP_ALU_ZERO
		|		cond_a(state->typ_nalu != 0);
		|		break;
		|	case 0x19:	// L - TYP_ALU_NONZERO
		|		cond_a(state->typ_nalu == 0);
		|		break;
		|	case 0x1a:	// L - TYP_ALU_A_GT_OR_GE_B
		|		{
		|		bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->typ_is_binary) || (!state->typ_is_binary && !A_BIT(0))));
		|		cond_a(!(
		|		    ((A_BIT(0) != B_BIT(0)) && A_BIT(0)) ||
		|		    (state->typ_coh && (ovrsign ^ state->typ_sub_else_add))
		|		));
		|		}
		|		break;
		|	case 0x1b:	// SPARE
		|		cond_a(true);
		|		break;
		|	case 0x1c:	// E - TYP_LOOP_COUNTER_ZERO
		|		cond_a(state->typ_count != 0x3ff);
		|		break;
		|	case 0x1d:	// SPARE
		|		cond_a(true);
		|		break;
		|	case 0x1e:	// L - TYP_ALU_ZERO - COMBO with VAL_ALU_NONZERO
		|		cond_a(state->typ_nalu != 0);
		|		break;
		|	case 0x1f:	// L - TYP_ALU_32_CO - ALU 32 BIT CARRY OUT
		|		cond_a(state->typ_com);
		|		break;
		|	case 0x20:	// L - TYP_ALU_CARRY
		|		cond_b(!state->typ_coh);
		|		break;
		|	case 0x21:	// L - TYP_ALU_OVERFLOW
		|		{
		|		bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->typ_is_binary) || (!state->typ_is_binary && !A_BIT(0))));
		|		cond_b(state->typ_ovr_en || (
		|		    state->typ_coh ^ state->typ_almsb ^ state->typ_sub_else_add ^ ovrsign
		|		));
		|		}
		|		break;
		|	case 0x22:	// L - TYP_ALU_LT_ZERO
		|		cond_b(state->typ_almsb);
		|		break;
		|	case 0x23:	// L - TYP_ALU_LE_ZERO
		|		cond_b(!(state->typ_almsb && (state->typ_nalu != 0)));
		|		break;
		|	case 0x24:	// ML - TYP_SIGN_BITS_EQUAL
		|		cond_b((A_BIT(0) != B_BIT(0)));
		|		break;
		|	case 0x25:	// E - TYP_FALSE
		|		cond_b(true);
		|		break;
		|	case 0x26:	// E - TYP_TRUE
		|		cond_b(false);
		|		break;
		|	case 0x27:	// E - TYP_PREVIOUS
		|		cond_b(state->typ_last_cond);
		|		break;
		|	case 0x28:	// ML - OF_KIND_MATCH
		|		{
		|		unsigned mask_a = state->typ_pa059[UIR_TYP_CLIT] >> 1;
		|		unsigned okpat_a = state->typ_pa059[UIR_TYP_CLIT + 256] >> 1;
		|		bool oka = (0x7f ^ (mask_a & B_LIT())) != okpat_a; // XXX state->typ_b ??
		|
		|		unsigned mask_b = state->typ_pa059[UIR_TYP_CLIT + 128] >> 1;
		|		unsigned okpat_b = state->typ_pa059[UIR_TYP_CLIT + 384] >> 1;
		|		bool okb = (0x7f ^ (mask_b & B_LIT())) != okpat_b;
		|
		|		bool okm = !(oka & okb);
		|		cond_c(okm);
		|		}
		|		break;
		|	case 0x29:	// ML - CLASS_A_EQ_LIT
		|		cond_c(A_LIT() != UIR_TYP_CLIT);
		|		break;
		|	case 0x2a:	// ML - CLASS_B_EQ_LIT
		|		cond_c(B_LIT() != UIR_TYP_CLIT);
		|		break;
		|	case 0x2b:	// ML - CLASS_A_EQ_B
		|		cond_c(A_LIT() != B_LIT());
		|		break;
		|	case 0x2c:	// ML - CLASS_A_B_EQ_LIT
		|		cond_c(!(A_LIT() != UIR_TYP_CLIT) || (B_LIT() != UIR_TYP_CLIT));
		|		break;
		|	case 0x2d:	// E - PRIVACY_A_OP_PASS
		|		cond_c(a_op_pass());
		|		break;
		|	case 0x2e:	// ML - PRIVACY_B_OP_PASS
		|		cond_c(b_op_pass());
		|		break;
		|	case 0x2f:	// ML - PRIVACY_BIN_EQ_PASS
		|		cond_c(priv_path_eq() && bin_op_pass());
		|		break;
		|	case 0x30:	// ML - PRIVACY_BIN_OP_PASS
		|		cond_d(bin_op_pass());
		|		break;
		|	case 0x31:	// ML - PRIVACY_NAMES_EQ
		|		cond_d(A_BITS(31) == B_BITS(31));
		|		break;
		|	case 0x32:	// ML - PRIVACY_PATHS_EQ
		|		cond_d(priv_path_eq());
		|		break;
		|	case 0x33:	// ML - PRIVACY_STRUCTURE
		|		cond_d(!(bin_op_pass() || priv_path_eq()));
		|		break;
		|	case 0x34:	// E - PASS_PRIVACY_BIT
		|		cond_d(state->typ_ppriv);
		|		break;
		|	case 0x35:	// ML - B_BUS_BIT_32
		|		cond_d(B_BIT(32));
		|		break;
		|	case 0x36:	// ML - B_BUS_BIT_33
		|		cond_d(B_BIT(33));
		|		break;
		|	case 0x37:	// ML - B_BUS_BIT_34
		|		cond_d(B_BIT(34));
		|		break;
		|	case 0x38:	// ML - B_BUS_BIT_35
		|		cond_e(B_BIT(35));
		|		break;
		|	case 0x39:	// ML - B_BUS_BIT_36
		|		cond_e(B_BIT(36));
		|		break;
		|	case 0x3a:	// ML - B_BUS_BIT_33_34_OR_36
		|		cond_e((B_BITS(36) & 0xd) != 0xd);
		|		break;
		|	case 0x3b:	// SPARE
		|		cond_e(true);
		|		break;
		|	case 0x3c:	// SPARE
		|		cond_e(true);
		|		break;
		|	case 0x3d:	// SPARE
		|		cond_e(true);
		|		break;
		|	case 0x3e:	// SPARE
		|		cond_e(true);
		|		break;
		|	case 0x3f:	// ML - B_BUS_BIT_21
		|		cond_e(B_BIT(21));
		|		break;
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|find_a(void)
		|{
		|	unsigned uira = UIR_TYP_A;
		|	if (uira == 0x28) {
		|		state->typ_a = ~0ULL << 10;
		|		state->typ_a |= state->typ_count;
		|		return;
		|	}
		|	if ((uira & 0x3c) == 0x28) {
		|		state->typ_a = ~0ULL;
		|		return;
		|	}
		|	state->typ_aadr = 0;
		|	if (uira == 0x2c) {
		|		state->typ_aadr = state->typ_count;
		|	} else if (uira <= 0x1f) {
		|		state->typ_aadr = frm << 5;
		|		state->typ_aadr |= uira & 0x1f;
		|	} else if (uira <= 0x2f) {
		|		state->typ_aadr |= (uira + state->typ_topreg + 1) & 0xf;
		|	} else {
		|		state->typ_aadr |= uira & 0x1f;
		|	}
		|	state->typ_a = state->typ_rfram[state->typ_aadr];
		|}
		|
		|void
		|SCM_«mmm» ::
		|find_b(void)
		|{
		|	unsigned uirb = UIR_TYP_B;
		|
		|	state->typ_badr = 0;
		|	if (uirb == 0x2c) {
		|		state->typ_badr = state->typ_count;
		|	} else if (uirb <= 0x1f) {
		|		state->typ_badr = frm << 5;
		|		state->typ_badr |= uirb & 0x1f;
		|	} else if (uirb <= 0x27) {
		|		state->typ_badr |= (uirb + state->typ_topreg + 1) & 0xf;
		|	} else if (uirb <= 0x2b) {
		|		unsigned csa = state->typ_botreg + (uirb&1);
		|		if (!(uirb & 2)) {
		|			csa += state->typ_csa_offset;
		|		}
		|		state->typ_badr |= csa & 0xf;
		|	} else if (uirb <= 0x2f) {
		|		state->typ_badr |= (uirb + state->typ_topreg + 1) & 0xf;
		|	} else {
		|		state->typ_badr |= uirb & 0x1f;
		|	}
		|	if (uirb == 0x29 && mp_typt_oe) {
		|		state->typ_b = ~mp_typ_bus;
		|	} else {
		|		state->typ_b = state->typ_rfram[state->typ_badr];
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|typ_q2(void)
		|{
		|	unsigned uirc = UIR_TYP_C;
		|
		|	unsigned priv_check = UIR_TYP_UPVC;
		|	if (mp_fiu_oe != 0x4) {
		|		find_a();
		|	}
		|	if (mp_typt_oe) {
		|		find_b();
		|	}
		|	state->typ_wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|	if (mp_csa_write_enable && uirc != 0x28)
		|	state->typ_wen = !state->typ_wen;
		|
		|	bool divide = rand != 0xb;
		|	bool acond = true;
		|	if (divide && state->typ_last_cond)
		|		acond = false;
		|	if (!divide && mp_q_bit) 
		|		acond = false;
		|	struct f181 f181l, f181h;
		|	unsigned tmp, idx, alurand, alufunc = UIR_TYP_AFNC;
		|
		|	if (rand < 8) {
		|		alurand = 7;
		|	} else {
		|		alurand = 15 - rand;
		|	}
		|	idx = acond << 8;
		|	idx |= alurand << 5;
		|	idx |= alufunc;
		|		
		|	tmp = state->typ_pa068[idx];
		|	state->typ_is_binary = (tmp >> 1) & 1;
		|	tmp >>= 3;
		|
		|	f181l.ctl = tmp >> 1;
		|	f181l.ctl |= (tmp & 1) << 4;
		|	f181l.ctl |= (rand != 0xf) << 5;
		|	f181l.ci = (state->typ_pa068[idx] >> 2) & 1;
		|	f181l.a = state->typ_a & 0xffffffff;
		|	f181l.b = state->typ_b & 0xffffffff;
		|	f181_alu(&f181l);
		|	state->typ_com = f181l.co;
		|	state->typ_nalu = f181l.o;
		|
		|	tmp = state->typ_pa010[idx];
		|	state->typ_sub_else_add = (tmp >> 2) & 1;
		|	state->typ_ovr_en = (tmp >> 1) & 1;
		|	tmp >>= 3;
		|
		|	f181h.ctl = tmp >> 1;
		|	f181h.ctl |= (tmp & 1) << 4;
		|	f181h.ctl |= 1 << 5;
		|	f181h.ci = f181l.co;
		|	f181h.a = state->typ_a >> 32;
		|	f181h.b = state->typ_b >> 32;
		|	f181_alu(&f181h);
		|	state->typ_coh = f181h.co;
		|	state->typ_nalu |= ((uint64_t)f181h.o) << 32;
		|	state->typ_alu = ~state->typ_nalu;
		|	state->typ_almsb = state->typ_alu >> 63ULL;
		|
		|	if (mp_adr_oe & 0x4) {
		|		uint64_t alu = state->typ_alu;
		|		unsigned spc = mp_spc_bus;
		|		if (spc != 4) {
		|			alu |=0xf8000000ULL;
		|		}
		|		mp_adr_bus = ~alu;
		|	}
		|
		|	state->typ_cadr = 0;
		|	if (uirc <= 0x1f) {
		|		// FRAME:REG
		|		state->typ_cadr |= uirc & 0x1f;
		|		state->typ_cadr |= frm << 5;
		|	} else if (uirc <= 0x27) {
		|		// 0x20 = TOP-1
		|		// …
		|		// 0x27 = TOP-8
		|		state->typ_cadr = (state->typ_topreg + (uirc & 0x7) + 1) & 0xf;
		|	} else if (uirc == 0x28) {
		|		// 0x28 LOOP COUNTER (RF write disabled)
		|	} else if (uirc == 0x29 && mp_csa_write_enable) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		unsigned sum = state->typ_botreg + state->typ_csa_offset + 1;
		|		state->typ_cadr |= sum & 0xf;
		|	} else if (uirc == 0x29 && !mp_csa_write_enable) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		state->typ_cadr |= uirc & 0x1f;
		|		state->typ_cadr |= frm << 5;
		|	} else if (uirc <= 0x2b) {
		|		// 0x2a BOT
		|		// 0x2b BOT-1
		|		state->typ_cadr |= (state->typ_botreg + (uirc & 1)) & 0xf;
		|		state->typ_cadr |= (state->typ_botreg + (uirc & 1)) & 0xf;
		|	} else if (uirc == 0x2c) {
		|		// 0x28 = LOOP_REG
		|		state->typ_cadr = state->typ_count;
		|	} else if (uirc == 0x2d) {
		|		// 0x2d SPARE
		|		assert (uirc != 0x2d);
		|	} else if (uirc <= 0x2f) {
		|		// 0x2e = TOP+1
		|		// 0x2f = TOP
		|		state->typ_cadr = (state->typ_topreg + (uirc & 0x1) + 0xf) & 0xf;
		|	} else if (uirc <= 0x3f) {
		|		// GP[0…F]
		|		state->typ_cadr |= 0x10 | (uirc & 0x0f);
		|	} else {
		|		assert(uirc <= 0x3f);
		|	}
		|
		|	bool micros_en = mp_uevent_enable;
		|	mp_clock_stop_3 = true;
		|	mp_clock_stop_4 = true;
		|	unsigned selcond = 0x00;
		|	if (state->typ_ppriv) {
		|		selcond = 0x80 >> priv_check;
		|	}
		|#define TYP_UEV (UEV_CLASS|UEV_BIN_EQ|UEV_BIN_OP|UEV_TOS_OP|UEV_TOS1_OP|UEV_CHK_SYS)
		|	mp_seq_uev &= ~TYP_UEV;
		|	if (micros_en) {
		|		if (selcond == 0x40 && bin_op_pass())
		|			mp_seq_uev |= UEV_BIN_OP;
		|		if (selcond == 0x80 && priv_path_eq() && bin_op_pass())
		|			mp_seq_uev |= UEV_BIN_EQ;
		|		if ((0x3 < rand && rand < 0x8) && clev())
		|			mp_seq_uev |= UEV_CLASS;
		|		if ((selcond == 0x10 && a_op_pass()) || (selcond == 0x04 && b_op_pass()))
		|			mp_seq_uev |= UEV_TOS1_OP;
		|		if ((selcond == 0x20 && a_op_pass()) || (selcond == 0x08 && b_op_pass()))
		|			mp_seq_uev |= UEV_TOS_OP;
		|		if ((!((rand != 0xe) || !(B_LIT() != UIR_TYP_CLIT))))
		|			mp_seq_uev |= UEV_CHK_SYS;
		|
		|		if ((!((rand != 0xe) || !(B_LIT() != UIR_TYP_CLIT)))) {
		|			mp_clock_stop_3 = false;
		|		}
		|
		|		if ((0x3 < rand && rand < 0x8) && clev()) {
		|			mp_clock_stop_3 = false;
		|		}
		|
		|		if (priv_path_eq() && bin_op_pass() && selcond == 0x80) {
		|			mp_clock_stop_3 = false;
		|		}
		|	}
		|
		|	if (selcond == 0x40 && bin_op_pass()) {
		|		mp_clock_stop_4 = false;
		|	}
		|
		|	if ((selcond & 0x30) && a_op_pass()) {
		|		mp_clock_stop_4 = false;
		|	}
		|
		|	if ((selcond & 0x0c) && b_op_pass()) {
		|		mp_clock_stop_4 = false;
		|	}
		|	typ_cond(mp_cond_sel, 0);
		|}
		|
		|void
		|SCM_«mmm» ::
		|typ_q4(void)
		|{
		|	uint64_t c = 0;
		|	bool chi = false;
		|	bool clo = false;
		|	bool uirsclk = !mp_sf_stop;
		|	bool sclke = (mp_clock_stop && mp_ram_stop && !mp_freeze);
		|	unsigned priv_check = UIR_TYP_UPVC;
		|	unsigned uirc = UIR_TYP_C;
		|
		|	if (uirsclk) {
		|		state->typ_csa_hit = mp_csa_hit;
		|		state->typ_csa_write = mp_csa_wr;
		|		mp_csa_write_enable = !(state->typ_csa_hit || state->typ_csa_write);
		|	}
		|
		|	bool c_source = UIR_TYP_CSRC;
		|	uint64_t fiu = 0;
		|	bool fiu0, fiu1;
		|	fiu0 = c_source;
		|	fiu1 = c_source == (rand != 0x3);
		|
		|	bool sel = UIR_TYP_SEL;
		|
		|	if (!fiu0 || !fiu1) {
		|		fiu = ~mp_fiu_bus;
		|	}
		|	if (!fiu0) {
		|		c |= fiu & 0xffffffff00000000ULL;
		|		chi = true;
		|	} else {
		|		if (sel) {
		|			c |= state->typ_wdr & 0xffffffff00000000ULL;
		|		} else {
		|			c |= state->typ_alu & 0xffffffff00000000ULL;
		|		}
		|		chi = true;
		|	}
		|	if (!fiu1) {
		|		c |= fiu & 0xffffffffULL;
		|		clo = true;
		|	} else {
		|		if (sel) {
		|			c |= state->typ_wdr & 0xffffffffULL;
		|		} else {
		|			c |= state->typ_alu & 0xffffffffULL;
		|		}
		|		clo = true;
		|	}
		|	if (chi && !clo)
		|		c |= 0xffffffff;
		|	if (!chi && clo)
		|		c |= 0xffffffffULL << 32;
		|
		|	bool awe = (!(mp_freeze) && mp_ram_stop);
		|	if (awe && !state->typ_wen) {
		|		state->typ_rfram[state->typ_cadr] = c;
		|	}
		|	unsigned csmux3 = mp_csa_offs ^ 0xf;
		|	if (uirsclk) {
		|		state->typ_csa_offset = csmux3;
		|	}
		|	if (sclke) {
		|		if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
		|			state->typ_wdr = ~mp_typ_bus;
		|		}
		|		if (uirc == 0x28) {
		|			state->typ_count = c;
		|		} else if (rand == 0x2) {
		|			state->typ_count += 1;
		|		} else if (rand == 0x1) {
		|			state->typ_count += 0x3ff;
		|		}
		|		state->typ_count &= 0x3ff;
		|
		|		unsigned csmux0;
		|		if (mp_load_top)
		|			csmux0 = state->typ_botreg;
		|		else
		|			csmux0 = state->typ_topreg;
		|
		|		unsigned csalu0 = csmux3 + csmux0 + 1;
		|	
		|		if (!mp_load_bot)
		|			state->typ_botreg = csalu0;
		|		if (!(mp_load_top && mp_pop_down))
		|			state->typ_topreg = csalu0;
		|		state->typ_last_cond = state->typ_cond;
		|		if (rand == 0xc) {
		|			state->typ_ofreg = state->typ_b >> 32;
		|		}
		|
		|		if (priv_check != 7) {
		|			bool set_pass_priv = rand != 0xd;
		|			state->typ_ppriv = set_pass_priv;
		|		}
		|	}
		|	if (uirsclk) {
		|		state->typ_uir = state->typ_wcsram[mp_nua_bus] ^ 0x7fffc0000000ULL;
		|		mp_nxt_mar_cntl = UIR_TYP_MCTL;
		|		mp_nxt_csa_cntl = UIR_TYP_CCTL;
		|	}
		|}
		|''')

    def sensitive(self):
        yield "PIN_H2.neg()"
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	rand = UIR_TYP_RAND;
		|	frm = UIR_TYP_FRM;
		|
		|	unsigned marctl = UIR_TYP_MCTL;
		|
		|	if (PIN_H2.negedge()) {
		|		if (mp_fiu_oe == 0x4) {
		|			find_a();
		|			mp_fiu_bus = ~state->typ_a;
		|		}
		|		if (!mp_typt_oe) {
		|			find_b();
		|			mp_typ_bus = ~state->typ_b;
		|		}
		|		typ_cond(mp_cond_sel, 0);
		|		if (mp_adr_oe & 0x6) {
		|			if (marctl & 0x8) {
		|				mp_spc_bus = (marctl & 0x7) ^ 0x7;
		|			} else {
		|				find_b();
		|				mp_spc_bus = (state->typ_b & 0x7) ^ 0x7;
		|			}
		|		}
		|	} else if (PIN_Q2.posedge()) {
		|		typ_q2();
		|		if ((mp_adr_oe & 0x6) && marctl < 0x8) {	// XXX: && ?
		|			mp_spc_bus = (state->typ_b & 0x7) ^ 0x7;
		|			// XXX: when 4, possible race against address bus truncation in TYP or VAL
		|		}
		|	} else if (PIN_Q4.posedge()) {
		|		typ_q4();
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("TYP", PartModelDQ("TYP", TYP))
