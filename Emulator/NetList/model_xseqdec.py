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

from part import PartModel, PartFactory

class XSEQDEC(PartFactory):
    ''' SEQ Decode Ram '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t top[1<<10];
		|	uint32_t bot[1<<10];
		|	uint32_t reg, last, cbot, ctop;
		|	uint8_t sr[4];
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
		|#define PERMUTE(MACRO) \\
		|	do { \\
		|		MACRO(0, 0,  0, UADR_DEC0) \\
		|		MACRO(0, 1,  1, UADR_DEC1) \\
		|		MACRO(0, 2,  4, UADR_DEC4) \\
		|		MACRO(0, 3,  5, UADR_DEC5) \\
		|		MACRO(0, 4,  7, UADR_DEC7) \\
		|		MACRO(0, 5,  8, UADR_DEC8) \\
		|		MACRO(0, 6, 10, UADR_DEC10) \\
		|		MACRO(0, 7, 11, UADR_DEC11) \\
		|		MACRO(1, 0,  2, UADR_DEC2) \\
		|		MACRO(1, 1,  3, UADR_DEC3) \\
		|		MACRO(1, 2,  6, UADR_DEC6) \\
		|		MACRO(1, 3,  9, UADR_DEC9) \\
		|		MACRO(1, 4, 12, UADR_DEC12) \\
		|		MACRO(1, 5, 15, PARITY) \\
		|		MACRO(1, 6, 13, USES_TOS) \\
		|		MACRO(1, 7, 14, IBUFF_FILL) \\
		|		MACRO(2, 0, 28, UNUSED24) \\
		|		MACRO(2, 1, 29, UNUSED25) \\
		|		MACRO(2, 2, 30, UNUSED26) \\
		|		MACRO(2, 3, 18, CSA_VALID0) \\
		|		MACRO(2, 4, 19, CSA_VALID1) \\
		|		MACRO(2, 5, 20, CSA_VALID2) \\
		|		MACRO(2, 6, 16, CSA_FREE0) \\
		|		MACRO(2, 7, 17, CSA_FREE1) \\
		|		MACRO(3, 0, 31, UNUSED27) \\
		|		MACRO(3, 1, 21, MEM_STRT0) \\
		|		MACRO(3, 2, 22, MEM_STRT1) \\
		|		MACRO(3, 3, 23, MEM_STRT2) \\
		|		MACRO(3, 4, 24, CUR_CLASS0) \\
		|		MACRO(3, 5, 25, CUR_CLASS1) \\
		|		MACRO(3, 6, 26, CUR_CLASS2) \\
		|		MACRO(3, 7, 27, CUR_CLASS3) \\
		|	} while (0)
		|
		|#define TO_SR(srn, srb, regb, name) \\
		|	state->sr[srn] |= ((state->reg >> (31 - regb)) & 1) << (7 - srb);
		|
		|#define TO_REG(srn, srb, regb, name) \\
		|	state->reg |= ((state->sr[srn] >> (7 - srb)) & 1) << (31 - regb);
		|
		|	unsigned disp, dcnt, diag, tdec, par, mode, tmp, emac, icc;
		|
		|	BUS_DISP_READ(disp);
		|	BUS_DCNT_READ(dcnt);
		|	BUS_DIAG_READ(diag);
		|	BUS_ICC_READ(icc);
		|	BUS_MODE_READ(mode);
		|	BUS_EMAC_READ(emac);
		|
		|	tdec = state->last & 0xffffff0f;
		|	tdec |= icc << 4;
		|
		|	bool e_macro_pend = !(emac == BUS_EMAC_MASK);
		|	output.emp = e_macro_pend;
		|
		|	if (PIN_CLK.posedge()) {
		|		switch (mode) {
		|		case 3:
		|			state->reg = tdec;
		|			state->reg |= 0x0f;
		|			state->sr[0] = state->sr[1] = state->sr[2] = state->sr[3] = 0;
		|			PERMUTE(TO_SR);
		|			break;
		|		case 2:
		|			state->sr[0] <<= 1;
		|			state->sr[1] <<= 1;
		|			state->sr[2] <<= 1;
		|			state->sr[3] <<= 1;
		|			state->sr[0] |= 0;	// DIPROC ADDRESS
		|			state->sr[1] |= 0;
		|			state->sr[2] |= 1; 
		|			state->sr[3] |= 0;
		|			break;
		|		case 1:
		|			state->sr[0] >>= 1;
		|			state->sr[1] >>= 1;
		|			state->sr[2] >>= 1;
		|			state->sr[3] >>= 1;
		|			state->sr[0] |= ((diag >> 7) & 1) << 7;
		|			state->sr[1] |= ((diag >> 6) & 1) << 7;
		|			state->sr[2] |= ((diag >> 5) & 1) << 7;
		|			state->sr[3] |= ((diag >> 4) & 1) << 7;
		|			break;
		|		default:
		|			break;
		|		}
		|
		|		unsigned scan = 0;
		|		if (mode == 1 || mode == 2) {
		|			state->reg = 0;
		|			PERMUTE(TO_REG);
		|		}
		|		if (mode) {
		|			scan |= (state->sr[0] & 1) << 3;
		|			scan |= (state->sr[1] & 1) << 2;
		|			scan |= (state->sr[2] & 1) << 1;
		|			scan |= (state->sr[3] & 1) << 0;
		|			output.scan = scan;
		|		TRACE(
		|			<< " mode " << mode
		|			<< std::hex
		|			<< " diag " << diag
		|			<< " reg " << state->reg
		|			<< " sr " << (unsigned)state->sr[0]
		|			<< ", " << (unsigned)state->sr[1]
		|			<< ", " << (unsigned)state->sr[2]
		|			<< ", " << (unsigned)state->sr[3]
		|			<< " scan " << scan
		|		);
		|		}
		|	}
		|
		|	unsigned a = disp & ((dcnt << 8) | diag);
		|	a ^= 0xffff;
		|
		|	bool banksel = (state->sr[2] >> 7) & 1;
		|	output.bsel = banksel;
		|
		|	bool top = !banksel || (disp >> 10) != 0x3f;
		|
		|	uint32_t *ptr;
		|	if (top)
		|		ptr = &state->top[a >> 6];
		|	else
		|		ptr = &state->bot[a & 0x3ff];
		|
		|	state->last = 0;
		|	bool write_ccl = false;
		|	if (!PIN_DWOE && mode != 3) {
		|		state->last = state->reg;
		|		output.uad = state->reg >> 16;
		|		output.dec = state->reg >> 8;
		|		output.ccl = state->reg >> 4;
		|	} else {
		|		if (emac != BUS_EMAC_MASK) {
		|			unsigned uad = 0;
		|			if (!(emac & 0x80))
		|				uad = 0x009c;
		|			else if (!(emac & 0x40))
		|				uad = 0x0098;
		|			else if (!(emac & 0x20))
		|				uad = 0x0094;
		|			else if (!(emac & 0x10))
		|				uad = 0x0090;
		|			else if (!(emac & 0x08))
		|				uad = 0x008c;
		|			else if (!(emac & 0x04))
		|				uad = 0x0088;
		|			else if (!(emac & 0x02))
		|				uad = 0x0084;
		|			else if (!(emac & 0x01))
		|				uad = 0x0080;
		|			uad <<= 3;
		|			output.uad = uad;
		|			state->last &= 0x0000ffff;
		|			state->last |= uad << 16;
		|		} else {
		|			TRACE(" would " << std::hex << (*ptr >> 16));
		|			output.uad = (*ptr >> 16);
		|			output.dec = (*ptr >> 8);
		|			state->last &= 0x000000ff;
		|			state->last |= *ptr & 0xffffff00;
		|		}
		|		write_ccl = true;
		|	}
		|
		|	tmp = tdec >> 8;	// CUR_CLASS[0..3] not included in parity
		|	par = (tmp ^ (tmp >> 16)) & 0xffff;
		|	par = (par ^ (par >> 8)) & 0xff;
		|	par = (par ^ (par >> 4)) & 0xf;
		|	par = (par ^ (par >> 2)) & 0x3;
		|	par = (par ^ (par >> 1)) & 0x1;
		|	par ^= 1;
		|
		|	bool dec_cs = PIN_DGCS=>;
		|
		|	bool enuadr = !(e_macro_pend || !dec_cs);
		|
		|	output.dper = !(enuadr && par);
		|
		|	if (!PIN_WE=> && dec_cs && enuadr) {
		|		TRACE(<< " W " << std::hex << a << " " << state->reg);
		|		*ptr &= 0x000000f0;
		|		*ptr |= state->reg & 0xffffff0f;
		|	}
		|
		|	unsigned dsp = 0;
		|	if (!PIN_CDDG=>) {
		|		dsp = diag;
		|		dsp |= dcnt << 8;
		|	} else if (!PIN_IMX=>) {
		|		dsp = disp;
		|	} else {
		|		unsigned val;
		|		BUS_VAL_READ(val);
		|		dsp = val;
		|	}
		|	dsp ^= BUS_DSP_MASK;
		|
		|	if (PIN_TCLK.posedge())
		|		state->ctop = dsp;
		|	if (PIN_BCLK.posedge())
		|		state->cbot = dsp;
		|
		|	unsigned cur_instr;
		|	if (PIN_TMX) 
		|		cur_instr = state->cbot;
		|	else
		|		cur_instr = state->ctop;
		|
		|	output.dsp = cur_instr;
		|
		|	uint32_t *ciptr;
		|	if (cur_instr & 0xfc00 || !banksel)
		|		ciptr = &state->top[cur_instr >> 6];
		|	else
		|		ciptr = &state->bot[cur_instr & 0x3ff];
		|
		|	if (!PIN_WE=> && dec_cs) {
		|		*ciptr &= 0xffffff0f;
		|		*ciptr |= state->reg & 0x000000f0;
		|	}
		|	if (write_ccl) {
		|		uint ccls = (*ciptr >> 4) & 0xf;
		|		output.ccl = ccls;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQDEC", PartModel("XSEQDEC", XSEQDEC))
