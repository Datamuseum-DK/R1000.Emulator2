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
   TYP A-side mux+latch
   ====================

'''

from part import PartModel, PartFactory

class XMULT(PartFactory):
    ''' TYP A-side mux+latch '''

    def state(self, file):
        file.fmt('''
		|	uint64_t alat;
		|	uint64_t blat;
		|	unsigned src;
		|	uint64_t prod;
		|	uint64_t out;
		|''')

    def sensitive(self):
        yield "PIN_OE"
        # yield "BUS_DST_SENSITIVE()"
        yield "PIN_Q2.pos()"
        yield "PIN_Q3.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|#ifdef DO_DLY
		|	if (state->ctx.job == 2) {
		|		state->ctx.job = 0;
		|		BUS_P_Z();
		|	}
		|	if (state->ctx.job == 1) {
		|		state->ctx.job = 0;
		|		BUS_P_WRITE(state->out);
		|	}
		|#endif
		|	if (!PIN_OE=>) {
		|		unsigned dst;
		|		uint64_t out; 
		|		BUS_DST_READ(dst);
		|		switch(dst) {
		|		case 0: out = 0; break;
		|		case 1: out = state->prod << 32; BUS_P_WRITE(out); break;
		|		case 2: out = state->prod << 16; BUS_P_WRITE(out); break;
		|		case 3: out = state->prod <<  0; BUS_P_WRITE(out); break;
		|		}
		|		out ^= BUS_P_MASK;
		|#ifdef DO_DLY
		|		if (state->out != out) {
		|			state->ctx.job = 1;
		|			state->out = out;
		|			next_trigger(5, SC_NS);
		|		}
		|#else
		|		state->out = out;
		|		BUS_P_WRITE(state->out);
		|#endif
		|	} 
		|	if (PIN_OE.posedge()) {
		|#ifdef DO_DLY
		|		state->ctx.job = 2;
		|		next_trigger(5, SC_NS);
		|#else
		|		BUS_P_Z();
		|#endif
		|	}
		|	if (PIN_Q2.posedge()) {
		|		BUS_SRC_READ(state->src);
		|	}
		|	if (PIN_Q3.posedge()) {
		|		if (!PIN_START=> && !PIN_DGMD=>) {
		|			BUS_A_READ(state->alat);
		|			state->alat ^= BUS_A_MASK;
		|			BUS_B_READ(state->blat);
		|			state->blat ^= BUS_B_MASK;
		|		}
		|
		|		uint32_t a;
		|		switch (state->src >> 2) {
		|		case 0: a = (state->alat >> 48) & 0xffff; break;
		|		case 1: a = (state->alat >> 32) & 0xffff; break;
		|		case 2: a = (state->alat >> 16) & 0xffff; break;
		|		case 3: a = (state->alat >>  0) & 0xffff; break;
		|		}
		|		uint32_t b;
		|		switch (state->src & 3) {
		|		case 0: b = (state->blat >> 48) & 0xffff; break;
		|		case 1: b = (state->blat >> 32) & 0xffff; break;
		|		case 2: b = (state->blat >> 16) & 0xffff; break;
		|		case 3: b = (state->blat >>  0) & 0xffff; break;
		|		}
		|		state->prod = a * b;
		|	}
		|
		|	TRACE(
		|		<< " q2 " << PIN_Q2? << " q2^" << PIN_Q2.posedge()
		|		<< " q3 " << PIN_Q3? << " q3^" << PIN_Q3.posedge()
		|		<< " start " << PIN_START?
		|		// << " a " << BUS_A_TRACE()
		|		// << " b " << BUS_B_TRACE()
		|		<< " src " << BUS_SRC_TRACE()
		|		<< " oe " << PIN_OE?
		|		<< " dst " << BUS_DST_TRACE()
		|		<< " dgmd " << PIN_DGMD?
		|		<< std::hex
		|		<< " al " << state->alat
		|		<< " bl " << state->blat
		|		<< " ssrc " << state->src
		|		<< " prod " << state->prod
		|		<< " out " << state->out
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMULT", PartModel("XMULT", XMULT))
