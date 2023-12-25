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

    def state(self, file):
 
        file.fmt('''
		|	uint64_t aram[1<<BUS_A_WIDTH];
		|	uint64_t c;
		|''')

    def xxsensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (state->ctx.job) {
		|		BUS_C_WRITE(state->c);
		|		state->ctx.job = 0;
		|	}
		|	uint64_t c = 0;
		|	uint64_t fiu = 0, alu = 0, wdr = 0;
		|	bool fiu_valid = false, alu_valid = false, wdr_valid = false;
		|	bool sel0 = PIN_SEL0=>;
		|	bool sel1 = PIN_SEL1=> || !PIN_FPA=>;
		|	bool diag_mux_sel = PIN_DGMS=>;
		|	bool cm_diag_on = PIN_DGCO=>;
		|	bool hilo = 
		|		(diag_mux_sel && sel0) ||
		|		(diag_mux_sel && !cm_diag_on);
		|	bool c_source = PIN_CSRC=>;
		|	bool split_c_src = PIN_CSPL=>;
		|	bool efiu0 = cm_diag_on && !c_source;
		|	bool efiu1 = cm_diag_on && (c_source != split_c_src);
		|	bool chi = false;
		|	bool clo = false;
		|
		|	if (!PIN_OE=>) {
		|		unsigned adr;
		|		BUS_A_READ(adr);
		|		c = state->aram[adr];
		|		if (c != state->c) {
		|			state->ctx.job = 1;
		|			state->c = c;
		|			next_trigger(5, sc_core::SC_NS);
		|		}
		|		return;
		|	}
		|
		|	if (efiu0) {
		|		BUS_FIU_READ(fiu);
		|		fiu ^= BUS_FIU_MASK;
		|		fiu_valid = true;
		|		c |= fiu & 0xffffffff00000000ULL;
		|		chi = true;
		|	} else if (!hilo) {
		|		BUS_ALU_READ(alu);
		|		alu_valid = true;
		|		if (sel1) {
		|			c |= (alu >> 16) & 0xffffffff00000000ULL;
		|			c |= 0xffff000000000000ULL;
		|		} else {
		|			c |= (alu << 1) & 0xffffffff00000000ULL;
		|		}
		|		chi = true;
		|	} else {
		|		if (sel1) {
		|			BUS_WDR_READ(wdr);
		|			wdr_valid = true;
		|			c |= wdr & 0xffffffff00000000ULL;
		|		} else {
		|			BUS_ALU_READ(alu);
		|			alu_valid = true;
		|			c |= alu & 0xffffffff00000000ULL;
		|		}
		|		chi = true;
		|	}
		|	if (efiu1) {
		|		if (!fiu_valid) {
		|			BUS_FIU_READ(fiu);
		|			fiu ^= BUS_FIU_MASK;
		|		}
		|		c |= fiu & 0xfffffffeULL;
		|		unsigned csel;
		|		BUS_CSEL_READ(csel);
		|		if (csel == 7) {
		|			c |= fiu & 0x1ULL;
		|		} else {
		|			unsigned cond = PIN_COND=>;
		|			c |= cond & 1;
		|		}
		|		clo = true;
		|	} else if (!hilo) {
		|		if (!alu_valid)
		|			BUS_ALU_READ(alu);
		|		if (sel1) {
		|			c |= (alu >> 16) & 0xffffffffULL;
		|		} else {
		|			c |= (alu << 1) & 0xffffffffULL;
		|			c |= 1;
		|		}
		|		clo = true;
		|	} else {
		|		if (sel1) {
		|			if (!wdr_valid)
		|				BUS_WDR_READ(wdr);
		|			c |= wdr & 0xffffffffULL;
		|		} else {
		|			if (!alu_valid)
		|				BUS_ALU_READ(alu);
		|			c |= alu & 0xffffffffULL;
		|		}
		|		clo = true;
		|	}
		|	if (chi && !clo)
		|		c |= 0xffffffff;
		|	if (!chi && clo)
		|		c |= 0xffffffffULL << 32;
		|	if (PIN_WE.posedge()) {
		|		unsigned adr;
		|		BUS_A_READ(adr);
		|		state->aram[adr] = c;
		|	}
		|	if (c != state->c) {
		|		state->ctx.job = 1;
		|		state->c = c;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|	TRACE(
		|	    << " sel0 " << PIN_SEL0?
		|	    << " sel1 " << PIN_SEL1?
		|	    << " csrc " << PIN_CSRC?
		|	    << " cspl " << PIN_CSPL?
		|	    << " dgms " << PIN_DGMS?
		|	    << " dgco " << PIN_DGCO?
		|	    << " fpa " << PIN_FPA?
		|	    << " fiu " << BUS_FIU_TRACE()
		|	    << " wdr " << BUS_WDR_TRACE()
		|	    << " alu " << BUS_ALU_TRACE()
		|	    << " c " << std::hex << c
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCMUX", PartModel("XVCMUX", XVCMUX))
