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

from part import PartModel, PartFactory

class XVCMUX(PartFactory):
    ''' VAL C-bus mux '''

    autopin = True

    def state(self, file):
 
        file.fmt('''
		|	uint64_t aram[1<<BUS_ADR_WIDTH];
		|	uint64_t alat;
		|	uint64_t c;
		|	uint64_t wdr;
		|	uint64_t zero;
		|	uint64_t malat, mblat, mprod, msrc;
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "BUS_UIA"
        yield "BUS_LOP"
        yield "PIN_ZSCK.pos()"
        yield "PIN_WE.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q4pos = PIN_Q4.posedge();
		|
		|	if (true) {
		|		uint64_t c = 0;
		|		uint64_t fiu = 0, alu = 0, wdr = 0;
		|		bool fiu_valid = false, alu_valid = false;
		|		bool sel0 = PIN_SEL0=>;
		|		bool sel1 = PIN_SEL1=>;
		|		bool c_source = PIN_CSRC=>;
		|		bool split_c_src = PIN_CSPL=>;
		|		bool efiu0 = !c_source;
		|		bool efiu1 = (c_source != split_c_src);
		|		bool chi = false;
		|		bool clo = false;
		|
		|		if (efiu0) {
		|			BUS_FIU_READ(fiu);
		|			fiu ^= BUS_FIU_MASK;
		|			fiu_valid = true;
		|			c |= fiu & 0xffffffff00000000ULL;
		|			chi = true;
		|		} else if (!sel0) {
		|			BUS_ALU_READ(alu);
		|			alu_valid = true;
		|			if (sel1) {
		|				c |= (alu >> 16) & 0xffffffff00000000ULL;
		|				c |= 0xffff000000000000ULL;
		|			} else {
		|				c |= (alu << 1) & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		} else {
		|			if (sel1) {
		|				wdr = state->wdr;
		|				c |= wdr & 0xffffffff00000000ULL;
		|			} else {
		|				BUS_ALU_READ(alu);
		|				alu_valid = true;
		|				c |= alu & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		}
		|		if (efiu1) {
		|			if (!fiu_valid) {
		|				BUS_FIU_READ(fiu);
		|				fiu ^= BUS_FIU_MASK;
		|			}
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
		|			if (!alu_valid)
		|				BUS_ALU_READ(alu);
		|			if (sel1) {
		|				c |= (alu >> 16) & 0xffffffffULL;
		|			} else {
		|				c |= (alu << 1) & 0xffffffffULL;
		|				c |= 1;
		|			}
		|			clo = true;
		|		} else {
		|			if (sel1) {
		|				wdr = state->wdr;
		|				c |= wdr & 0xffffffffULL;
		|			} else {
		|				if (!alu_valid)
		|					BUS_ALU_READ(alu);
		|				c |= alu & 0xffffffffULL;
		|			}
		|			clo = true;
		|		}
		|		if (chi && !clo)
		|			c |= 0xffffffff;
		|		if (!chi && clo)
		|			c |= 0xffffffffULL << 32;
		|		if (PIN_WE.posedge()) {
		|			unsigned adr;
		|			BUS_ADR_READ(adr);
		|			state->aram[adr] = c;
		|		}
		|		if (!PIN_OE=>) {
		|			unsigned adr;
		|			BUS_ADR_READ(adr);
		|			output.c = state->aram[adr];
		|		} else {
		|			output.c = c;
		|		}
		|	}
		|
		|	if (!PIN_Q2=>) {
		|		state->alat = output.c;
		|	}
		|	//output.z_a = PIN_AOE=>;
		|	if (1) {
		|		unsigned uir_a;
		|		BUS_UIA_READ(uir_a);
		|		if (uir_a ==0x28) {
		|			BUS_LOP_READ(output.a);
		|			output.a |= ~BUS_LOP_MASK;
		|		} else if (uir_a ==0x29) {
		|			unsigned mdst;
		|			BUS_MDST_READ(mdst);
		|			switch(mdst) {
		|			case 0: output.a = 0; break;
		|			case 1: output.a = state->mprod << 32; break;
		|			case 2: output.a = state->mprod << 16; break;
		|			case 3: output.a = state->mprod <<  0; break;
		|			}
		|			output.a ^= BUS_A_MASK;
		|		} else if (uir_a == 0x2a) {
		|			output.a = state->zero;
		|		} else if (uir_a ==0x2b) {
		|			output.a = BUS_A_MASK;
		|		} else {
		|			output.a = state->alat;
		|		}
		|	}
		|	if (PIN_ZSCK.posedge()) {
		|		uint64_t alu, probe = (1ULL<<63), count;
		|		BUS_ALU_READ(alu);
		|		for (count = 0; count < 65; count++) {
		|			if (!(alu & probe))
		|				break;
		|			probe >>= 1;
		|		}
		|		state->zero = ~count;
		|	}
		|	if (q4pos && !PIN_LDWDR=> &&  PIN_SCLKE=>) {
		|		BUS_VAL_READ(state->wdr);
		|		state->wdr ^= BUS_VAL_MASK;
		|	}
		|	if (q2pos) {
		|		BUS_MSRC_READ(state->msrc);
		|		if (!PIN_MSTRT=>) {
		|			state->malat = output.a ^ BUS_A_MASK;
		|			BUS_B_READ(state->mblat);
		|			state->mblat ^= BUS_B_MASK;
		|		}
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
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCMUX", PartModel("XVCMUX", XVCMUX))
