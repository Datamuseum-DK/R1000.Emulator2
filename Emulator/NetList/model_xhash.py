#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   MEM32 HASH generator
   ====================

'''

from part import PartModel, PartFactory

class XHASH(PartFactory):

    ''' MEM32 HASH generator '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned sr;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "BUS_TRC_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t a;
		|	uint32_t s, hash = 0, m, nxt = state->sr;
		|
		|	if (PIN_Q4.posedge()) {
		|		nxt = state->sr;
		|		BUS_M_READ(m);
		|		switch (m) {
		|		case 3:
		|			BUS_S_READ(s);
		|			BUS_A_READ(a);
		|#define GBIT(fld,bit,width) ((fld >> (width - (bit + 1))) & 1)
		|			if (GBIT(s, 1, BUS_S_WIDTH) ^
		|			    GBIT(a, 12, BUS_A_WIDTH) ^
		|			    GBIT(a, 49, BUS_A_WIDTH))
		|				hash |= 1<<11;
		|			if (GBIT(a, 40, BUS_A_WIDTH) ^ GBIT(a, 13, BUS_A_WIDTH))
		|				hash |= 1<<10;
		|			if (GBIT(a, 41, BUS_A_WIDTH) ^ GBIT(a, 14, BUS_A_WIDTH))
		|				hash |= 1<<9;
		|			if (GBIT(a, 42, BUS_A_WIDTH) ^ GBIT(a, 15, BUS_A_WIDTH))
		|				hash |= 1<<8;
		|			if (GBIT(a, 39, BUS_A_WIDTH) ^ GBIT(a, 16, BUS_A_WIDTH))
		|				hash |= 1<<7;
		|			if (GBIT(a, 43, BUS_A_WIDTH) ^ GBIT(a, 17, BUS_A_WIDTH))
		|				hash |= 1<<6;
		|			if (GBIT(a, 47, BUS_A_WIDTH) ^ GBIT(a, 18, BUS_A_WIDTH))
		|				hash |= 1<<5;
		|			if (GBIT(a, 46, BUS_A_WIDTH) ^ GBIT(a, 19, BUS_A_WIDTH))
		|				hash |= 1<<4;
		|			if (GBIT(a, 45, BUS_A_WIDTH) ^ GBIT(a, 20, BUS_A_WIDTH))
		|				hash |= 1<<3;
		|			if (GBIT(a, 44, BUS_A_WIDTH) ^ GBIT(a, 21, BUS_A_WIDTH))
		|				hash |= 1<<2;
		|			if (GBIT(a, 50, BUS_A_WIDTH) ^ GBIT(s, 0, BUS_S_WIDTH))
		|				hash |= 1<<1;
		|			if (GBIT(a, 48, BUS_A_WIDTH) ^ GBIT(s, 2, BUS_S_WIDTH))
		|				hash |= 1<<0;
		|	
		|			unsigned p;
		|		
		|			if (PIN_TE=>) {
		|				BUS_T_READ(p);
		|			} else {
		|				p = (a >> BUS_A_LSB(27)) & 0xf;
		|			}
		|			nxt = hash | (p << 12);
		|			break;
		|		case 2:
		|			nxt = state->sr >> 1;
		|			nxt |= PIN_R=> << 15;
		|			break;
		|		case 1:
		|			nxt = state->sr << 1;
		|			break;
		|		default:
		|			break;
		|		}
		|	}
		|
		|	unsigned btrc;
		|	BUS_TRC_READ(btrc);
		|	output.tag = ((nxt & btrc) ^ 0xfff) << 2;
		|
		|	state->sr = nxt;
		|
		|	output.p = state->sr >> 12;
		|	output.l = state->sr & 0xfff;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XHASH", PartModel("XHASH", XHASH))
