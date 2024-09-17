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
		|	uint64_t typ, val;
		|	unsigned word;
		|	unsigned mpc;
		|	unsigned curr_lex;
		|	unsigned retrn_pc_ofs;
		|	unsigned boff;
		|''')

    def xsensitive(self):
        yield "PIN_ICLK.pos()"
        yield "PIN_BCLK.pos()"
        yield "PIN_WDISP"
        yield "PIN_MIBMT"
        yield "BUS_CURI"
        yield "BUS_URAND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_ICLK.posedge()) {
		|		BUS_TYP_READ(state->typ);
		|		BUS_VAL_READ(state->val);
		|	} 
		|{
		|	unsigned boff = 0;
		|	bool wdisp, mibmt, oper;
		|	unsigned macro_pc_ofs = state->mpc;
		|	unsigned a, b;
		|
		|	if (PIN_RCLK.posedge()) {
		|		state->retrn_pc_ofs = state->mpc;
		|	}
		|
		|	wdisp = PIN_WDISP;
		|	mibmt = PIN_MIBMT;
		|	b = macro_pc_ofs;
		|	if (!wdisp && !mibmt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!wdisp && mibmt) {
		|		a = output.disp;
		|		oper = false;
		|	} else if (wdisp && !mibmt) {
		|		BUS_CURI_READ(a);
		|		a |= 0xf800;
		|		oper = true;
		|	} else {
		|		BUS_CURI_READ(a);
		|		a |= 0xf800;
		|		oper = true;
		|	}
		|	a &= 0x7ff;
		|	if (a & 0x400)
		|		a |= 0x7800;
		|	a ^= 0x7fff;
		|	b &= 0x7fff;
		|	if (oper) {
		|		if (wdisp)
		|			a += 1;
		|		a &= 0x7fff;
		|		boff = a + b;
		|	} else {
		|		if (!wdisp)
		|			a += 1;
		|		boff = b - a;
		|	}
		|	boff &= 0x7fff;
		|	state->boff = boff;
		|	output.bridx = boff & 7;
		|}
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
		|{
		|	unsigned rand, coff;
		|	BUS_URAND_READ(rand);
		|	switch (rand & 3) {
		|	case 3:	coff = state->retrn_pc_ofs; break;
		|	case 2: coff = state->boff; break;
		|	case 1: coff = state->mpc; break;
		|	case 0: coff = state->boff; break;
		|	}
		|	coff ^= BUS_COFF_MASK;
		|	output.coff = coff;
		|}
		|
		|	output.emp = state->word != 0;
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
		|if (1) {
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
		|}
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
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQIBUF", PartModel("XSEQIBUF", XSEQIBUF))
