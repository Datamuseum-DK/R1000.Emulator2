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
		|#define A_LSB BUS_DT_LSB
		|#define B_LSB BUS_DT_LSB
		|#define A_BITS(n) (state->a >> A_LSB(n))
		|#define B_BITS(n) (state->b >> B_LSB(n))
		|#define A_BIT(n) (A_BITS(n) & 1)
		|#define B_BIT(n) (B_BITS(n) & 1)
		|#define A_LIT() (state->a & 0x7f)
		|#define B_LIT() (state->b & 0x7f)
		|''')

    def state(self, file):
 
        file.fmt('''
		|	uint64_t rfram[1<<10];
		|	uint8_t pa010[512], pa068[512], pa059[512];
		|	uint64_t a, b, c, alu;
		|	uint64_t wdr;
		|	unsigned count;
		|	unsigned csa_offset;
		|	unsigned topreg;
		|	unsigned botreg;
		|	bool csa_hit;
		|	bool csa_write;
		|	unsigned aadr;
		|	unsigned badr;
		|	unsigned cadr;
		|	bool cond;
		|	bool almsb;
		|	bool coh;
		|	bool com;
		|	uint8_t zero;
		|	uint32_t ofreg;
		|	bool ppriv;
		|	bool last_cond;
		|	bool wen;
		|	bool is_binary;
		|	bool sub_else_add;
		|	bool ovr_en;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pa010, sizeof state->pa010,
		|	    "PA010");
		|	load_programmable(this->name(),
		|	    state->pa068, sizeof state->pa068,
		|	    "PA068");
		|	load_programmable(this->name(),
		|	    state->pa059, sizeof state->pa059,
		|	    "PA059-01");
		|''')

    def sensitive(self):
            #yield "PIN_CCLK"		# q4pos,prev
            #yield "BUS_MCTL"		# uir q4pos,prev
            #yield "PIN_OFC.pos()"	# prev
            #yield "PIN_QFOE"		# prev
            #yield "PIN_QSPOE"		# SPDR,prev
            #yield "PIN_QTOE"		# prev
            #yield "PIN_SCLKE"		# q4pos,prev
            #yield "PIN_TQBIT"		# q2pos,prev
            #yield "PIN_UCLK"		# q4pos,prev
            #yield "PIN_VAEN"		# prev

            #yield "PIN_ALOOP"		# uir q1pos
            #yield "PIN_BLOOP"		# uir q1pos
            #yield "BUS_UIRA"		# uir
            #yield "BUS_UIRB"		# uir
            #yield "BUS_UIRC"		# uir
            #yield "BUS_FRM"		# uir q1pos & q3pos
            #yield "BUS_RAND"		# uir
            #yield "BUS_CLIT"		# uir
            #yield "BUS_AFNC"		# uir q2pos
            #yield "PIN_CSRC"		# uir WEpos
            #yield "PIN_SEL"		# uir WEpos
            #yield "BUS_UPVC"		# uir

            #yield "PIN_ADROE"		# h1?
            #yield "PIN_CSAH"		# UCLK
            #yield "BUS_CSAO"		# UCLK, CCLK
            #yield "PIN_CSAW"		# UCLK
            #yield "BUS_DF"		# WEpos
            #yield "PIN_LBOT"		# CCLK
            #yield "PIN_LDWDR"		# q4pos
            #yield "PIN_LPOP"		# CCLK
            #yield "PIN_LTOP"		# CCLK

            # yield "BUS_CSEL"		# uir? h1
            # yield "BUS_DT"		# q2pos, q4pos

            yield "BUS_DSP"		# q2pos
            yield "PIN_H2.neg()"
            yield "PIN_Q2"
            yield "PIN_Q4"
            yield "PIN_UEN"
            #yield "PIN_WE.pos()"	# q4?

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned clit(void);
		|	bool bin_op_pass(void);
		|	bool priv_path_eq(void);
		|	bool a_op_pass(void);
		|	bool b_op_pass(void);
		|	bool clev(unsigned);
		|	void typ_cond(unsigned condsel, unsigned when);
		|	void cond_a(bool val);
		|	void cond_b(bool val);
		|	void cond_c(bool val);
		|	void cond_d(bool val);
		|	void cond_e(bool val);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|unsigned
		|SCM_«mmm» ::
		|clit(void)
		|{
		|	unsigned tmp;
		|	BUS_CLIT_READ(tmp);
		|	return (tmp);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|bin_op_pass(void)
		|{
		|	bool dp = !(A_BIT(35) && B_BIT(35));
		|	bool abim = !(!(A_BITS(31) == state->ofreg) | dp);
		|	bool bbim = !(!(B_BITS(31) == state->ofreg) | dp);
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
		|	return (!(A_BIT(35) && ((A_BITS(31) == state->ofreg) || A_BIT(34))));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|b_op_pass(void)
		|{
		|	return (!(B_BIT(35) && ((B_BITS(31) == state->ofreg) || B_BIT(34))));
		|}
		|
		|bool
		|SCM_«mmm» ::
		|clev(unsigned rand)
		|{
		|	return (!(
		|		(!(rand != 0x4) && !(A_LIT() != clit())) ||
		|		(!(rand != 0x6) && !(A_LIT() != B_LIT())) ||
		|		(!(rand != 0x5) && !(B_LIT() != clit())) ||
		|		(!(rand != 0x7) && !(A_LIT() != B_LIT()) && !(B_LIT() != clit()))
		|	));
		|}
		|
		|void SCM_«mmm» :: cond_a(bool val) { state->cond = val; output.conda = !val; };
		|void SCM_«mmm» :: cond_b(bool val) { state->cond = val; output.condb = !val; };
		|void SCM_«mmm» :: cond_c(bool val) { state->cond = val; output.condc = !val; };
		|void SCM_«mmm» :: cond_d(bool val) { state->cond = val; output.condd = !val; };
		|void SCM_«mmm» :: cond_e(bool val) { state->cond = val; output.conde = !val; };
		|
		|void
		|SCM_«mmm» ::
		|typ_cond(unsigned condsel, unsigned when)
		|{
		|
		|#if 1
		|	if ((condsel >> 3) == 0xb)
		|		condsel &= ~0x40;
		|#endif
		|	switch(condsel) {
		|#if 1
		|	case 0x18:	// L - TYP_ALU_ZERO
		|		cond_a(state->zero != 0xff);
		|		break;
		|	case 0x19:	// L - TYP_ALU_NONZERO
		|		cond_a(state->zero == 0xff);
		|		break;
		|	case 0x1a:	// L - TYP_ALU_A_GT_OR_GE_B
		|		{
		|		bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->is_binary) || (!state->is_binary && !A_BIT(0))));
		|		cond_a(!(
		|		    ((A_BIT(0) != B_BIT(0)) && A_BIT(0)) ||
		|		    (state->coh && (ovrsign ^ state->sub_else_add))
		|		));
		|		}
		|		break;
		|	case 0x1b:	// SPARE
		|		cond_a(true);
		|		break;
		|	case 0x1c:	// E - TYP_LOOP_COUNTER_ZERO
		|		cond_a(state->count != 0x3ff);
		|		break;
		|	case 0x1d:	// SPARE
		|		cond_a(true);
		|		break;
		|	case 0x1e:	// L - TYP_ALU_ZERO - COMBO with VAL_ALU_NONZERO
		|		cond_a(state->zero != 0xff);
		|		break;
		|	case 0x1f:	// L - TYP_ALU_32_CO - ALU 32 BIT CARRY OUT
		|		cond_a(state->com);
		|		break;
		|	case 0x20:	// L - TYP_ALU_CARRY
		|		cond_b(!state->coh);
		|		break;
		|	case 0x21:	// L - TYP_ALU_OVERFLOW
		|		{
		|		bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->is_binary) || (!state->is_binary && !A_BIT(0))));
		|		cond_b(state->ovr_en || (
		|		    state->coh ^ state->almsb ^ state->sub_else_add ^ ovrsign
		|		));
		|		}
		|		break;
		|	case 0x22:	// L - TYP_ALU_LT_ZERO
		|		cond_b(state->almsb);
		|		break;
		|	case 0x23:	// L - TYP_ALU_LE_ZERO
		|		cond_b(!(state->almsb && (state->zero != 0xff)));
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
		|		cond_b(state->last_cond);
		|		break;
		|#endif
		|	case 0x28:	// ML - OF_KIND_MATCH
		|		{
		|		unsigned mask_a = state->pa059[clit()] >> 1;
		|		unsigned okpat_a = state->pa059[clit() + 256] >> 1;
		|		bool oka = (0x7f ^ (mask_a & B_LIT())) != okpat_a; // XXX state->b ??
		|
		|		unsigned mask_b = state->pa059[clit() + 128] >> 1;
		|		unsigned okpat_b = state->pa059[clit() + 384] >> 1;
		|		bool okb = (0x7f ^ (mask_b & B_LIT())) != okpat_b;
		|
		|		bool okm = !(oka & okb);
		|		cond_c(okm);
		|		}
		|		break;
		|	case 0x29:	// ML - CLASS_A_EQ_LIT
		|		cond_c(A_LIT() != clit());
		|		break;
		|	case 0x2a:	// ML - CLASS_B_EQ_LIT
		|		cond_c(B_LIT() != clit());
		|		break;
		|	case 0x2b:	// ML - CLASS_A_EQ_B
		|		cond_c(A_LIT() != B_LIT());
		|		break;
		|	case 0x2c:	// ML - CLASS_A_B_EQ_LIT
		|		cond_c(!(A_LIT() != clit()) || (B_LIT() != clit()));
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
		|		cond_d(state->ppriv);
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
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t c = 0;
		|	uint64_t fiu = 0;
		|	bool fiu_valid = false;
		|	bool fiu0, fiu1;
		|	bool chi = false;
		|	bool clo = false;
		|	bool h2 = PIN_H2=>;
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|
		|	bool uirsclk = PIN_UCLK.posedge();
		|	bool sclke = !PIN_SCLKE=>;
		|
		|	unsigned uira, uirb, uirc, rand, condsel;
		|	BUS_UIRA_READ(uira);
		|	BUS_UIRB_READ(uirb);
		|	BUS_UIRC_READ(uirc);
		|	BUS_RAND_READ(rand);
		|	BUS_CSEL_READ(condsel);
		|
		|	unsigned condmask = 0;
		|
		|#define COND(g, c) (((g) << 3)| (c))
		|	// Early conditions
		|	assert (state->count <= 0x3ff);
		|	switch (condsel) {
		|	case COND(0x3, 4): // E - TYPE_COUNTER_ZERO	 
		|	case COND(0xb, 4): // E - TYPE_COUNTER_ZERO	 
		|		condmask = 0x10;
		|		typ_cond(condsel, 0);
		|		break;
		|	case COND(0x4, 5): // E - TYP_FALSE
		|	case COND(0x4, 6): // E - TYP_TRUE
		|	case COND(0x4, 7): // E - TYP_PREVIOUS
		|		condmask = 0x08;
		|		typ_cond(condsel, 0);
		|		break;
		|	case COND(0x6, 4): // E - PASS_PRIVACY_BIT
		|		condmask = 0x02;
		|		typ_cond(condsel, 0);
		|		break;
		|	}
		|
		|	unsigned condgrp = condsel >> 3;
		|	if (condgrp == 0xb)
		|		condgrp = 0x3;
		|
		|	unsigned csmux3;
		|	BUS_CSAO_READ(csmux3);
		|	csmux3 ^= BUS_CSAO_MASK;
		|
		|	unsigned atos = (uira & 0xf) + state->topreg + 1;
		|	unsigned btos = (uirb & 0xf) + state->topreg + 1;
		|
		|	unsigned csa = state->botreg + (uirb&1);
		|	if (!(uirb & 2)) {
		|		csa += state->csa_offset;
		|	}
		|
		|	if (uirsclk) {
		|		state->csa_hit = PIN_CSAH=>;
		|		state->csa_write = PIN_CSAW=>;
		|		output.cwe = !(state->csa_hit || state->csa_write);
		|	}
		|
		|	unsigned frm;
		|	BUS_FRM_READ(frm);
		|	if (q2pos) {
		|		state->wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|		if (output.cwe && uirc != 0x28)
		|		state->wen = !state->wen;
		|	}
		|
		|	if (q1pos) {
		|		state->aadr = 0;
		|		if (PIN_ALOOP=>) {
		|			state->aadr = state->count;
		|		} else if (uira <= 0x1f) {
		|			state->aadr = frm << 5;
		|			state->aadr |= uira & 0x1f;
		|		} else if (uira <= 0x2f) {
		|			state->aadr |= atos & 0xf;
		|		} else {
		|			state->aadr |= uira & 0x1f;
		|		}
		|
		|		state->badr = 0;
		|		if (PIN_BLOOP=>) {
		|			state->badr = state->count;
		|		} else if (uirb <= 0x1f) {
		|			state->badr = frm << 5;
		|			state->badr |= uirb & 0x1f;
		|		} else if (uirb <= 0x27) {
		|			state->badr |= btos & 0xf;
		|		} else if (uirb <= 0x2b) {
		|			state->badr |= csa & 0xf;
		|		} else if (uirb <= 0x2f) {
		|			state->badr |= btos & 0xf;
		|		} else {
		|			state->badr |= uirb & 0x1f;
		|		}
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|
		|	if (!h2) {
		|		if ((uira & 0x3c) != 0x28) {
		|			state->a = state->rfram[state->aadr];
		|		} else if (uira == 0x28) {
		|			state->a = BUS_QF_MASK;
		|			state->a ^= 0x3ff;
		|			state->a |= state->count;
		|		} else {
		|			state->a = BUS_QF_MASK;
		|		}
		|		if (!output.z_qf) {
		|			output.qf = state->a ^ BUS_QF_MASK;
		|		}
		|	}
		|
		|	if (q3pos) {
		|		state->cadr = 0;
		|		if (uirc <= 0x1f) {
		|			// FRAME:REG
		|			state->cadr |= uirc & 0x1f;
		|			state->cadr |= frm << 5;
		|		} else if (uirc <= 0x27) {
		|			// 0x20 = TOP-1
		|			// …
		|			// 0x27 = TOP-8
		|			state->cadr = (state->topreg + (uirc & 0x7) + 1) & 0xf;
		|		} else if (uirc == 0x28) {
		|			// 0x28 LOOP COUNTER (RF write disabled)
		|		} else if (uirc == 0x29 && output.cwe) {
		|			// 0x29 DEFAULT (RF write disabled)
		|			unsigned sum = state->botreg + state->csa_offset + 1;
		|			state->cadr |= sum & 0xf;
		|		} else if (uirc == 0x29 && !output.cwe) {
		|			// 0x29 DEFAULT (RF write disabled)
		|			state->cadr |= uirc & 0x1f;
		|			state->cadr |= frm << 5;
		|		} else if (uirc <= 0x2b) {
		|			// 0x2a BOT
		|			// 0x2b BOT-1
		|			state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|			state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|		} else if (uirc == 0x2c) {
		|			// 0x28 = LOOP_REG
		|			state->cadr = state->count;
		|		} else if (uirc == 0x2d) {
		|			// 0x2d SPARE
		|			assert (uirc != 0x2d);
		|		} else if (uirc <= 0x2f) {
		|			// 0x2e = TOP+1
		|			// 0x2f = TOP
		|			state->cadr = (state->topreg + (uirc & 0x1) + 0xf) & 0xf;
		|		} else if (uirc <= 0x3f) {
		|			// GP[0…F]
		|			state->cadr |= 0x10 | (uirc & 0x0f);
		|		} else {
		|			assert(uirc <= 0x3f);
		|		}
		|	}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!h2) {
		|		if (uirb == 0x29 && output.z_qt) {
		|			BUS_DT_READ(state->b);
		|			state->b ^= BUS_DT_MASK;
		|		} else {
		|			state->b = state->rfram[state->badr];
		|		}
		|	}
		|	if (q2pos) {
		|		output.ocken = rand != 0xc;
		|
		|		bool divide = rand != 0xb;
		|		bool acond = true;
		|		if (divide && state->last_cond)
		|			acond = false;
		|		if (!divide && PIN_TQBIT=>)
		|			acond = false;
		|		struct f181 f181l, f181h;
		|		unsigned tmp, idx, alurand, alufunc;
		|		BUS_AFNC_READ(alufunc);
		|
		|		if (rand < 8) {
		|			alurand = 7;
		|		} else {
		|			alurand = 15 - rand;
		|		}
		|		idx = acond << 8;
		|		idx |= alurand << 5;
		|		idx |= alufunc;
		|		
		|		tmp = state->pa068[idx];
		|		state->is_binary = (tmp >> 1) & 1;
		|		tmp >>= 3;
		|
		|		f181l.ctl = tmp >> 1;
		|		f181l.ctl |= (tmp & 1) << 4;
		|		f181l.ctl |= (rand != 0xf) << 5;
		|		f181l.ci = (state->pa068[idx] >> 2) & 1;
		|		f181l.a = state->a & 0xffffffff;
		|		f181l.b = state->b & 0xffffffff;
		|		f181_alu(&f181l);
		|		state->com = f181l.co;
		|		state->alu = f181l.o;
		|
		|		tmp = state->pa010[idx];
		|		state->sub_else_add = (tmp >> 2) & 1;
		|		state->ovr_en = (tmp >> 1) & 1;
		|		tmp >>= 3;
		|
		|		f181h.ctl = tmp >> 1;
		|		f181h.ctl |= (tmp & 1) << 4;
		|		f181h.ctl |= 1 << 5;
		|		f181h.ci = f181l.co;
		|		f181h.a = state->a >> 32;
		|		f181h.b = state->b >> 32;
		|		f181_alu(&f181h);
		|		state->coh = f181h.co;
		|		state->alu |= ((uint64_t)f181h.o) << 32;
		|		state->zero = 0;
		|		if (!(state->alu & (0xffULL) <<  0)) state->zero |= 0x01;
		|		if (!(state->alu & (0xffULL) <<  8)) state->zero |= 0x02;
		|		if (!(state->alu & (0xffULL) << 16)) state->zero |= 0x04;
		|		if (!(state->alu & (0xffULL) << 24)) state->zero |= 0x08;
		|		if (!(state->alu & (0xffULL) << 32)) state->zero |= 0x10;
		|		if (!(state->alu & (0xffULL) << 40)) state->zero |= 0x20;
		|		if (!(state->alu & (0xffULL) << 48)) state->zero |= 0x40;
		|		if (!(state->alu & (0xffULL) << 56)) state->zero |= 0x80;
		|		state->alu = ~state->alu;
		|		state->almsb = state->alu >> 63ULL;
		|
		|		output.z_adr = PIN_ADROE=>;
		|		if (!output.z_adr) {
		|			unsigned spc;
		|			BUS_DSP_READ(spc);
		|			uint64_t alu = state->alu;
		|
		|			if (spc != 4) {
		|				alu |=0xf8000000ULL;
		|			}
		|
		|			output.adr = alu ^ BUS_ADR_MASK;
		|		}
		|
		|		if (condgrp == 3) {
		|			condmask = 0x10;
		|			typ_cond(condsel, 2);
		|#if 0	
		|			bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->is_binary) || (!state->is_binary && !A_BIT(0))));
		|			switch (condsel & 0x7) {
		|			case 0:	// L - TYP_ALU_ZERO
		|			case 6: // L - TYP_ALU_ZERO - COMBO with VAL_ALU_NONZERO
		|				state->cond = state->zero != 0xff;
		|				break;
		|			case 1:	// L - TYP_ALU_NONZERO
		|				state->cond = state->zero == 0xff;
		|				break;
		|			case 2:	// L - TYP_ALU_A_GT_OR_GE_B
		|				state->cond = !(
		|				    ((A_BIT(0) != B_BIT(0)) && A_BIT(0)) ||
		|				    (state->coh && (ovrsign ^ state->sub_else_add))
		|				);
		|				break;
		|			case 4: // E - TYP_LOOP_COUNTER_ZERO
		|				state->cond = state->count != 0x3ff;
		|				break;
		|			case 7: // L - TYP_ALU_32_CO - ALU 32 BIT CARRY OUT
		|				state->cond = state->com;
		|				break;
		|			default:
		|				state->cond = true;
		|				break;
		|			}
		|#endif
		|		}
		|		if (condgrp == 4) {
		|			condmask = 0x08;
		|			typ_cond(condsel, 2);
		|#if 0
		|			bool ovrsign = (!(((A_BIT(0) != B_BIT(0)) && state->is_binary) || (!state->is_binary && !A_BIT(0))));
		|			switch (condsel & 0x7) {
		|			case 0:	// L - TYP_ALU_CARRY
		|				state->cond = !state->coh;
		|				break;
		|			case 1: // L - TYP_ALU_OVERFLOW
		|				state->cond = state->ovr_en || (
		|				    state->coh ^ state->almsb ^ state->sub_else_add ^ ovrsign
		|				);
		|				break;
		|			case 2: // L - TYP_ALU_LT_ZERO
		|				state->cond = state->almsb;
		|				break;
		|			case 3: // L - TYP_ALU_LE_ZERO
		|				state->cond = !(state->almsb && (state->zero != 0xff));
		|				break;
		|			case 4: // ML - TYP_SIGN_BITS_EQUAL
		|				state->cond = (A_BIT(0) != B_BIT(0));
		|				break;
		|			case 5: // E - TYP_FALSE
		|				state->cond = true;
		|				break;
		|			case 6: // E - TYP_TRUE
		|				state->cond = false;
		|				break;
		|			case 7:	// E - TYP_PREVIOUS
		|				state->cond = state->last_cond;
		|				break;
		|			}
		|#endif
		|		}
		|	}
		|
		|	if (q2pos && (condgrp == 5 || condgrp == 6 || condgrp == 7)) {
		|
		|		if (condgrp == 5) {
		|			typ_cond(condsel, 2);
		|			condmask = 0x04;
		|		}
		|		if (condgrp == 6) {
		|			condmask = 0x02;
		|			typ_cond(condsel, 2);
		|		}
		|		if (condgrp == 7) {
		|			condmask = 0x01;
		|			typ_cond(condsel, 2);
		|		}
		|	}
		|
		|	if (h2 || PIN_WE.posedge()) {
		|		bool c_source = PIN_CSRC=>;
		|		fiu0 = c_source;
		|		fiu1 = c_source == (rand != 0x3);
		|
		|		bool sel = PIN_SEL=>;
		|
		|		if (!fiu0) {
		|			BUS_DF_READ(fiu);
		|			fiu ^= BUS_DF_MASK;
		|			fiu_valid = true;
		|			c |= fiu & 0xffffffff00000000ULL;
		|			chi = true;
		|		} else {
		|			if (sel) {
		|				c |= state->wdr & 0xffffffff00000000ULL;
		|			} else {
		|				c |= state->alu & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		}
		|		if (!fiu1) {
		|			if (!fiu_valid) {
		|				BUS_DF_READ(fiu);
		|				fiu ^= BUS_DF_MASK;
		|			}
		|			c |= fiu & 0xffffffffULL;
		|			clo = true;
		|		} else {
		|			if (sel) {
		|				c |= state->wdr & 0xffffffffULL;
		|			} else {
		|				c |= state->alu & 0xffffffffULL;
		|			}
		|			clo = true;
		|		}
		|		if (chi && !clo)
		|			c |= 0xffffffff;
		|		if (!chi && clo)
		|			c |= 0xffffffffULL << 32;
		|
		|		if (PIN_WE.posedge() && !state->wen) {
		|			state->rfram[state->cadr] = c;
		|		}
		|	}
		|	if (q4pos && sclke && !PIN_LDWDR=>) {
		|		BUS_DT_READ(state->wdr);
		|		state->wdr ^= BUS_DT_MASK;
		|	}
		|
		|	if (q4pos) {
		|		if (sclke) {
		|			if (uirc == 0x28) {
		|				state->count = c;
		|			} else if (rand == 0x2) {
		|				state->count += 1;
		|			} else if (rand == 0x1) {
		|				state->count += 0x3ff;
		|			}
		|			state->count &= 0x3ff;
		|		}
		|		if (rand == 0x2) {
		|			output.lovf = state->count != 0x3ff;
		|		} else if (rand == 0x1) {
		|			output.lovf = state->count != 0;
		|		} else {
		|			output.lovf = true;
		|		}
		|	}
		|
		|	if (!output.z_qt) {
		|		output.qt = state->b ^ BUS_QT_MASK;
		|	}
		|
		|	if (uirsclk) {
		|		state->csa_offset = csmux3;
		|	}
		|	if (PIN_CCLK.posedge()) {
		|		bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|		bot_mux_sel = PIN_LBOT=>;
		|		add_mux_sel = PIN_LTOP=>;
		|		top_mux_sel = !(add_mux_sel && PIN_LPOP=>);
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
		|	}
		|#if 0
		|	if (state->cond) {
		|		output.tcnd &= ~condmask;
		|	} else {
		|		output.tcnd |= condmask;
		|	}
		|	output.tcnd &= BUS_TCND_MASK;
		|#endif
		|	if (PIN_CCLK.posedge()) {
		|		state->last_cond = state->cond;
		|	}
		|	if (PIN_OFC.posedge()) {
		|		state->ofreg = state->b >> 32;
		|	}
		|
		|	unsigned priv_check;
		|	BUS_UPVC_READ(priv_check);
		|
		|	if (q4pos && sclke && priv_check != 7) {
		|		bool set_pass_priv = rand != 0xd;
		|		state->ppriv = set_pass_priv;
		|	}
		|
		|	bool micros_en = PIN_UEN=>;
		|
		|	unsigned selcond = 0xff;
		|	if (state->ppriv && micros_en) {
		|		selcond = 0x80 >> priv_check;
		|		selcond ^= 0xff;
		|	}
		|
		|	if (q3pos) {
		|		output.ue = BUS_UE_MASK;
		|		if (micros_en && selcond == 0xbf && bin_op_pass())
		|			output.ue &= ~0x20;	// T.BIN_OP.UE~
		|
		|		if (micros_en && selcond == 0x7f && priv_path_eq() && bin_op_pass())
		|			output.ue &= ~0x10;	// T.BIN_EQ.UE~
		|
		|		if (micros_en && (0x3 < rand && rand < 0x8) && clev(rand))
		|			output.ue &= ~0x08;	// T.CLASS.UE~
		|
		|		if (micros_en && selcond == 0xef && a_op_pass())
		|			output.ue &= ~0x04;	// T.TOS1_OP.UE~
		|		if (micros_en && selcond == 0xfb && b_op_pass())
		|			output.ue &= ~0x04;	// T.TOS1_OP.UE~
		|
		|		if (micros_en && selcond == 0xdf && a_op_pass())
		|			output.ue &= ~0x02;	// T.TOS_OP.UE~
		|		if (micros_en && selcond == 0xf7 && b_op_pass())
		|			output.ue &= ~0x02;	// T.TOS_OP.UE~
		|
		|		if (micros_en && (!((rand != 0xe) || !(B_LIT() != clit()))))
		|			output.ue &= ~0x01;	// T.CHK_SYS.UE~
		|	}
		|
		|	if (1 || q3pos) {	// Stops after VM-start
		|		output.t0stp = true;
		|		if (micros_en && (!((rand != 0xe) || !(B_LIT() != clit()))))
		|			output.t0stp = false;
		|		if (micros_en && (0x3 < rand && rand < 0x8) && clev(rand))
		|			output.t0stp = false;
		|		if (micros_en && priv_path_eq() && bin_op_pass() && selcond == 0x7f)
		|			output.t0stp = false;
		|
		|		output.t1stp = true;
		|		if (selcond == 0xbf && bin_op_pass())
		|			output.t1stp = false;
		|		if ((selcond == 0xef || selcond == 0xdf) && a_op_pass())
		|			output.t1stp = false;
		|		if ((selcond == 0xf7 || selcond == 0xfb) && b_op_pass())
		|			output.t1stp = false;
		|	}
		|
		|	output.spdr = true;
		|
		|	output.spdr = PIN_ADROE=> && PIN_VAEN=>;
		|	output.z_qsp = output.spdr;
		|
		|	if (q4pos || !output.z_qsp) {
		|		unsigned marctl;
		|		BUS_MCTL_READ(marctl);
		|
		|		if (marctl & 0x8) {
		|			output.qsp = (marctl & 0x7) ^ 0x7;
		|		} else {
		|			output.qsp = state->b ^ 0x7;
		|		}
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("TYP", PartModelDQ("TYP", TYP))