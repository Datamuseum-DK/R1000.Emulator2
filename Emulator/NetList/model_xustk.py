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
   Micro Stack
   ===========

'''

from part import PartModelDQ, PartFactory

class XUSTK(PartFactory):
    ''' Micro Stack '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned nxtuadr;	// Z029
		|	uint16_t ram[16];
		|	uint16_t topu;
		|	uint16_t adr;
		|	unsigned fiu;
		|	unsigned other;
		|	unsigned late_u;
		|	unsigned prev;
		|	unsigned uei;
		|	unsigned uev;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_QFOE"
        yield "PIN_QVOE"

        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LCLK.pos()"
        yield "PIN_ACLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = "?";
		|	bool stkclk = PIN_Q4.posedge() && !PIN_STKEN=>;
		|	bool uevent = output.u_event;
		|
		|	bool xwrite;
		|	bool pop;
		|	bool stkcnt_ena;
		|	bool stkinpsel_0;
		|	bool stkinpsel_1;
		|	if (uevent) {
		|		xwrite = true;
		|		pop = true;
		|		stkinpsel_0 = true;
		|		stkinpsel_1 = true;
		|	} else if (!PIN_PUSH=>) {
		|		xwrite = true;
		|		pop = false;
		|		stkinpsel_0 = !PIN_PUSHBR=>;
		|		stkinpsel_1 = !PIN_BADHINT=>;
		|	} else {
		|		xwrite = !PIN_PUSHRND=>;
		|		pop = !!(PIN_RETURN=> || PIN_POPRND=>);
		|		stkinpsel_0 = false;
		|		stkinpsel_1 = true;
		|	}
		|	stkcnt_ena = !(xwrite || pop);
		|	unsigned stkinpsel = 0;
		|	if (stkinpsel_0) stkinpsel |= 2;
		|	if (stkinpsel_1) stkinpsel |= 1;
		|
		|	if (stkclk && !stkcnt_ena) {
		|		if (PIN_H2 && xwrite) {
		|			switch(stkinpsel) {
		|			case 0:
		|				BUS_BRN_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				what = "0";
		|				break;
		|			case 1:
		|				BUS_DF_READ(state->topu);
		|				state->topu &= 0xffff;
		|				what = "1";
		|				break;
		|			case 2:
		|				BUS_CUR_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= 0xffff;;
		|				what = "2";
		|				break;
		|			case 3:
		|				BUS_CUR_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				what = "3";
		|				break;
		|			}
		|		} else {
		|			what = "4";
		|			state->topu = state->ram[state->adr];
		|		}
		|		output.svlat = !((state->topu >> 14) & 0x1);
		|	}
		|	if (PIN_Q2.posedge()) {
		|		state->ram[(state->adr + 1) & 0xf] = state->topu;
		|	}
		|	if (stkclk) {
		|		if (PIN_CSR=> && PIN_STOP=>) {
		|			state->adr = xwrite;
		|		} else if (!stkcnt_ena) {
		|			if (xwrite) {
		|				state->adr = (state->adr + 1) & 0xf;
		|			} else {
		|				state->adr = (state->adr + 0xf) & 0xf;
		|			}
		|		}
		|		output.ssz = state->adr == 0;
		|	}
		|
		|	if (PIN_LCLK.posedge()) {
		|		uint64_t fiu;
		|		BUS_DF_READ(fiu);
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = state->topu ^ 0xffff;
		|		output.qf ^= 0xffff;
		|	}
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = state->topu ^ 0xffff;
		|		output.qv ^= BUS_QV_MASK;
		|	}
		|
		|''')

        file.fmt('''
		|	unsigned data = 0, sel;
		|	bool macro_hic = true;
		|	bool u_event = true;
		|
		|	if (PIN_FIU_CLK.posedge()) {
		|		BUS_DF_READ(state->fiu);
		|		state->fiu &= 0x3fff;
		|	}	
		|
		|	if (PIN_LCLK.posedge()) {
		|		BUS_LATE_READ(state->late_u);
		|		sel = 0;
		|		if (!PIN_U_MUX_SEL) sel |= 4;
		|		if (PIN_G_SEL0) sel |= 2;
		|		if (PIN_G_SEL1) sel |= 1;
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 2:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		case 3:
		|		case 4:
		|			BUS_CUR_READ(data);
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|		state->other = data;
		|	}
		|
		|	if (!PIN_DV_U) {
		|		data = state->nxtuadr;
		|	} else if (PIN_BAD_HINT=>) {
		|		data = state->other;
		|	} else if (PIN_LMAC=>) {
		|		// Not tested by expmon_test_seq ?
		|		data = state->late_u << 3;
		|		data ^= (7 << 3);
		|		data |= 0x0140;
		|		macro_hic = false;
		|	} else if (state->uei != 0) {
		|		data = state->uev;
		|		data <<= 3;
		|		data |= 0x0180;
		|		u_event = false;
		|	} else {
		|		sel = 0;
		|		if (PIN_U_MUX_SEL) sel |= 4;
		|		if (PIN_G_SEL0) sel |= 2;
		|		if (PIN_G_SEL1) sel |= 1;
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 2:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		case 3:
		|		case 4:
		|			BUS_CUR_READ(data);
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|	}
		|	if (PIN_Q1not.posedge()) {
		|
		|		uint8_t utrc[2];
		|		utrc[0] = UT_UADR;
		|		utrc[0] |= (data >> 8) & 0x3f;
		|		utrc[1] = data & 0xff;
		|		microtrace(utrc, sizeof utrc);
		|
		|		output.nu = data;
		|	}
		|
		|	output.macro_hic = macro_hic;
		|	output.u_event = !u_event;
		|	output.u_eventnot = u_event;
		|
		|	if (PIN_ACLK.posedge()) {
		|		BUS_UEI_READ(state->uei);
		|		state->uei <<= 1;
		|		state->uei |= 1;
		|		state->uei ^= 0xffff;
		|		state->uev = 16 - fls(state->uei);
		|		output.uevp = state->uei == 0;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XUSTK", PartModelDQ("XUSTK", XUSTK))
