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
   SEQ 52 MISC
   ===========

'''

from part import PartModel, PartFactory

class XS52MISC(PartFactory):
    ''' SEQ 52 MISC '''

    autopin = True

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_TCLR"

    def state(self, file):
        ''' Extra state variable '''

        file.fmt('''
		|	unsigned rreg;
		|	unsigned lreg;
		|	unsigned treg;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (!PIN_TCLR=>) {
		|		state->treg = 0;
		|		output.fo7 = false;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		if (PIN_SSTOP=> && PIN_BHEN=> && PIN_BHIN2=>) {
		|			unsigned restrt_rnd;
		|			BUS_RRND_READ(restrt_rnd);
		|			if (!PIN_WDISP=>) {
		|				state->rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->rreg = (restrt_rnd & 0x3) << 1;
		|			} else {
		|				state->rreg &= 0xa;
		|			}
		|			if (PIN_MEV=>) {
		|				state->rreg &= ~0x2;
		|			}
		|			BUS_TIN_READ(state->treg);
		|			state->treg ^= 0x4;
		|		} else if (PIN_SSTOP=> && PIN_BHEN=>) {
		|			state->rreg <<= 1;
		|			state->rreg &= 0xe;
		|			state->rreg |= 0x1;
		|			state->treg <<= 1;
		|			state->treg &= 0xe;
		|			state->treg |= 0x1;
		|		}
		|		output.rq = state->rreg;
		|		output.fo7 = state->treg >> 3;
		|
		|		unsigned lin;
		|		BUS_LIN_READ(lin);
		|
		|		if (!PIN_SCKEN=>) {
		|			state->lreg = lin;
		|		}
		|		output.lq = state->lreg;
		|		output.lqn = !(state->lreg & 1);
		|
		|		if ((lin & 0x4) && !PIN_SCKEN=>) {
		|			output.lcp = PIN_COND=>;
		|			output.lcn = !output.lcp;
		|		}
		|
		|		switch(output.lq & 0x6) {
		|		case 0x0:
		|		case 0x4:
		|			output.ldc = (output.lq >> 3) & 1;
		|			break;
		|		case 0x2:
		|			output.ldc = (output.lq >> 0) & 1;
		|			break;
		|		case 0x6:
		|			output.ldc = output.lcp;
		|			break;
		|		}
		|	}
		|		
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XS52MISC", PartModel("XS52MISC", XS52MISC))
