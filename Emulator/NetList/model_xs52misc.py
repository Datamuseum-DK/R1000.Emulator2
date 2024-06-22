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
		|		output.tq = state->treg;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		unsigned prev_rreg = state->rreg;
		|		unsigned rmode;
		|		BUS_RMOD_READ(rmode);
		|		switch (rmode) {
		|		case 0:
		|			break;
		|		case 1:
		|			state->rreg <<= 1;
		|			state->rreg &= 0xe;
		|			state->rreg |= 0x1;
		|			break;
		|		case 2:
		|			state->rreg >>= 1;
		|			state->rreg &= 0x7;
		|			if (PIN_RSIN=>)
		|				state->rreg |= 0x8;
		|			break;
		|		case 3:
		|			unsigned restrt_rnd;
		|			BUS_RRND_READ(restrt_rnd);
		|			if (!PIN_WDISP=>) {
		|				state->rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->rreg = (restrt_rnd & 2) << 2;
		|				state->rreg |= (restrt_rnd & 1) << 1;
		|			} else {
		|				state->rreg &= 0xa;
		|			}
		|			if (PIN_MEV=>) {
		|				state->rreg &= ~0x2;
		|			}
		|			break;
		|		}
		|		output.rq = state->rreg;
		|
		|		switch (rmode) {
		|		case 0:
		|			break;
		|		case 1:
		|			state->treg <<= 1;
		|			state->treg &= 0xe;
		|			state->treg |= 0x1;
		|			break;
		|		case 2:
		|			state->treg >>= 1;
		|			state->treg &= 0x7;
		|			if (prev_rreg & 1)
		|				state->treg |= 0x8;
		|			break;
		|		case 3:
		|			BUS_TIN_READ(state->treg);
		|			break;
		|		}
		|		output.tq = state->treg;
		|
		|
		|		unsigned lmode;
		|		BUS_LMOD_READ(lmode);
		|		switch (lmode) {
		|		case 0:
		|			break;
		|		case 1:
		|			state->lreg <<= 1;
		|			state->lreg &= 0xe;
		|			state->lreg |= 0x1;
		|			break;
		|		case 2:
		|			state->lreg >>= 1;
		|			state->lreg &= 0x7;
		|			if (PIN_LSIN=>)
		|				state->lreg |= 0x8;
		|			break;
		|		case 3:
		|			BUS_LIN_READ(state->lreg);
		|			break;
		|		}
		|		output.lq = state->lreg;
		|		output.lqn = !(state->lreg & 1);
		|	}
		|		
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XS52MISC", PartModel("XS52MISC", XS52MISC))
