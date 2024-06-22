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
   TYP/VAL ALU
   ===========

   The 74181 consists of four segments:

   1.  Calculate a function of two S-bits, A & B which we call C
   2.  Calculate a function of the two other S-bits, A & B which we call D
   3.  Carry-look-ahead-circuit which generates CO
   4.  Add C & D to Y but if M is high, supress the carry in the addition (=XOR)

   NB: The R1000 schematics mirrors the bit-order of the S bus
'''

from part import PartModel, PartFactory

class XALU(PartFactory):
    ''' TYP/VAL ALU '''

    autopin = True

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_CI"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned a, b, s, ci;
		|
		|	bool mag = PIN_MAG=>;
		|	bool m = PIN_M=>;
		|	ci = PIN_CI=>;
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_S_READ(s);
		|
		|	s ^= BUS_S_MASK;
		|
		|	uint64_t c;
		|	switch(s & 0x3) {
		|	case 0x0: c = a; break;
		|	case 0x1: c = a | b; break;
		|	case 0x2: c = a | (b^BUS_Y_MASK); break;
		|	case 0x3: c = BUS_Y_MASK; break;
		|	}
		|	c ^= BUS_Y_MASK;
		|
		|	uint64_t d;
		|	switch(s & 0xc) {
		|	case 0x0: d = 0; break;
		|	case 0x4: d = a & (b^BUS_Y_MASK); break;
		|	case 0x8: d = a & b; break;
		|	case 0xc: d = a; break;
		|	}
		|	d ^= BUS_Y_MASK;
		|
		|	uint64_t y;
		|	if (!mag) {
		|		// TYP board INC/DEC128
		|		y = (c & 0xff) + (d & 0xff) + ci;
		|		y &= 0xff;
		|		y ^= 0x80;
		|		if (a & 0x80)
		|			ci = 0;
		|		else
		|			ci = 0x100;
		|		y += (c & (~0xff)) + (d & (~0xff)) + ci;
		|	} else {
		|		y = c + d + ci;
		|	}
		|
		|	output.co = (y >> BUS_Y_WIDTH) & 1;
		|
		|	if (m) {
		|		y = c ^ d;
		|		if (!mag)
		|			y ^= 0x80;
		|	}
		|
		|	output.eq = 0;
		|	if (!(y & 0xff)) output.eq |= 1;
		|	if (!(y & 0xff00)) output.eq |= 2;
		|	if (!(y & 0xff0000)) output.eq |= 4;
		|	if (!(y & 0xff000000)) output.eq |= 8;
		|
		|	output.y = y ^= BUS_Y_MASK;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XALU32C", PartModel("XALU32C", XALU))
