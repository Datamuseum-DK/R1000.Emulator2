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

class XVCMUX(PartFactory):
    ''' VAL C-bus mux '''

    autopin = True

    def state(self, file):
 
        file.fmt('''
		|	uint64_t rfram[1<<10];
		|	uint64_t a, b, c;
		|	uint64_t wdr;
		|	uint64_t zero;
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
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "PIN_QFOE.neg()"
        yield "PIN_QVOE.neg()"
        yield "PIN_ADROE.neg()"
        yield "BUS_UIRA"
        yield "BUS_UIRB"
        yield "PIN_ZSCK.pos()"
        yield "PIN_AWE.pos()"
        yield "PIN_UCLK.pos()"
        yield "PIN_CCLK.pos()"
        yield "PIN_H2"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	bool h2 = PIN_H2=>;
		|	bool sclken = PIN_SCLKE=>;
		|
		|	bool uirsclk = PIN_UCLK.posedge();
		|
		|	unsigned uira, uirb, uirc;
		|	BUS_UIRA_READ(uira);
		|	BUS_UIRB_READ(uirb);
		|	BUS_UIRC_READ(uirc);
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
		|	output.wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|	if (output.cwe && uirc != 0x28)
		|		output.wen = !output.wen;
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
		|	unsigned rand;
		|	BUS_RAND_READ(rand);
		|	bool split_c_src = rand != 0x4;
		|	bool get_literal = rand != 0x6;
		|	bool start_mult = rand != 0xc;
		|	bool prod_16 = rand != 0xd;
		|	bool prod_32 = rand != 0xe;
		|	if (rand < 8) {
		|		output.alur = 7;
		|	} else {
		|		output.alur = 15 - rand;
		|	}
		|	output.cntz = rand != 0x5;
		|	output.div = rand != 0xb;
		|	output.sneak = (rand != 0x3) && (rand != 0x6);
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (q2pos || (!h2 && !output.z_qf)) {
		|		if (uira ==0x28) {
		|			state->a = state->count;
		|			state->a |= ~BUS_CNT_MASK;
		|		} else if (uira ==0x29) {
		|			unsigned mdst;
		|			// BUS_MDST_READ(mdst);
		|			mdst = prod_32 << 1;
		|			mdst |= prod_16;
		|			switch(mdst) {
		|			case 0: state->a = 0; break;
		|			case 1: state->a = state->mprod << 32; break;
		|			case 2: state->a = state->mprod << 16; break;
		|			case 3: state->a = state->mprod <<  0; break;
		|			}
		|			state->a ^= BUS_DV_MASK;
		|		} else if (uira == 0x2a) {
		|			state->a = state->zero;
		|		} else if (uira ==0x2b) {
		|			state->a = BUS_DV_MASK;
		|		} else {
		|			state->a = state->rfram[state->aadr];
		|		}
		|		if (!output.z_qf) {
		|			output.qf = state->a ^ BUS_QF_MASK;
		|		}
		|		output.amsb = state->a >> 63;
		|	}
		|
		|	output.z_qv = PIN_QVOE=>;
		|	if (q2pos || (!h2 && !output.z_qv)) {
		|		bool oe, oe7;
		|		if (uirb != (0x16 ^ BUS_UIRB_MASK)) {
		|			oe = false;
		|		} else if (!state->csa_hit && !PIN_QVOE=>) { 
		|			oe = false;
		|		} else {
		|			oe = true;
		|		}
		|
		|		oe7 = oe || !get_literal;
		|
		|		uint64_t b = 0;
		|		if (!oe) {
		|			b |= state->rfram[state->badr] & 0xffffffffffffff00ULL;
		|		}
		|		if (!oe7) {
		|			b |= state->rfram[state->badr] & 0xffULL;
		|		}
		|		if (oe || oe7) {
		|			uint64_t bus;
		|			BUS_DV_READ(bus);
		|			bus ^= BUS_DV_MASK;
		|			if (oe) {
		|				b |= bus & 0xffffffffffffff00ULL;
		|			}
		|			if (oe7) {
		|				b |= bus & 0xffULL;
		|			}
		|		}
		|		state->b = b;
		|		if (!output.z_qv) {
		|			output.qv = state->b ^ BUS_QV_MASK;
		|		}
		|		output.bmsb = state->b >> 63;
		|	}
		|
		|	if (q2pos) {
		|		BUS_MSRC_READ(state->msrc);
		|		if (!start_mult) {
		|			state->malat = state->a ^ BUS_DV_MASK;
		|			state->mblat = state->b ^ BUS_DV_MASK;
		|		}
		|	}
		|
		|	if (q2pos) {
		|		struct f181 f181l, f181h;
		|		unsigned tmp;
		|
		|		BUS_ACL_READ(tmp);
		|		f181l.ctl = tmp >> 1;
		|		f181l.ctl |= (tmp & 1) << 4;
		|		f181l.ctl |= 1 << 5;
		|		f181l.ci = PIN_CI=>;
		|		f181l.a = state->a & 0xffffffff;
		|		f181l.b = state->b & 0xffffffff;
		|		f181_alu(&f181l);
		|		output.com = f181l.co;
		|		state->alu = f181l.o;
		|
		|		BUS_ACH_READ(tmp);
		|		f181h.ctl = tmp >> 1;
		|		f181h.ctl |= (tmp & 1) << 4;
		|		f181h.ctl |= 1 << 5;
		|		f181h.ci = f181l.co;
		|		f181h.a = state->a >> 32;
		|		f181h.b = state->b >> 32;
		|		f181_alu(&f181h);
		|		output.coh = f181h.co;
		|		state->alu |= ((uint64_t)f181h.o) << 32;
		|		output.zero = 0;
		|		if (!(state->alu & (0xffULL) <<  0)) output.zero |= 0x01;
		|		if (!(state->alu & (0xffULL) <<  8)) output.zero |= 0x02;
		|		if (!(state->alu & (0xffULL) << 16)) output.zero |= 0x04;
		|		if (!(state->alu & (0xffULL) << 24)) output.zero |= 0x08;
		|		if (!(state->alu & (0xffULL) << 32)) output.zero |= 0x10;
		|		if (!(state->alu & (0xffULL) << 40)) output.zero |= 0x20;
		|		if (!(state->alu & (0xffULL) << 48)) output.zero |= 0x40;
		|		if (!(state->alu & (0xffULL) << 56)) output.zero |= 0x80;
		|		state->alu = ~state->alu;
		|		output.cmsb = state->alu >> 63;
		|		output.z_adr = PIN_ADROE=>;
		|		if (!output.z_adr) {
		|			unsigned spc;
		|			BUS_SPC_READ(spc);
		|			uint64_t alu = state->alu;
		|
		|			if (spc != 4) {
		|				alu |=0xf8000000ULL;
		|			}
		|
		|			output.adr = alu ^ BUS_ADR_MASK;
		|		}
		|	}
		|
		|	if (h2) {
		|		uint64_t c = 0;
		|		uint64_t fiu = 0, wdr = 0;
		|		bool sel0 = PIN_SEL0=>;
		|		bool sel1 = PIN_SEL1=>;
		|		bool c_source = PIN_CSRC=>;
		|		bool efiu0 = !c_source;
		|		bool efiu1 = (c_source != split_c_src);
		|		bool chi = false;
		|		bool clo = false;
		|
		|		if (efiu0 || efiu1) {
		|			BUS_DF_READ(fiu);
		|			fiu ^= BUS_DF_MASK;
		|		}
		|		if (efiu0) {
		|			c |= fiu & 0xffffffff00000000ULL;
		|			chi = true;
		|		} else if (!sel0) {
		|			if (sel1) {
		|				c |= (state->alu >> 16) & 0xffffffff00000000ULL;
		|				c |= 0xffff000000000000ULL;
		|			} else {
		|				c |= (state->alu << 1) & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		} else {
		|			if (sel1) {
		|				wdr = state->wdr;
		|				c |= wdr & 0xffffffff00000000ULL;
		|			} else {
		|				c |= state->alu & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		}
		|		if (efiu1) {
		|			c |= fiu & 0xfffffffeULL;
		|			unsigned csel;
		|			BUS_CSEL_READ(csel);
		|			if (csel == 7) {
		|				c |= fiu & 0x1ULL;
		|			} else {
		|				unsigned cond = PIN_COND=>;
		|				c |= cond & 1;
		|			}
		|			clo = true;
		|		} else if (!sel0) {
		|			if (sel1) {
		|				c |= (state->alu >> 16) & 0xffffffffULL;
		|			} else {
		|				c |= (state->alu << 1) & 0xffffffffULL;
		|				c |= 1;
		|			}
		|			clo = true;
		|		} else {
		|			if (sel1) {
		|				wdr = state->wdr;
		|				c |= wdr & 0xffffffffULL;
		|			} else {
		|				c |= state->alu & 0xffffffffULL;
		|			}
		|			clo = true;
		|		}
		|		if (chi && !clo)
		|			c |= 0xffffffff;
		|		if (!chi && clo)
		|			c |= 0xffffffffULL << 32;
		|		state->c = c;
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
		|	if (PIN_AWE.posedge()) {
		|		state->rfram[state->cadr] = state->c;
		|	}
		|	if (PIN_ZSCK.posedge()) {
		|		uint64_t probe = (1ULL<<63), count;
		|		for (count = 0; count < 65; count++) {
		|			if (!(state->alu & probe))
		|				break;
		|			probe >>= 1;
		|		}
		|		state->zero = ~count;
		|	}
		|	if (q4pos && !PIN_LDWDR=> && sclken) {
		|		BUS_DV_READ(state->wdr);
		|		state->wdr ^= BUS_DV_MASK;
		|	}
		|	if (q4pos) {
		|		uint32_t a;
		|		switch (state->msrc >> 2) {
		|		case 0: a = (state->malat >> 48) & 0xffff; break;
		|		case 1: a = (state->malat >> 32) & 0xffff; break;
		|		case 2: a = (state->malat >> 16) & 0xffff; break;
		|		case 3: a = (state->malat >>  0) & 0xffff; break;
		|		}
		|		uint32_t b;
		|		switch (state->msrc & 3) {
		|		case 0: b = (state->mblat >> 48) & 0xffff; break;
		|		case 1: b = (state->mblat >> 32) & 0xffff; break;
		|		case 2: b = (state->mblat >> 16) & 0xffff; break;
		|		case 3: b = (state->mblat >>  0) & 0xffff; break;
		|		}
		|		state->mprod = a * b;
		|	}
		|
		|	if (q4pos) {
		|		bool incl = rand != 0x1;
		|		bool decl = rand != 0x2;
		|		bool lnan1a = !(decl && incl && output.div);
		|		bool count_up = !(decl && output.div);
		|		bool count_en = !(lnan1a && sclken);
		|		bool lcmp28 = uirc != 0x28;
		|		bool lnan3a = !(lcmp28);
		|		bool lnan3b = sclken;
		|		bool lnan2c = !(lnan3a && lnan3b);
		|		if (count_en) {
		|			output.cntov = true;
		|		} else if (count_up) {
		|			output.cntov = state->count != BUS_CNT_MASK;
		|		} else {
		|			output.cntov = state->count != 0;
		|		}
		|		if (!lnan2c) {
		|			state->count = state->c;
		|		} else if (!count_en && count_up) {
		|			state->count += 1;
		|		} else if (!count_en) {
		|			state->count += BUS_CNT_MASK;
		|		}
		|		state->count &= BUS_CNT_MASK;
		|		output.cnt = state->count;
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
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCMUX", PartModelDQ("XVCMUX", XVCMUX))
