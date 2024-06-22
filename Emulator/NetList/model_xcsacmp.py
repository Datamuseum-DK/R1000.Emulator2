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
   FIU CSA Comparator
   ==================

'''

from part import PartModel, PartFactory

class XCSACMP(PartFactory):
    ''' FIU CSA Comparator '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned nve, pdreg;
		|	bool pdt, oor;
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

        file.fmt('''
		|	unsigned a, b, dif;
		|	bool co, name_match, in_range;
		|
		|	if (PIN_SCLK.posedge()) {
		|		// CSAFFB
		|		state->pdt = !PIN_PRED=>;
		|
		|		// NVEMUX + CSAREG
		|		if (PIN_DSEL=>) {
		|			BUS_CNV_READ(state->nve);
		|		} else if (PIN_DNVE=>) {
		|			state->nve = 0xf;
		|		} else {
		|			state->nve = 0;
		|		}
		|	}
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|
		|	if (PIN_OCLK.posedge()) {
		|		state->pdreg = a;
		|	}
		|
		|	if (state->pdt) {
		|		co = a <= state->pdreg;
		|		dif = ~0xfffff + state->pdreg - a;
		|	} else {
		|		co = b <= a;
		|		dif = ~0xfffff + a - b;
		|	}
		|	dif &= 0xfffff;
		|
		|	name_match = PIN_NMAT=>;
		|
		|	// CNAN0B, CINV0B, CSCPR0
		|	in_range = (!state->pdt && name_match) || (dif & 0xffff0);
		|	output.inrg = in_range;
		|
		|	output.hofs = 0xf + state->nve - (dif & 0xf);
		|
		|	output.chit = !(
		|		co &&
		|		!(
		|			in_range ||
		|			((dif & 0xf) >= state->nve)
		|		)
		|	);
		|
		|	if (PIN_Q4.posedge()) {
		|		state->oor = !(co || name_match);
		|		output.oor = state->oor;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCSACMP", PartModel("XCSACMP", XCSACMP))
