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

from part import PartModelDQ, PartFactory

class XICTR(PartFactory):
    ''' TYP A-side mux+latch '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned prescaler;
		|	uint16_t delay, slice;
		|	bool slice_ev, delay_ev;
		|	bool sen, den, ten;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_QTOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 1000) {
		|		output.sme = true;
		|		state->sen = true;
		|		output.dme = true;
		|		state->den = true;
		|	}
		|
		|	if (PIN_Q2.posedge()) {
		|		unsigned rnd;
		|		BUS_RND_READ(rnd);
		|		if (state->slice_ev && !state->ten) {
		|			output.sme = false;
		|		}
		|		if (rnd == 0x0a) {
		|			output.sme = true;
		|		}
		|		if (state->delay_ev && !state->ten) {
		|			output.dme = false;
		|		}
		|		if (rnd == 0x0b) {
		|			output.dme = true;
		|		}
		|	}
		|
		|	if (PIN_Q4.posedge()) {
		|		unsigned rnd;
		|		BUS_RND_READ(rnd);
		|		state->prescaler++;
		|		state->ten = state->prescaler != 0xf;
		|		state->prescaler &= 0xf;
		|		if (!PIN_SCE=>) {
		|			if (rnd == 0x0c) {
		|				state->sen = false;
		|			}
		|			if (rnd == 0x0d) {
		|				assert(rnd == 0x0d);
		|				state->sen = true;
		|			}
		|			if (rnd == 0x0e) {
		|				assert(rnd == 0x0e);
		|				state->den = false;
		|			}
		|			if (rnd == 0x0f) {
		|				assert(rnd == 0x0f);
		|				state->den = true;
		|			}
		|		}
		|
		|		state->slice_ev= state->slice == 0xffff;
		|		// if (!PIN_LDSL=>) {
		|		if (rnd == 0x06) {
		|			unsigned tmp;
		|			BUS_DT_READ(tmp);
		|			state->slice = tmp >> 16;
		|			TRACE(<< " LD " << std::hex << state->slice);
		|		} else 	if (!state->sen && !state->ten) {
		|			state->slice++;
		|		}
		|
		|		state->delay_ev= state->delay == 0xffff;
		|		// if (!PIN_LDDL=>) {
		|		if (rnd == 0x07) {
		|			unsigned tmp;
		|			BUS_DT_READ(tmp);
		|			state->delay = tmp;
		|		} else if (!state->den && !state->ten) {
		|			state->delay++;
		|		}
		|	}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		output.qt = ((unsigned)(state->slice) << 16) | state->delay;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XICTR", PartModelDQ("XICTR", XICTR))
