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
   SEQ Writeable Control Store
   ===========================

			VAL                                             TYP
IR0     IR1     IR2     0-32            32-47           48-63           0-31            32-63
0       0       0       TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE VAL BUS
0       0       1       OFFS.OE~        OFFS.OE~        CUR_INSTRA.OE~  CUR_NAME.OE~    OFFS.OE~        CURRENT MACRO INSTRUCTION
0       1       0       OFFS.OE~        OFFS.OE~        DECODE.OE~      CUR_NAME.OE~    OFFS.OE~        DECODING MACRO INSTRUCTION
0       1       1       OFFS.OE~        OFFS.OE~        TOP_STACK.OE~   CUR_NAME.OE~    OFFS.OE~        TOP OF THE MICRO STACK
1       0       0       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        SAVE OFFSET
1       0       1       OFFS.OE~        OFFS.OE~        PC.OE~          REF_NAME.OE~    OFFS.OE~        RESOLVE RAM
1       1       0       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        CONTROL TOP
1       1       1       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        CONTROL PRED

'''

from part import PartModel, PartFactory

class XSEQWCS(PartFactory):
    ''' SEQ Writeable Control Store '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t *ram;
		|	uint64_t wcs;
		|	bool ff0, ff1, ff2;
		|''')

    def init(self, file):
        file.fmt('''
		|	state->ram = (uint64_t*)CTX_GetRaw("SEQ_WCS", sizeof(uint64_t) << BUS_UA_WIDTH);
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_DSP0"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned um, tmp, ua;
		|
		|	if (PIN_CLK.posedge()) {
		|		BUS_UM_READ(um);
		|		switch (um) {
		|		case 3: // load
		|			BUS_UA_READ(ua);
		|			state->wcs = state->ram[ua];
		|			output.halt = !(PIN_SCE=> || PIN_HLR=>);
		|			output.llm = !(PIN_SCE=> || !PIN_LMAC=>);
		|			output.uir = state->wcs;
		|			output.uir ^= 0x7fULL << 13;	// Invert condsel
		|		case 0: // noop
		|			break;
		|		}
		|
		|		BUS_UA_READ(ua);
		|		tmp = state->ram[ua];
		|		unsigned br_type = (tmp >> 22) & 0xf;
		|		state->ff0 = 0xb < br_type && br_type < 0xf;
		|		output.mdsp = !state->ff0;
		|		unsigned lex_adr = (tmp >> 11) & 0x3;
		|		state->ff1 = lex_adr & 0x2;
		|		state->ff2 = lex_adr == 0;
		|		if (!state->ff2)
		|			output.ras &= ~1;
		|		else
		|			output.ras |= 1;
		|		output.lexi = lex_adr == 1;
		|	}
		|	if ((state->ff0 && !PIN_DSP0=>) || state->ff1)
		|		output.ras &= ~2;
		|	else
		|		output.ras |= 2;
		''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQWCS", PartModel("XSEQWCS", XSEQWCS))
