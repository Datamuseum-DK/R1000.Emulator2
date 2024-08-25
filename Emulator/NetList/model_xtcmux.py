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
   TYP C-bus mux
   =============

'''

from part import PartModel, PartFactory

class XTCMUX(PartFactory):
    ''' TYP C-bus mux '''

    autopin = True

    def state(self, file):
 
        file.fmt('''
		|	uint64_t aram[1<<BUS_A_WIDTH];
		|	uint64_t c, wdr;
		|''')

    def sensitive(self):
        yield "PIN_CLK.neg()"
        yield "PIN_Q4.pos()"
        yield "PIN_WE.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t c = 0;
		|	uint64_t fiu = 0, alu = 0;
		|	bool fiu_valid = false, alu_valid = false;
		|	bool fiu0, fiu1;
		|	bool chi = false;
		|	bool clo = false;
		|
		|	if (PIN_OE=> || PIN_WE.posedge()) {
		|		if (!PIN_DGCM=>) {
		|			fiu0 = true;
		|			fiu1 = true;
		|		} else {
		|			bool c_source = PIN_CSRC=>;
		|			fiu0 = c_source;
		|			fiu1 = c_source == PIN_CSPL=>;
		|		}
		|
		|		bool sel = PIN_SEL=>;
		|
		|		if (!fiu0) {
		|			BUS_FIU_READ(fiu);
		|			fiu ^= BUS_FIU_MASK;
		|			fiu_valid = true;
		|			c |= fiu & 0xffffffff00000000ULL;
		|			chi = true;
		|		} else {
		|			if (sel) {
		|				c |= state->wdr & 0xffffffff00000000ULL;
		|			} else {
		|				BUS_ALU_READ(alu);
		|				alu_valid = true;
		|				c |= alu & 0xffffffff00000000ULL;
		|			}
		|			chi = true;
		|		}
		|		if (!fiu1) {
		|			if (!fiu_valid) {
		|				BUS_FIU_READ(fiu);
		|				fiu ^= BUS_FIU_MASK;
		|			}
		|			c |= fiu & 0xffffffffULL;
		|			clo = true;
		|		} else {
		|			if (sel) {
		|				c |= state->wdr & 0xffffffffULL;
		|			} else {
		|				if (!alu_valid)
		|					BUS_ALU_READ(alu);
		|				c |= alu & 0xffffffffULL;
		|			}
		|			clo = true;
		|		}
		|		if (chi && !clo)
		|			c |= 0xffffffff;
		|		if (!chi && clo)
		|			c |= 0xffffffffULL << 32;
		|
		|		if (PIN_WE.posedge()) {
		|			unsigned adr;
		|			BUS_A_READ(adr);
		|			state->aram[adr] = c;
		|		}
		|	}
		|	if (!PIN_OE=>) {
		|		unsigned adr;
		|		BUS_A_READ(adr);
		|		output.c = state->aram[adr];
		| 	} else {
		|		output.c = c;
		|	}
		|	if (PIN_Q4.posedge() && PIN_SCLKE=> && !PIN_LDWDR=>) {
		|		BUS_DTY_READ(state->wdr);
		|		state->wdr ^= BUS_DTY_MASK;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCMUX", PartModel("XTCMUX", XTCMUX))
