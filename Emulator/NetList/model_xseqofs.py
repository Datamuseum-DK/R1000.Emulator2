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
   SEQ offset generation
   =====================

'''

from part import PartModel, PartFactory

class XSEQOFS(PartFactory):

    ''' SEQ offset generation '''

    def state(self, file):
        file.fmt('''
		|	uint64_t offs;
		|	unsigned par;
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
		|#define DO_Z (1ULL << 32)
		|
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		if (state->offs == DO_Z) {
		|			BUS_ADR_Z();
		|			next_trigger(PIN_OE.negedge_event());
		|		} else {
		|			BUS_ADR_WRITE(state->offs);
		|		}
		|		BUS_PAR_WRITE(state->par);
		|	}
		|
		|	uint64_t offs;
		|
		|	if (PIN_OE=>) {
		|		offs = DO_Z;
		|	} else {
		|		if (!PIN_RESDR=>) {
		|			BUS_RES_READ(offs);
		|		} else if (PIN_ADRIC=>) {
		|			BUS_CODE_READ(offs);
		|		} else {
		|			BUS_OFFS_READ(offs);
		|		}
		|		offs <<= 7;
		|
		|		unsigned branch;
		|		BUS_BRNC_READ(branch);
		|		branch ^= BUS_BRNC_MASK;
		|		offs |= branch << 4;
		|	}
		|
		|	uint64_t tmp;
		|	unsigned par = 0;
		|
		|	tmp = offs & 0x7f;
		|	tmp = (tmp ^ (tmp >> 4)) & 0x0f;
		|	tmp = (tmp ^ (tmp >> 2)) & 0x03;
		|	tmp = (tmp ^ (tmp >> 1)) & 0x01;
		|	par |= tmp;
		|
		|	tmp = offs & 0x1f80;
		|	tmp = (tmp ^ (tmp >> 8)) & 0xff;
		|	tmp = (tmp ^ (tmp >> 4)) & 0x0f;
		|	tmp = (tmp ^ (tmp >> 2)) & 0x03;
		|	tmp = (tmp ^ (tmp >> 1)) & 0x01;
		|	tmp ^= 1;
		|	par |= tmp << 1;
		|
		|	tmp = offs & 0xffe000;
		|	tmp = (tmp ^ (tmp >> 16)) & 0xffff;
		|	tmp = (tmp ^ (tmp >>  8)) & 0xff;
		|	tmp = (tmp ^ (tmp >>  4)) & 0x0f;
		|	tmp = (tmp ^ (tmp >>  2)) & 0x03;
		|	tmp = (tmp ^ (tmp >>  1)) & 0x01;
		|	par |= tmp << 2;
		|
		|	tmp = offs & 0xff000000;
		|	tmp = (tmp ^ (tmp >> 16)) & 0xffff;
		|	tmp = (tmp ^ (tmp >>  8)) & 0xff;
		|	tmp = (tmp ^ (tmp >>  4)) & 0x0f;
		|	tmp = (tmp ^ (tmp >>  2)) & 0x03;
		|	tmp = (tmp ^ (tmp >>  1)) & 0x01;
		|	tmp ^= 1;
		|	par |= tmp << 3;
		|
		|	if (offs != state->offs || par != state->par) {
		|		state->ctx.job = 1;
		|		state->offs = offs;
		|		state->par = par;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQOFS", PartModel("XSEQOFS", XSEQOFS))
