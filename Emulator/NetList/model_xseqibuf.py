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
   SEQ Instruction buffer
   ======================

'''

from part import PartModel, PartFactory

class XSEQIBUF(PartFactory):
    ''' SEQ Instruction buffer '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t typ, val;
		|	unsigned word;
		|	unsigned mpc;
		|''')

    def sensitive(self):
        yield "PIN_ICLK.pos()"
        yield "PIN_BCLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (PIN_ICLK.posedge()) {
		|		BUS_TYP_READ(state->typ);
		|		BUS_VAL_READ(state->val);
		|	} 
		|
		|	if (PIN_BCLK.posedge()) {
		|		unsigned mode = 0;
		|		unsigned u = 0;
		|		if (PIN_CNDLD=>) u |= 1;
		|		if (PIN_WDISP=>) u |= 2;
		|		switch (u) {
		|		case 0: mode = 1; break;
		|		case 1: mode = 1; break;
		|		case 3: mode = 0; break;
		|		case 2:
		|			if (PIN_MD0=>) mode |= 2;
		|			if (PIN_RND1=>) mode |= 1;
		|			break;
		|		}
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			if (!PIN_MUX=>) {
		|				BUS_VAL_READ(tmp);
		|				state->word = (tmp >> 4) & 7;
		|				state->mpc = (tmp >> 4) & 0x7fff;
		|			} else {
		|				BUS_BIDX_READ(state->word);
		|				state->mpc = state->word;
		|				BUS_BOF_READ(tmp);
		|				state->mpc |= (tmp << 3);
		|			}
		|		} else if (mode == 2) {
		|			state->mpc += 1;
		|			state->word += 1;
		|			if (state->word == 0x8)
		|				state->word = 0;
		|		} else if (mode == 1) {
		|			state->mpc -= 1;
		|			if (state->word == 0x0)
		|				state->word = 7;
		|			else
		|				state->word -= 1;
		|		}
		|		output.mps = state->mpc;
		|	}
		|
		|	PIN_EMP<=(state->word != 0);
		|
		|	if (state->word == 7)
		|		output.disp = state->typ >> 48;
		|	else if (state->word == 6)
		|		output.disp = state->typ >> 32;
		|	else if (state->word == 5)
		|		output.disp = state->typ >> 16;
		|	else if (state->word == 4)
		|		output.disp = state->typ >> 0;
		|	else if (state->word == 3)
		|		output.disp = state->val >> 48;
		|	else if (state->word == 2)
		|		output.disp = state->val >> 32;
		|	else if (state->word == 1)
		|		output.disp = state->val >> 16;
		|	else if (state->word == 0)
		|		output.disp = state->val >> 0;
		|	else
		|		output.disp = 0xffff;
		|	output.disp &= 0xffff;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQIBUF", PartModel("XSEQIBUF", XSEQIBUF))
