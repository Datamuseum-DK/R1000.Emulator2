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
		|	uint64_t alu;
		|	unsigned count;
		|	unsigned csa_offset;
		|	unsigned topreg;
		|	unsigned botreg;
		|	bool csa_hit;
		|	bool csa_write;
		|	unsigned aadr;
		|	unsigned badr;
		|	unsigned cadr;
		|	bool amsb, bmsb, cmsb, mbit, last_cond;
		|	bool isbin, sub_else_add, ovren, carry_middle;
		|	uint8_t zero;
		|	bool coh;
		|	bool wen;
		|	uint64_t *wcsram;
		|	uint64_t uir;
		|
		|#define UIR_A		((state->uir >> (39-5)) & 0x3f)
		|#define UIR_B		((state->uir >> (39-11)) & 0x3f)
		|#define UIR_FRM	((state->uir >> (39-16)) & 0x1f)
		|#define UIR_SEL	((state->uir >> (39-18)) & 0x3)
		|#define UIR_RAND	((state->uir >> (39-22)) & 0xf)
		|#define UIR_C		((state->uir >> (39-28)) & 0x3f)
		|#define UIR_MSRC	((state->uir >> (39-32)) & 0xf)
		|#define UIR_AFNC	((state->uir >> (39-37)) & 0x1f)
		|#define UIR_CSRC	((state->uir >> (39-38)) & 0x1)
		|''')


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), pa010, sizeof pa010, "PA010");
		|	load_programmable(this->name(), pa011, sizeof pa011, "PA011");
		|	state->wcsram = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
		|	state->csa_hit = true;
		|	state->csa_write = true;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_H2.neg()"

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned rand;
		|	uint8_t pa010[512];
		|	uint8_t pa011[512];
		|	bool csa_clk;
		|
		|	void dump_state(void);
		|	bool ovrsgn(void);
		|	bool cond_a(unsigned csel);
		|	bool cond_b(unsigned csel);
		|	bool cond_c(unsigned csel);
		|	bool fiu_cond(void);
		|	void find_a(void);
		|	void find_b(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|dump_state(void)
		|{
		|return;
		|ALWAYS_TRACE(
		|	<< "STATE " << std::hex
		|	<< " a " << state->a
		|	<< " b " << state->b
		|	<< " c " << state->c
		|	<< " wdr " << state->wdr
		|	<< " zc " << state->zerocnt
		|	<< " ch " << state->csa_hit
		|	<< " cw " << state->csa_write
		|	<< " lc " << state->last_cond
		|	<< " o.cwe " << output.cwe
		|	<< " o.z_qf " << output.z_qf
		|	<< " o.c_a " << output.vcnda
		|	<< " o.c_b " << output.vcndb
		|	<< " o.c_c " << output.vcndc
		|);
		|}
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
		|bool
		|SCM_«mmm» ::
		|cond_a(unsigned csel)
		|{
		|	bool cond;
		|	switch (csel & 0x7) {
		|	case 0:
		|		cond = (state->zero != 0xff);
		|		break;
		|	case 1:
		|	case 6:
		|		cond = (state->zero == 0xff);
		|		break;
		|	case 2:
		|		cond = !(
		|			(state->bmsb && (state->amsb ^ state->bmsb)) ||
		|			(!state->coh && (ovrsgn() ^ state->sub_else_add))
		|		);
		|		break;
		|	case 4:
		|		cond = state->count != 0x3ff;
		|		break;
		|	case 7:
		|		cond = state->carry_middle;
		|		break;
		|	default:
		|		cond = true;
		|		break;
		|	}
		|	output.vcnda = !cond;
		|	if (csa_clk) {
		|		state->last_cond = cond;
		|	}
		|	return (cond);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|cond_b(unsigned csel)
		|{
		|	bool cond;
		|	switch (csel & 0x7) {
		|	case 0:
		|		cond = !state->coh;
		|		break;
		|	case 1:
		|		cond = state->ovren || !(ovrsgn() ^ state->sub_else_add ^ (!state->coh) ^ state->cmsb);
		|		break;
		|	case 2:
		|		cond = state->cmsb;
		|		break;
		|	case 3:
		|		cond = !state->cmsb || (state->zero == 0xff);
		|		break;
		|	case 4:
		|		cond = (state->amsb ^ state->bmsb);
		|		break;
		|	case 7:
		|		cond = state->last_cond;
		|		break;
		|	default:
		|		cond = true;
		|		break;
		|	}
		|	output.vcndb = !cond;
		|	if (csa_clk) {
		|		state->last_cond = cond;
		|	}
		|	return (cond);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|cond_c(unsigned csel)
		|{
		|	bool cond;
		|	
		|	switch (csel & 7) {
		|	case 0:
		|		cond = ((state->zero & 0xf0) != 0xf0);
		|		break;
		|	case 1:
		|		cond = ((state->zero & 0xfc) != 0xfc);
		|		break;
		|	case 2:
		|		cond = ((state->zero & 0x0c) != 0x0c);
		|		break;
		|	case 3:
		|		cond = output.qbit;
		|		break;
		|	case 5:
		|		cond = state->mbit;
		|		break;
		|	case 6:
		|		cond = false;
		|		break;
		|	default:
		|		cond = true;
		|		break;
		|	}
		|	output.vcndc = !cond;
		|	if (csa_clk) {
		|		state->last_cond = cond;
		|	}
		|	return (cond);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|fiu_cond(void)
		|{
		|	unsigned csel;
		|	BUS_CSEL_READ(csel);
		|	bool fcond;
		|	switch (csel) {
		|	case 0x00:
		|		fcond = state->zero == 0xff;
		|		break;
		|	case 0x01:
		|		fcond = state->zero != 0xff;
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
		|	unsigned uira = UIR_A;
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
		|		unsigned frm = UIR_FRM;
		|		unsigned atos = (uira & 0xf) + state->topreg + 1;
		|		state->aadr = 0;
		|		if (uira == 0x2c) {
		|			state->aadr = state->count;
		|		} else if (uira <= 0x1f) {
		|			state->aadr = frm << 5;
		|			state->aadr |= uira & 0x1f;
		|		} else if (uira <= 0x2f) {
		|			state->aadr |= atos & 0xf;
		|		} else {
		|			state->aadr |= uira & 0x1f;
		|		}
		|		state->a = state->rfram[state->aadr];
		|	}
		|	state->amsb = state->a >> 63;
		|}
		|
		|void
		|SCM_«mmm» ::
		|find_b(void)
		|{
		|	unsigned uirb = UIR_B;
		|	bool oe, oe7;
		|	if (uirb != (0x16 ^ 0x3f)) {
		|		oe = false;
		|	} else if (!state->csa_hit && !PIN_QVOE=>) { 
		|		oe = false;
		|	} else {
		|		oe = true;
		|	}
		|
		|	bool get_literal = rand != 0x6;
		|	oe7 = oe || !get_literal;
		|
		|	unsigned frm = UIR_FRM;
		|	unsigned btos = (uirb & 0xf) + state->topreg + 1;
		|	unsigned csa = state->botreg + (uirb&1);
		|	if (!(uirb & 2)) {
		|		csa += state->csa_offset;
		|	}
		|	state->badr = 0;
		|	if (uirb == 0x2c) {
		|		state->badr = state->count;
		|	} else if (uirb <= 0x1f) {
		|		state->badr = frm << 5;
		|		state->badr |= uirb & 0x1f;
		|	} else if (uirb <= 0x27) {
		|		state->badr |= btos & 0xf;
		|	} else if (uirb <= 0x2b) {
		|		state->badr |= csa & 0xf;
		|	} else if (uirb <= 0x2f) {
		|		state->badr |= btos & 0xf;
		|	} else {
		|		state->badr |= uirb & 0x1f;
		|	}
		|	uint64_t b = 0;
		|	if (!oe) {
		|		b |= state->rfram[state->badr] & 0xffffffffffffff00ULL;
		|	}
		|	if (!oe7) {
		|		b |= state->rfram[state->badr] & 0xffULL;
		|	}
		|	if (oe || oe7) {
		|		uint64_t bus;
		|		bus = ~val_bus;
		|		if (oe) {
		|			b |= bus & 0xffffffffffffff00ULL;
		|		}
		|		if (oe7) {
		|			b |= bus & 0xffULL;
		|		}
		|	}
		|	state->b = b;
		|	state->bmsb = state->b >> 63;
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|	//bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	//bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	//bool h2 = PIN_H2=>;
		|	bool h1pos = PIN_H2.negedge();
		|	bool sclken = (PIN_STS=> && PIN_RMS=> && !PIN_FREZE=>);
		|	//csa_clk = PIN_CCLK.posedge();
		|	csa_clk = q4pos && sclken;
		|
		|	//bool uirsclk = PIN_UCLK.posedge();
		|	bool uirsclk = q4pos && !PIN_SFS=>;
		|	if (q4pos) dump_state();
		|
		|	unsigned uirc = UIR_C;
		|
		|	rand = UIR_RAND;
		|
		|	bool divide = rand != 0xb;
		|
		|
		|																											if (csa_clk) {
		|																												bool xor0c = state->mbit ^ (!state->coh);
		|																												bool xor0d = state->output.qbit ^ xor0c;
		|																												bool caoi0b = !(
		|																													((!divide) && xor0d) ||
		|																													(divide && state->coh)
		|																												);
		|																												output.qbit = caoi0b;
		|																											}
		|
		|
		|																											if (uirsclk) {
		|																												state->csa_hit = PIN_CSAH=>;
		|																												state->csa_write = PIN_CSAW=>;
		|																												output.cwe = !(state->csa_hit || state->csa_write);
		|																											}
		|
		|	output.z_qf = PIN_QFOE=>;
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|							if (h1pos && !output.z_qf) {
		|								find_a();
		|								output.qf = state->a ^ BUS_QF_MASK;
		|								fiu_bus = output.qf;
		|							}
		|							if (h1pos && !PIN_QVOE=>) {
		|								find_b();
		|								val_bus = ~state->b;
		|							}
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|															if (q2pos) {
		|																if (output.z_qf) {
		|																	find_a();
		|																}
		|																if (PIN_QVOE=>) {
		|																	find_b();
		|																}
		|																state->wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|																if (output.cwe && uirc != 0x28)
		|																	state->wen = !state->wen;
		|														
		|																state->msrc = UIR_MSRC;
		|																bool start_mult = rand != 0xc;
		|																if (!start_mult) {
		|																	state->malat = ~state->a;
		|																	state->mblat = ~state->b;
		|																}
		|
		|																struct f181 f181l, f181h;
		|																unsigned tmp, proma, alur;
		|														
		|																tmp = UIR_RAND;
		|																if (tmp < 8) {
		|																	alur = 7;
		|																} else {
		|																	alur = 15 - tmp;
		|																}
		|														
		|																proma = UIR_AFNC;
		|																proma |= alur << 5;
		|																if (
		|																	!(
		|																		(state->last_cond && divide) ||
		|																		(output.qbit && !divide)
		|																	)
		|																) {
		|																	proma |= 0x100;
		|																}
		|														
		|																tmp = pa011[proma];			// S0-4.LOW
		|																state->isbin = (tmp >> 1) & 1;			// IS_BINARY
		|																f181l.ctl = (tmp >> 4) & 0xf;
		|																f181l.ctl |= ((tmp >> 3) & 1) << 4;
		|																f181l.ctl |= 1 << 5;
		|																f181l.ci = (pa011[proma] >> 2) & 1;	// ALU.C15
		|																f181l.a = state->a & 0xffffffff;
		|																f181l.b = state->b & 0xffffffff;
		|																f181_alu(&f181l);
		|																state->carry_middle = f181l.co;
		|																state->alu = f181l.o;
		|														
		|																tmp = pa010[proma];			// S0-4.HIGH
		|																state->ovren = (tmp >> 1) & 1;			// OVR.EN~
		|																state->sub_else_add = (tmp >> 2) & 1;			// SUB_ELSE_ADD
		|																f181h.ctl = (tmp >> 4) & 0xf;
		|																f181h.ctl |= ((tmp>>3) & 1) << 4;
		|																f181h.ctl |= 1 << 5;
		|																f181h.ci = f181l.co;
		|																f181h.a = state->a >> 32;
		|																f181h.b = state->b >> 32;
		|																f181_alu(&f181h);
		|																state->coh = f181h.co;
		|																state->alu |= ((uint64_t)f181h.o) << 32;
		|																state->zero = 0;
		|																if (!(state->alu & (0xffULL) <<  0)) state->zero |= 0x01;
		|																if (!(state->alu & (0xffULL) <<  8)) state->zero |= 0x02;
		|																if (!(state->alu & (0xffULL) << 16)) state->zero |= 0x04;
		|																if (!(state->alu & (0xffULL) << 24)) state->zero |= 0x08;
		|																if (!(state->alu & (0xffULL) << 32)) state->zero |= 0x10;
		|																if (!(state->alu & (0xffULL) << 40)) state->zero |= 0x20;
		|																if (!(state->alu & (0xffULL) << 48)) state->zero |= 0x40;
		|																if (!(state->alu & (0xffULL) << 56)) state->zero |= 0x80;
		|																state->alu = ~state->alu;
		|																state->cmsb = state->alu >> 63;
		|																if (!PIN_ADROE=>) {
		|																	unsigned spc = spc_bus;
		|																	uint64_t alu = state->alu;
		|														
		|																	if (spc != 4) {
		|																		alu |=0xf8000000ULL;
		|																	}
		|														
		|																	// output.adr = alu ^ BUS_ADR_MASK;
		|																	adr_bus = alu ^ ~0ULL;;
		|																}
		|															}
		|
		|															if (q2pos) {
		|																uint64_t c2;
		|																uint64_t fiu = 0, mux = 0;
		|																bool c_source = UIR_CSRC;
		|																bool split_c_src = rand == 0x4;
		|																if (split_c_src || !c_source) {
		|																	BUS_DF_READ(fiu);
		|																	fiu ^= BUS_DF_MASK;
		|																	if ((c_source == split_c_src) && (rand == 3 || rand == 6)) {
		|																		fiu &= ~1ULL;
		|																		fiu |= fiu_cond();
		|																	}
		|																}
		|																if (c_source || split_c_src) {
		|																	unsigned sel = UIR_SEL;
		|																	switch (sel) {
		|																	case 0x0:
		|																		mux = state->alu << 1;
		|																		mux |= 1;
		|																		break;
		|																	case 0x1:
		|																		mux = state->alu >> 16;
		|																		mux |= 0xffffULL << 48;
		|																		break;
		|																	case 0x2: mux = state->alu; break;
		|																	case 0x3: mux = state->wdr; break;
		|																	}
		|																}
		|																if (!split_c_src && !c_source) {
		|																	c2 = fiu;
		|																} else if (!split_c_src) {
		|																	c2 = mux;
		|																} else if (c_source) {
		|																	c2 = fiu & 0xffffffffULL;
		|																	c2 |= mux & 0xffffffffULL << 32;
		|																} else {
		|																	c2 = mux & 0xffffffffULL;
		|																	c2 |= fiu & 0xffffffffULL << 32;
		|																}
		|																state->c = c2;
		|															}
		|
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|																			if (q2pos) {
		|																				unsigned frm = UIR_FRM;
		|																				state->cadr = 0;
		|																				if (uirc <= 0x1f) {
		|																					// FRAME:REG
		|																					state->cadr |= uirc & 0x1f;
		|																					state->cadr |= frm << 5;
		|																				} else if (uirc <= 0x27) {
		|																					// 0x20 = TOP-1
		|																					// …
		|																					// 0x27 = TOP-8
		|																					state->cadr = (state->topreg + (uirc & 0x7) + 1) & 0xf;
		|																				} else if (uirc == 0x28) {
		|																					// 0x28 LOOP COUNTER (RF write disabled)
		|																				} else if (uirc == 0x29 && output.cwe) {
		|																					// 0x29 DEFAULT (RF write disabled)
		|																					unsigned sum = state->botreg + state->csa_offset + 1;
		|																					state->cadr |= sum & 0xf;
		|																				} else if (uirc == 0x29 && !output.cwe) {
		|																					// 0x29 DEFAULT (RF write disabled)
		|																					state->cadr |= uirc & 0x1f;
		|																					state->cadr |= frm << 5;
		|																				} else if (uirc <= 0x2b) {
		|																					// 0x2a BOT
		|																					// 0x2b BOT-1
		|																					state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|																					state->cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|																				} else if (uirc == 0x2c) {
		|																					// 0x28 = LOOP_REG
		|																					state->cadr = state->count;
		|																				} else if (uirc == 0x2d) {
		|																					// 0x2d SPARE
		|																					assert (uirc != 0x2d);
		|																				} else if (uirc <= 0x2f) {
		|																					// 0x2e = TOP+1
		|																					// 0x2f = TOP
		|																					state->cadr = (state->topreg + (uirc & 0x1) + 0xf) & 0xf;
		|																				} else if (uirc <= 0x3f) {
		|																					// GP[0…F]
		|																					state->cadr |= 0x10 | (uirc & 0x0f);
		|																				} else {
		|																					assert(uirc <= 0x3f);
		|																				}
		|																			}
		|																											if (q4pos) {
		|																												bool awe = (!(PIN_FREZE=>) && PIN_RMS=>);
		|																												if (awe && !state->wen) {
		|																													state->rfram[state->cadr] = state->c;
		|																												}
		|																												if (csa_clk && rand == 0x5) {
		|																													uint64_t count2 = 0x40 - flsll(~state->alu);
		|																													state->zerocnt = ~count2;
		|																												}
		|																												if (!PIN_LDWDR=> && sclken) {
		|																													state->wdr = ~val_bus;
		|																												}
		|																												uint32_t a;
		|																												switch (state->msrc >> 2) {
		|																												case 0: a = (state->malat >> 48) & 0xffff; break;
		|																												case 1: a = (state->malat >> 32) & 0xffff; break;
		|																												case 2: a = (state->malat >> 16) & 0xffff; break;
		|																												case 3: a = (state->malat >>  0) & 0xffff; break;
		|																												}
		|																												uint32_t b;
		|																												switch (state->msrc & 3) {
		|																												case 0: b = (state->mblat >> 48) & 0xffff; break;
		|																												case 1: b = (state->mblat >> 32) & 0xffff; break;
		|																												case 2: b = (state->mblat >> 16) & 0xffff; break;
		|																												case 3: b = (state->mblat >>  0) & 0xffff; break;
		|																												}
		|																												state->mprod = a * b;
		|																											
		|																												bool incl = rand != 0x1;
		|																												bool decl = rand != 0x2;
		|																												bool lnan1a = !(decl && incl && divide);
		|																												bool count_up = !(decl && divide);
		|																												bool count_en = !(lnan1a && sclken);
		|																												bool lcmp28 = uirc != 0x28;
		|																												bool lnan3a = !(lcmp28);
		|																												bool lnan3b = sclken;
		|																												bool lnan2c = !(lnan3a && lnan3b);
		|																												if (!lnan2c) {
		|																													state->count = state->c;
		|																												} else if (!count_en && count_up) {
		|																													state->count += 1;
		|																												} else if (!count_en) {
		|																													state->count += 0x3ff;
		|																												}
		|																												state->count &= 0x3ff;
		|																											
		|																												unsigned csmux3;
		|																												BUS_CSAO_READ(csmux3);
		|																												csmux3 ^= BUS_CSAO_MASK;
		|																												if (uirsclk) {
		|																													state->csa_offset = csmux3;
		|																												}
		|																												if (csa_clk) {
		|																													bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|																													bot_mux_sel = PIN_LBOT=>;
		|																													add_mux_sel = PIN_LTOP=>;
		|																													top_mux_sel = !(add_mux_sel && PIN_LPOP=>);
		|																										
		|																													unsigned csmux0;
		|																													if (add_mux_sel)
		|																														csmux0 = state->botreg;
		|																													else
		|																														csmux0 = state->topreg;
		|																											
		|																													unsigned csalu0 = csmux3 + csmux0 + 1;
		|																											
		|																													if (!bot_mux_sel)
		|																														state->botreg = csalu0;
		|																													if (top_mux_sel)
		|																														state->topreg = csalu0;
		|																												}
		|																											
		|																												if (csa_clk) {
		|																													state->mbit = state->cmsb;
		|																												}
		|																												if (uirsclk) {
		|																													unsigned addr;
		|																													BUS_UAD_READ(addr);
		|																													state->uir = state->wcsram[addr] ^ 0xffff800000ULL;
		|																												}
		|																											}
		|
		|	unsigned csel;
		|	BUS_CSEL_READ(csel);
		|	switch (csel >> 3) {
		|	case 0x0: cond_a(csel); break;
		|	case 0x1: cond_b(csel); break;
		|	case 0x2: cond_c(csel); break;
		|	case 0xb: cond_a(csel); break;
		|	default: break;
		|	}
		|
		|	if (q4pos) dump_state();
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("VAL", PartModelDQ("VAL", VAL))
