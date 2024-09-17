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

class XICTR(PartFactory):
    ''' TYP A-side mux+latch '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned prescaler;
		|	uint16_t delay;
		|	uint16_t slice;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 1000) {
		|		output.sme = true;
		|		output.sen = true;
		|	}
		|
		|	if (PIN_Q2.posedge()) {
		|		if (output.sev && !output.ten) {
		|			output.sme = false;
		|		}
		|		if (PIN_CSLC=>) {
		|			output.sme = true;
		|		}
		|	}
		|
		|	if (PIN_Q4.posedge()) {
		|		state->prescaler++;
		|		output.ten = state->prescaler != 0xf;
		|		state->prescaler &= 0xf;
		|		if (!PIN_SCE=>) {
		|			if (PIN_ESLC=>)
		|				output.sen = false;
		|			if (PIN_DSLC=>)
		|				output.sen = true;
		|			if (PIN_EDLY=>)
		|				output.den = false;
		|			if (PIN_DDLY=>)
		|				output.den = true;
		|		}
		|
		|		output.sev = state->slice == 0xffff;
		|		if (!PIN_LDSL=>) {
		|			unsigned tmp;
		|			BUS_DT_READ(tmp);
		|			state->slice = tmp >> 16;
		|			TRACE(<< " LD " << std::hex << state->slice);
		|		} else 	if (!output.sen && !output.ten) {
		|			state->slice++;
		|		}
		|
		|		if (!PIN_LDDL=>) {
		|			unsigned tmp;
		|			BUS_DT_READ(tmp);
		|			state->delay = tmp;
		|		} else if (!output.den && !output.ten) {
		|			state->delay++;
		|		}
		|		output.dev = state->delay == 0xffff;
		|		TRACE(
		|			<< std::hex
		|			<< " slc " << state->slice
		|			<< " dly " << state->delay
		|			<< " sen " << output.sen
		|			<< " sev " << output.sev
		|			<< " ten " << output.ten
		|		);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XICTR", PartModel("XICTR", XICTR))
