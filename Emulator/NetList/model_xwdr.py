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
   Write Data Register
   ===================

'''

from part import PartModel, PartFactory

class XWDR(PartFactory):
    ''' Select next micro address '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t data;
		|	uint16_t parity;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool s0 = false, s1 = false, spill_d, spill_p;
		|	uint16_t diag = 0, tmp;	
		|
		|	if (PIN_CLK.posedge()) {
		|		s0 = s1 = PIN_SCLKEN=> && true && !PIN_LOADWDR=>;
		|
		|		if (s0 && s1) {
		|			BUS_DB_READ(state->data);
		|			state->data = ~state->data;
		|			tmp = 0x00;
		|			// .P2 and .P6 are swapped and patching DIPROC's table
		|			// is not enough
		|			state->parity = tmp & 0xdd;
		|			state->parity |= (tmp & 0x02) << 4;
		|			state->parity |= (tmp & 0x20) >> 4;
		|		} else if (s0) {
		|			diag = 0xff;
		|			// BUS_DIAG_READ(diag);
		|			spill_d = (state->data >> 32) & 1;
		|			state->data >>= 1;
		|			spill_p = state->parity & 1;
		|			state->parity >>= 1;
		|
		|			if (diag & 0x80)
		|				state->data |= (1ULL<<63);
		|			else
		|				state->data &= ~(1ULL<<63);
		|
		|			if (diag & 0x40)
		|				state->data |= (1ULL<<51);
		|			else
		|				state->data &= ~(1ULL<<51);
		|
		|			if (diag & 0x20)
		|				state->data |= (1ULL<<39);
		|			else
		|				state->data &= ~(1ULL<<39);
		|
		|			if (spill_d)
		|				state->parity |= (1<<7);
		|			else
		|				state->parity &= ~(1<<7);
		|
		|			if (diag & 0x10)
		|				state->parity |= (1<<3);
		|			else
		|				state->parity &= ~(1<<3);
		|
		|			if (spill_p)
		|				state->data |= (1ULL<<31);
		|			else
		|				state->data &= ~(1ULL<<31);
		|
		|			if (diag & 0x08)
		|				state->data |= (1ULL<<23);
		|			else
		|				state->data &= ~(1ULL<<23);
		|
		|			if (diag & 0x04)
		|				state->data |= (1ULL<<11);
		|			else
		|				state->data &= ~(1ULL<<11);
		|		} else if (s1) {
		|			std::cerr << "WDR shift left\\n";
		|		}
		|		output.qb = state->data;
		|		// .P2 and .P6 are swapped and patching DIPROC's tbl is not enough. 
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XWDR", PartModel("XWDR", XWDR))
