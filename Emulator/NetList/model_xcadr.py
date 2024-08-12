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
   TV C-addr calculation
   =====================

'''

from part import PartModel, PartFactory

class XCADR(PartFactory):
    ''' TV C-addr calculation '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned csa_offset;
		|	unsigned topreg;
		|	unsigned botreg;
		|	bool csa_hit;
		|	bool csa_write;
		|''')

    def sensitive(self):
        yield "PIN_UCLK.pos()"
        yield "PIN_CCLK.pos()"
        yield "PIN_H2"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool uirsclk = PIN_UCLK.posedge();
		|
		|	unsigned uira, uirb, uirc;
		|	BUS_A_READ(uira);
		|	BUS_B_READ(uirb);
		|	BUS_C_READ(uirc);
		|
		|	bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|	bot_mux_sel = PIN_LBOT=>;
		|	add_mux_sel = PIN_LTOP=>;
		|	top_mux_sel = !(add_mux_sel && PIN_LPOP=>);
		|
		|	unsigned csmux3;
		|	BUS_CSAO_READ(csmux3);
		|	csmux3 ^= 0xf;
		|
		|	unsigned csmux0;
		|	if (add_mux_sel)
		|		csmux0 = state->botreg;
		|	else
		|		csmux0 = state->topreg;
		|
		|	unsigned csalu0 = csmux3 + csmux0 + 1;
		|
		|	if (uirsclk) {
		|		state->csa_offset = csmux3;
		|	}
		|	if (PIN_CCLK.posedge()) {
		|		if (!bot_mux_sel)
		|			state->botreg = csalu0;
		|		if (top_mux_sel)
		|			state->topreg = csalu0;
		|	}
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
		|		output.clh = state->csa_hit;
		|		output.cwe = !(state->csa_hit || state->csa_write);
		|	}
		|
		|	unsigned cadr = 0, frm, loop;
		|	BUS_FRM_READ(frm);
		|	BUS_LOOP_READ(loop);
		|	if (uirc <= 0x1f) {
		|		// FRAME:REG
		|		cadr |= uirc & 0x1f;
		|		cadr |= frm << 5;
		|	} else if (uirc <= 0x27) {
		|		// 0x20 = TOP-1
		|		// …
		|		// 0x27 = TOP-8
		|		cadr = (state->topreg + (uirc & 0x7) + 1) & 0xf;
		|	} else if (uirc == 0x28) {
		|		// 0x28 LOOP COUNTER (RF write disabled)
		|	} else if (uirc == 0x29 && output.cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		unsigned sum = state->botreg + state->csa_offset + 1;
		|		cadr |= sum & 0xf;
		|	} else if (uirc == 0x29 && !output.cwe) {
		|		// 0x29 DEFAULT (RF write disabled)
		|		cadr |= uirc & 0x1f;
		|		cadr |= frm << 5;
		|	} else if (uirc <= 0x2b) {
		|		// 0x2a BOT
		|		// 0x2b BOT-1
		|		cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|		cadr |= (state->botreg + (uirc & 1)) & 0xf;
		|	} else if (uirc == 0x2c) {
		|		// 0x28 = LOOP_REG
		|		cadr = loop;
		|	} else if (uirc == 0x2d) {
		|		// 0x2d SPARE
		|		assert (uirc != 0x2d);
		|	} else if (uirc <= 0x2f) {
		|		// 0x2e = TOP+1
		|		// 0x2f = TOP
		|		cadr = (state->topreg + (uirc & 0x1) + 0xf) & 0xf;
		|	} else if (uirc <= 0x3f) {
		|		// GP[0…F]
		|		cadr |= 0x10 | (uirc & 0x0f);
		|	} else {
		|		assert(uirc <= 0x3f);
		|	}
		|
		|	output.wen = (uirc == 0x28 || uirc == 0x29); // LOOP_CNT + DEFAULT
		|	if (output.cwe && uirc != 0x28)
		|		output.wen = !output.wen;
		|
		|	unsigned aadr = 0, badr = 0;
		|	if (PIN_H2=>) {
		|		aadr = cadr;
		|		badr = cadr;
		|	} else {
		|		if (PIN_ALOOP=>) {
		|			aadr = loop;
		|		} else if (uira <= 0x1f) {
		|			aadr = frm << 5;
		|			aadr |= uira & 0x1f;
		|		} else if (uira <= 0x2f) {
		|			aadr |= atos & 0xf;
		|		} else {
		|			aadr |= uira & 0x1f;
		|		}
		|
		|		if (PIN_BLOOP=>) {
		|			badr = loop;
		|		} else if (uirb <= 0x1f) {
		|			badr = frm << 5;
		|			badr |= uirb & 0x1f;
		|		} else if (uirb <= 0x27) {
		|			badr |= btos & 0xf;
		|		} else if (uirb <= 0x2b) {
		|			badr |= csa & 0xf;
		|		} else if (uirb <= 0x2f) {
		|			badr |= btos & 0xf;
		|		} else {
		|			badr |= uirb & 0x1f;
		|		}
		|	}
		|	output.aadr = aadr;
		|	output.badr = badr;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCADR", PartModel("XCADR", XCADR))
