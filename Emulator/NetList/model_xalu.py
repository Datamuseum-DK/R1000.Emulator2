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
		|	struct f181 f181;
		|
		|	BUS_A_READ(f181.a);
		|	BUS_B_READ(f181.b);
		|	BUS_S_READ(f181.ctl);
		|	f181.ci = PIN_CI=>;
		|	f181.ctl |= PIN_MAG=> << 5;
		|	f181.ctl |= PIN_M=> << 4;
		|
		|	f181_alu(&f181);
		|	output.co = f181.co;
		|	output.eq = 0;
		|	if (!(f181.o & 0xff)) output.eq |= 1;
		|	if (!(f181.o & 0xff00)) output.eq |= 2;
		|	if (!(f181.o & 0xff0000)) output.eq |= 4;
		|	if (!(f181.o & 0xff000000)) output.eq |= 8;
		|
		|	output.y = f181.o ^= BUS_Y_MASK;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XALU32C", PartModel("XALU32C", XALU))
