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

class XTCMUX(PartFactory):
    ''' TYP C-bus mux '''

    autopin = True

    def state(self, file):
 
        file.fmt('''
		|	uint64_t rfram[1<<10];
		|	uint8_t pa010[512], pa068[512];
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
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pa010, sizeof state->pa010,
		|	    "PA010");
		|	load_programmable(this->name(),
		|	    state->pa068, sizeof state->pa068,
		|	    "PA068");
		|''')
        super().init(file)

    def sensitive(self):
            yield "PIN_CSRC"
            yield "BUS_DT"
            yield "BUS_DF"
            yield "PIN_LDWDR"
            yield "PIN_Q2"
            yield "PIN_Q4"
            yield "PIN_QTOE"
            yield "PIN_SEL"
            yield "BUS_UIRA"
            yield "BUS_UIRB"
            yield "PIN_ADROE"
            yield "PIN_WE.pos()"


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
		|	bool sclke = PIN_SCLKE=>;
		|
		|	unsigned uira, uirb, uirc, rand;
		|	BUS_UIRA_READ(uira);
		|	BUS_UIRB_READ(uirb);
		|	BUS_UIRC_READ(uirc);
		|	BUS_RAND_READ(rand);
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
		|
		|	output.z_qf = PIN_QFOE=>;
		|
		|	if (!h2) {
		|		if ((uira & 0x3c) != 0x28) {
		|			state->a = state->rfram[state->aadr];
		|		} else if (uira == 0x28) {
		|			state->a = BUS_A_MASK;
		|			state->a ^= 0x3ff;
		|			state->a |= state->count;
		|		} else {
		|			state->a = BUS_A_MASK;
		|		}
		|		output.a = state->a;
		|		if (!output.z_qf) {
		|			output.qf = output.a ^ BUS_QF_MASK;
		|		}
		|		output.amsb = output.a >> 63;
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
		|		output.b = state->b;
		|	}
		|	if (q2pos) {
		|		struct f181 f181l, f181h;
		|		unsigned tmp, idx, alurand, alufunc;
		|		BUS_AFNC_READ(alufunc);
		|
		|		if (rand < 8) {
		|			alurand = 7;
		|		} else {
		|			alurand = 15 - rand;
		|		}
		|		idx = PIN_ACOND=> << 8;
		|		idx |= alurand << 5;
		|		idx |= alufunc;
		|		
		|		tmp = state->pa068[idx] >> 3;
		|		f181l.ctl = tmp >> 1;
		|		f181l.ctl |= (tmp & 1) << 4;
		|		f181l.ctl |= (rand != 0xf) << 5;
		|		f181l.ci = (state->pa068[idx] >> 2) & 1;
		|		f181l.a = state->a & 0xffffffff;
		|		f181l.b = state->b & 0xffffffff;
		|		f181_alu(&f181l);
		|		output.com = f181l.co;
		|		state->alu = f181l.o;
		|
		|		tmp = state->pa010[idx] >> 3;
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
		|		output.almsb = state->alu >> 63ULL;
		|
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
		|		if (PIN_WE.posedge()) {
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
		|		output.lo = state->count;
		|	}
		|
		|	if (!output.z_qt) {
		|		output.qt = output.b ^ BUS_QT_MASK;
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
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCMUX", PartModelDQ("XTCMUX", XTCMUX))
