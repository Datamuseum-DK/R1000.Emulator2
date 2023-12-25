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
   TYP/VAL B-side of RF
   ====================

'''

from part import PartModel, PartFactory

class XTVBSIDE(PartFactory):
    ''' TYP/VAL B-side of RF '''

    def state(self, file):
        file.fmt('''
		|	uint64_t bram[1 << BUS_A_WIDTH];
		|	uint64_t blat;
		|	uint64_t b;
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
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_B_WRITE(state->b);
		|	}
		|	uint64_t cbuf, b = 0, bus;
		|	unsigned adr;
		|
		|	if (PIN_RFCS=>) {
		|		BUS_C_READ(cbuf);
		|	} else {
		|		BUS_A_READ(adr);
		|		cbuf = state->bram[adr];
		|	}
		|	if (PIN_RFWE.posedge()) {
		|		uint64_t tmp;
		|		BUS_A_READ(adr);
		|		BUS_C_READ(tmp);
		|		state->bram[adr] = tmp;
		|	}
		|	if (PIN_BLE=>) {
		|		state->blat = cbuf;
		|	}
		|	if (!PIN_BOE=>) {
		|		b |= state->blat & 0xffffffffffffff00ULL;
		|	}
		|	if (!PIN_BOE7=>) {
		|		b |= state->blat & 0xffULL;
		|	}
		|	if (!PIN_BROE=> || !PIN_BROE7=>) {
		|		BUS_BUS_READ(bus);
		|		bus ^= BUS_BUS_MASK;
		|	}
		|	if (!PIN_BROE=>) {
		|		b |= bus & 0xffffffffffffff00ULL;
		|	}
		|	if (!PIN_BROE7=>) {
		|		b |= bus & 0xffULL;
		|	}
		|#if 0
		|	if (b != state->b) {
		|		state->ctx.job = 1;
		|		state->b = b;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|#else
		|	BUS_B_WRITE(b);
		|#endif
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVBSIDE", PartModel("XTVBSIDE", XTVBSIDE))
