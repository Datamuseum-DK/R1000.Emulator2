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
   SEQ Scavenger
   =============

'''

from part import PartModelDQ, PartFactory

class XSCAV(PartFactory):
    ''' SEQ Scavenger '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t ram[1<<BUS_A_WIDTH];
		|	uint8_t screg;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "PIN_WE.pos()"
        yield "PIN_QVIOE"
        yield "BUS_A_SENSITIVE()"
        yield "BUS_MSP_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a, d;
		|
		|	BUS_A_READ(a);
		|	if (PIN_WE.posedge()) {
		|		BUS_DVI_READ(d);
		|		state->ram[a] = d;
		|	}
		|	d = state->ram[a];
		|	output.sp = !(odd_parity(d) & 1);
		|
		|	if (PIN_Q4.posedge()) {
		|		state->screg = d;
		|	}
		|
		|	unsigned msp;
		|	BUS_MSP_READ(msp);
		|	d >>= 1;
		|	d |= 0x80;
		|	output.sd = !((d >> (7-msp)) & 1);
		|	output.z_qvi = PIN_QVIOE=>;
		|	if (!output.z_qvi)
		|		output.qvi = state->screg;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSCAV", PartModelDQ("XSCAV", XSCAV))
