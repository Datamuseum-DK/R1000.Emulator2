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

from part import PartModelDQ, PartFactory

class XVBSIDE(PartFactory):
    ''' VAL B-side of RF '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t bram[1 << BUS_BADR_WIDTH];
		|	uint64_t b;
		|''')

    def sensitive(self):
        yield "BUS_DV"
        yield "BUS_C"
        yield "PIN_Q2.neg()"
        yield "PIN_BWE.pos()"
        yield "PIN_QVOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned badr;
		|	BUS_BADR_READ(badr);
		|
		|	if (PIN_BWE.posedge()) {
		|		uint64_t tmp;
		|		BUS_C_READ(tmp);
		|		state->bram[badr] = tmp;
		|	}
		|
		|	if (!PIN_H2=>) {
		|		bool oe, oe7;
		|
		|		unsigned uirb;
		|		BUS_UIRB_READ(uirb);
		|		uirb ^= BUS_UIRB_MASK;
		|		if (uirb != 0x16) {
		|			oe = false;
		|		} else if (!PIN_LHIT=> && !PIN_QVOE=>) { 
		|			oe = false;
		|		} else {
		|			oe = true;
		|		}
		|
		|		bool glit = PIN_GETL=>;
		|		oe7 = oe || !glit;
		|
		|		uint64_t b = 0;
		|		if (!oe) {
		|			b |= state->bram[badr] & 0xffffffffffffff00ULL;
		|		}
		|		if (!oe7) {
		|			b |= state->bram[badr] & 0xffULL;
		|		}
		|		if (oe || oe7) {
		|			uint64_t bus;
		|			BUS_DV_READ(bus);
		|			bus ^= BUS_DV_MASK;
		|			if (oe) {
		|				b |= bus & 0xffffffffffffff00ULL;
		|			}
		|			if (oe7) {
		|				b |= bus & 0xffULL;
		|			}
		|		}
		|		output.b = b;
		|		output.bmsb = b >> 63;
		|	}
		|''')


class XTVBSIDE(PartFactory):
    ''' TYP/VAL B-side of RF '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t bram[1 << BUS_A_WIDTH];
		|	uint64_t blat;
		|	uint64_t b;
		|''')

    def sensitive(self):
        yield "BUS_DX"
        yield "BUS_C"
        yield "PIN_BLE.pos()"
        yield "PIN_RFWE.pos()"
        yield "PIN_QXOE"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
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
		|		BUS_DX_READ(bus);
		|		bus ^= BUS_DX_MASK;
		|	}
		|	if (!PIN_BROE=>) {
		|		b |= bus & 0xffffffffffffff00ULL;
		|	}
		|	if (!PIN_BROE7=>) {
		|		b |= bus & 0xffULL;
		|	}
		|	output.b = b;
		|	output.bb0 = b >> 63;
		|	output.z_qx = PIN_QXOE=>;
		|	if (!output.z_qx) {
		|		output.qx = b ^ BUS_QX_MASK;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVBSIDE", PartModelDQ("XVBSIDE", XVBSIDE))
    part_lib.add_part("XTVBSIDE", PartModelDQ("XTVBSIDE", XTVBSIDE))
