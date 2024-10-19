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
   SEQ Instruction buffer
   ======================

'''

from part import PartModel, PartFactory

class XSEQIBUF(PartFactory):
    ''' SEQ Instruction buffer '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t top[1<<10];	// Z020
		|	uint32_t bot[1<<10];	// Z020
		|	uint32_t reg, last, cbot, ctop;
		|	unsigned prev_dsp;
		|	unsigned emac;
		|	unsigned curins;
		|	bool topbot;
		|
		|	uint64_t typ, val;
		|	unsigned word;
		|	unsigned mpc;
		|	unsigned curr_lex;
		|	unsigned retrn_pc_ofs;
		|	unsigned boff;
		|''')

    def sensitive(self):
        yield "PIN_ACLK.pos()"
        yield "PIN_BCLK.pos()"
        yield "PIN_CLCLK.pos()"
        # yield "PIN_CNDLD"		# BCLK
        # yield "PIN_DISPA"		# ACLK
        # yield "BUS_EMAC"		# ACLK
        yield "PIN_FLIP.pos()"
        yield "PIN_ICLK.pos()"
        # yield "PIN_ILDRN"		# ACLK
        # yield "PIN_IMX"		# ACLK
        yield "BUS_IRD"
        yield "BUS_LAUIR"
        yield "PIN_LINC"
        # yield "PIN_MD0"		# BCLK
        yield "PIN_MIBMT"
        yield "PIN_MUX"
        yield "PIN_QBOE"
        yield "PIN_QVOE"
        yield "BUS_RASEL"
        yield "PIN_RCLK.pos()"
        # yield "PIN_RND1"		# BCLK
        yield "PIN_SCLKE"
        # yield "BUS_TYP"		# ICLK
        yield "BUS_URAND"
        yield "BUS_VAL"
        yield "PIN_WDISP"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_ICLK.posedge()) {
		|		BUS_TYP_READ(state->typ);
		|		BUS_VAL_READ(state->val);
		|	} 
		|
		|	unsigned macro_pc_ofs = state->mpc;
		|
		|	if (PIN_RCLK.posedge()) {
		|		state->retrn_pc_ofs = state->mpc;
		|	}
		|
		|	bool wdisp = PIN_WDISP;
		|	bool mibmt = PIN_MIBMT;
		|	bool oper;
		|	unsigned a;
		|	if (!wdisp && !mibmt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!wdisp && mibmt) {
		|		a = output.disp;
		|		oper = false;
		|	} else if (wdisp && !mibmt) {
		|		a = state->curins;
		|		oper = true;
		|	} else {
		|		a = state->curins;
		|		oper = true;
		|	}
		|	a &= 0x7ff;
		|	if (a & 0x400)
		|		a |= 0x7800;
		|	a ^= 0x7fff;
		|	unsigned b = macro_pc_ofs & 0x7fff;
		|	if (oper) {
		|		if (wdisp)
		|			a += 1;
		|		a &= 0x7fff;
		|		state->boff = a + b;
		|	} else {
		|		if (!wdisp)
		|			a += 1;
		|		state->boff = b - a;
		|	}
		|	state->boff &= 0x7fff;
		|	output.bridx = state->boff & 7;
		|
		|	if (PIN_BCLK.posedge()) {
		|		unsigned mode = 0;
		|		unsigned u = 0;
		|		if (PIN_CNDLD=>) u |= 1;
		|		if (PIN_WDISP=>) u |= 2;
		|		switch (u) {
		|		case 0: mode = 1; break;
		|		case 1: mode = 1; break;
		|		case 3: mode = 0; break;
		|		case 2:
		|			if (PIN_MD0=>) mode |= 2;
		|			if (PIN_RND1=>) mode |= 1;
		|			break;
		|		}
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			if (!PIN_MUX=>) {
		|				BUS_VAL_READ(tmp);
		|				state->word = (tmp >> 4) & 7;
		|				state->mpc = (tmp >> 4) & 0x7fff;
		|			} else {
		|				state->mpc = state->boff;
		|				state->word = state->boff & 7;
		|			}
		|		} else if (mode == 2) {
		|			state->mpc += 1;
		|			state->word += 1;
		|			if (state->word == 0x8)
		|				state->word = 0;
		|		} else if (mode == 1) {
		|			state->mpc -= 1;
		|			if (state->word == 0x0)
		|				state->word = 7;
		|			else
		|				state->word -= 1;
		|		}
		|	}
		|
		|	unsigned rand;
		|	BUS_URAND_READ(rand);
		|	switch (rand & 3) {
		|	case 3:	output.coff = state->retrn_pc_ofs; break;
		|	case 2: output.coff = state->boff; break;
		|	case 1: output.coff = state->mpc; break;
		|	case 0: output.coff = state->boff; break;
		|	}
		|	output.coff ^= BUS_COFF_MASK;
		|
		|	unsigned disp = output.disp;
		|
		|	output.empty = state->word != 0;
		|
		|	if (state->word == 7)
		|		output.disp = state->typ >> 48;
		|	else if (state->word == 6)
		|		output.disp = state->typ >> 32;
		|	else if (state->word == 5)
		|		output.disp = state->typ >> 16;
		|	else if (state->word == 4)
		|		output.disp = state->typ >> 0;
		|	else if (state->word == 3)
		|		output.disp = state->val >> 48;
		|	else if (state->word == 2)
		|		output.disp = state->val >> 32;
		|	else if (state->word == 1)
		|		output.disp = state->val >> 16;
		|	else if (state->word == 0)
		|		output.disp = state->val >> 0;
		|	else
		|		output.disp = 0xffff;
		|	output.disp &= 0xffff;
		|
		|	unsigned val, iclex;
		|
		|	BUS_VAL_READ(val);
		|	iclex = (val & 0xf) + 1;
		|
		|	if (PIN_CLCLK.posedge()) {
		|		state->curr_lex = val & 0xf;
		|		state->curr_lex ^= 0xf;
		|	}
		|	unsigned sel, res_addr = 0;
		|	BUS_RASEL_READ(sel);
		|	switch (sel) {
		|	case 0:
		|		if (PIN_LAUIR0=> && PIN_LAUIR1=>)
		|			res_addr = 0xe;
		|		else
		|			res_addr = 0xf;
		|		break;
		|	case 1:
		|		res_addr = (output.disp >> 9) & 0xf;
		|		break;
		|	case 2:
		|		res_addr = iclex;
		|		break;
		|	case 3:
		|		res_addr = state->curr_lex ^ 0xf;
		|		break;
		|	default:
		|		assert(sel < 4);
		|	}
		|	output.radr = res_addr;
		|	if (PIN_LINC=>) {
		|		output.icond = true;
		|		output.sext = true;
		|	} else {
		|		output.icond = !(res_addr == 0xf);
		|		output.sext = !((res_addr > 0xd));
		|	}		
		|
		|	output.z_qb = PIN_QBOE=>;
		|	if (!output.z_qb) {
		|		unsigned ird;
		|		BUS_IRD_READ(ird);
		|		if (ird == 2) {
		|			output.qb = output.disp;
		|		} else {
		|			output.qb = (output.coff << 4) & BUS_QB_MASK;
		|			output.qb |= (state->curr_lex & 0xf);
		|			output.qb ^= BUS_QB_MASK;
		|		}
		|	}
		|
		|	bool aclk = PIN_ACLK.posedge();
		|
		|	if (aclk) {
		|		BUS_EMAC_READ(state->emac);
		|		output.me = state->emac;
		|		output.emp = state->emac != BUS_EMAC_MASK;
		|	}
		|	if (state->emac != BUS_EMAC_MASK) {
		|		unsigned uad = 0;
		|		if (!(state->emac & 0x40))
		|			uad = 0x04e0;
		|		else if (!(state->emac & 0x20))
		|			uad = 0x04c0;
		|		else if (!(state->emac & 0x10))
		|			uad = 0x04a0;
		|		else if (!(state->emac & 0x08))
		|			uad = 0x0480;
		|		else if (!(state->emac & 0x04))
		|			uad = 0x0460;
		|		else if (!(state->emac & 0x02))
		|			uad = 0x0440;
		|		else if (!(state->emac & 0x01))
		|			uad = 0x0420;
		|		output.uad = uad;
		|		state->last = uad << 16;
		|	} else {
		|		unsigned ai = disp;
		|		ai ^= 0xffff;
		|		bool top = (disp >> 10) != 0x3f;
		|		uint32_t *ptr;
		|		if (top)
		|			ptr = &state->top[ai >> 6];
		|		else
		|			ptr = &state->bot[ai & 0x3ff];
		|		output.uad = (*ptr >> 16);
		|		output.dec = (*ptr >> 8);
		|		state->last = *ptr & 0xffffff00;
		|	}
		|
		|	if (aclk) {
		|		unsigned tdec;
		|		tdec = state->last & 0xffffff0f;
		|		tdec |= output.ccl << 4;
		|		state->reg = tdec;
		|		state->reg |= 0x0f;
		|	}
		|
		|	if (aclk && !PIN_SCLKE=>) {
		|		unsigned dsp = 0;
		|		if (!PIN_IMX=>) {
		|			dsp = disp;
		|		} else {
		|			uint64_t tval;
		|			BUS_VAL_READ(tval);
		|			dsp = tval & 0xffff;
		|		}
		|		dsp ^= BUS_DSP_MASK;
		|
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
		|		state->curins = state->cbot;
		|	else
		|		state->curins = state->ctop;
		|
		|	if (state->prev_dsp != state->curins) {
		|		uint8_t utrc[4];
		|		utrc[0] = UT_CURINS;
		|		utrc[1] = 0;
		|		utrc[2] = state->curins >> 8;
		|		utrc[3] = state->curins;
		|		microtrace(utrc, sizeof utrc);
		|		state->prev_dsp = state->curins;
		|	}
		|
		|	uint32_t *ciptr;
		|	if (state->curins & 0xfc00) {
		|		ciptr = &state->top[state->curins >> 6];
		|	} else {
		|		ciptr = &state->bot[state->curins & 0x3ff];
		|	}
		|
		|	output.ccl = (*ciptr >> 4) & 0xf;
		|
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = state->curins ^ BUS_QV_MASK;
		|	}
		|	output.dsp = state->curins;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQIBUF", PartModel("XSEQIBUF", XSEQIBUF))
