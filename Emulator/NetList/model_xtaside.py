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
   TYP A-side mux+latch
   ====================

'''

from part import PartModel, PartFactory

class XTASIDE(PartFactory):
    ''' TYP A-side mux+latch '''

    def state(self, file):
        file.fmt('''
		|	uint64_t alat;
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
		|	unsigned uir_a, loop;
		|	uint64_t a = 0, p;
		|
		|	if (PIN_LE) {
		|		BUS_C_READ(state->alat);
		|	}
		|	BUS_UA_READ(uir_a);
		|	if ((uir_a & 0x3c) != 0x28 || !PIN_AODIAG) {
		|		a = state->alat;
		|		PIN_AOUT = 0;
		|	} else if (uir_a == 0x28) {
		|		BUS_LOOP_READ(loop);
		|		a = BUS_A_MASK;
		|		a ^= BUS_LOOP_MASK;
		|		a |= loop;
		|		PIN_AOUT = 1;
		|	} else {
		|		a = BUS_A_MASK;
		|		BUS_A_WRITE(BUS_A_MASK);
		|		PIN_AOUT = 1;
		|	}
		|	BUS_A_WRITE(a);
		|	p = (a ^ (a >> 4)) & 0x0f0f0f0f0f0f0f0fULL;
		|	p = (p ^ (p >> 2)) & 0x0303030303030303ULL;
		|	p = (p ^ (p >> 1)) & 0x0101010101010101ULL;
		|	p |= (p >> 7);
		|	p |= (p >> 14);
		|	p |= (p >> 28);
		|	p &= 0xff;
		|	p ^= 0xff;
		|	BUS_AP_WRITE(p);
		|	TRACE(
		|	    << " aod " << PIN_AODIAG?
		|	    << " uira " << BUS_UA_TRACE()
		|	    << " loop " << BUS_LOOP_TRACE()
		|	    << " c " << BUS_C_TRACE()
		|	    << " - a " << BUS_A_TRACE()
		|	    << " " << std::hex << a
		|	    << " p " << std::hex << p
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTASIDE", PartModel("XTASIDE", XTASIDE))
