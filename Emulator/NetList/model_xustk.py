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
		|	uint16_t ram[16];
		|	uint16_t topu;
		|	uint16_t adr;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_QFOE"
        yield "PIN_QVOE"
        yield "PIN_QPOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = "?";
		|	bool stkclk = PIN_Q4.posedge() && !PIN_STKEN=>;
		|	bool uevent = PIN_UEVENT=>;
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
		|				BUS_BRNCH_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "0";
		|				break;
		|			case 1:
		|				BUS_DF_READ(state->topu);
		|				state->topu &= 0xffff;
		|				what = "1";
		|				break;
		|			case 2:
		|				BUS_CURU_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "2";
		|				break;
		|			case 3:
		|				BUS_CURU_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "3";
		|				break;
		|			}
		|		} else {
		|			what = "4";
		|			state->topu = state->ram[state->adr];
		|		}
		|		output.topu = state->topu ^ 0xffff;
		|		uint8_t par = odd_parity64(output.topu);
		|		output.qp = par;
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
		|		uint8_t parc, pari;
		|		BUS_DP_READ(pari);
		|		parc = odd_parity64(fiu);
		|		output.perr = parc != pari;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	output.z_qp = PIN_QPOE=>;
		|	if (!output.z_qf) {
		|		output.qf = output.topu;
		|		output.qf ^= 0xffff;
		|	}
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = output.topu;
		|		output.qv ^= BUS_QV_MASK;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XUSTK", PartModelDQ("XUSTK", XUSTK))
