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
   SEQ Decode Ram
   ==============

'''

from part import PartModelDQ, PartFactory

class XSEQDEC(PartFactory):
    ''' SEQ Decode Ram '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t top[1<<10];	// Z020
		|	uint32_t bot[1<<10];	// Z020
		|	uint32_t reg, last, cbot, ctop;
		|	unsigned prev_dsp;
		|	unsigned emac;
		|	bool topbot;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "BUS_DISP"
        yield "PIN_QVOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool clk = PIN_CLK.posedge();
		|
		|	unsigned disp;
		|	BUS_DISP_READ(disp);
		|
		|	if (clk) {
		|		BUS_EMAC_READ(state->emac);
		|		output.me = state->emac;
		|		output.emp = state->emac != BUS_EMAC_MASK;
		|	}
		|	if (output.emp) {
		|		unsigned uad = 0;
		|		if (!(state->emac & 0x40))
		|			uad = 0x009c;
		|		else if (!(state->emac & 0x20))
		|			uad = 0x0098;
		|		else if (!(state->emac & 0x10))
		|			uad = 0x0094;
		|		else if (!(state->emac & 0x08))
		|			uad = 0x0090;
		|		else if (!(state->emac & 0x04))
		|			uad = 0x008c;
		|		else if (!(state->emac & 0x02))
		|			uad = 0x0088;
		|		else if (!(state->emac & 0x01))
		|			uad = 0x0084;
		|		uad <<= 3;
		|		output.uad = uad;
		|		state->last = uad << 16;
		|	} else {
		|		unsigned a = disp;
		|		a ^= 0xffff;
		|		bool top = (disp >> 10) != 0x3f;
		|		uint32_t *ptr;
		|		if (top)
		|			ptr = &state->top[a >> 6];
		|		else
		|			ptr = &state->bot[a & 0x3ff];
		|		output.uad = (*ptr >> 16);
		|		output.dec = (*ptr >> 8);
		|		state->last = *ptr & 0xffffff00;
		|	}
		|
		|	if (clk) {
		|		unsigned tdec;
		|		tdec = state->last & 0xffffff0f;
		|		tdec |= output.ccl << 4;
		|		state->reg = tdec;
		|		state->reg |= 0x0f;
		|	}
		|
		|	unsigned dsp = 0;
		|	if (!PIN_IMX=>) {
		|		dsp = disp;
		|	} else {
		|		unsigned val;
		|		BUS_DV_READ(val);
		|		dsp = val;
		|	}
		|	dsp ^= BUS_DSP_MASK;
		|
		|	if (clk && !PIN_SCLKE=>) {
		|		bool gate = !(PIN_ILDRN=> && PIN_DISPA=>);
		|		if (gate && state->topbot)
		|			state->ctop = dsp;
		|		if (gate && !state->topbot)
		|			state->cbot = dsp;
		|	}
		|
		|	if (PIN_FLIP.posedge()) {
		|		state->topbot = !state->topbot;
		|	}
		|
		|	if (state->topbot) 
		|		output.dsp = state->cbot;
		|	else
		|		output.dsp = state->ctop;
		|
		|	if (state->prev_dsp != output.dsp) {
		|		uint8_t utrc[4];
		|		utrc[0] = UT_CURINS;
		|		utrc[1] = 0;
		|		utrc[2] = output.dsp >> 8;
		|		utrc[3] = output.dsp;
		|		microtrace(utrc, sizeof utrc);
		|		state->prev_dsp = output.dsp;
		|	}
		|
		|	uint32_t *ciptr;
		|	if (output.dsp & 0xfc00) {
		|		ciptr = &state->top[output.dsp >> 6];
		|	} else {
		|		ciptr = &state->bot[output.dsp & 0x3ff];
		|	}
		|
		|	output.ccl = (*ciptr >> 4) & 0xf;
		|
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = output.dsp ^ BUS_QV_MASK;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQDEC", PartModelDQ("XSEQDEC", XSEQDEC))
