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
   VAL Writable Control Store
   ==========================

'''

from part import PartModel, PartFactory

class XVALWCS(PartFactory):
    ''' VAL Writable Control Store '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|	unsigned addr;
		|	uint64_t wcs, ff1, ff2, ff3, sr0, sr1, sr2, sr4;
		|''')

    def sensitive(self):
        yield "PIN_DUAS"
        yield "BUS_UAC"
        yield "BUS_UAD"
        yield "PIN_UCLK.pos()"
        yield "PIN_USEL"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|#define PERMUTE(MX) \\
		|	MX( 0, state->ff1, 0, 1) \\
		|	MX( 1, state->ff1, 1, 1) \\
		|	MX( 2, state->ff1, 2, 1) \\
		|	MX( 3, state->ff1, 3, 1) \\
		|	MX( 4, state->ff1, 4, 1) \\
		|	MX( 5, state->ff1, 5, 1) \\
		|	MX( 6, state->ff1, 6, 1) \\
		|	MX( 7, state->ff1, 7, 1) \\
		|	MX( 8, state->ff2, 0, 1) \\
		|	MX( 9, state->ff2, 1, 1) \\
		|	MX(10, state->ff2, 2, 1) \\
		|	MX(11, state->ff2, 3, 1) \\
		|	MX(12, state->ff2, 4, 1) \\
		|	MX(13, state->ff2, 5, 1) \\
		|	MX(14, state->ff2, 6, 1) \\
		|	MX(15, state->ff2, 7, 1) \\
		|	MX(16, state->ff3, 7, 1) \\
		|	MX(17, state->sr0, 5, 0) \\
		|	MX(18, state->sr0, 6, 0) \\
		|	MX(39, state->sr0, 7, 0) \\
		|	MX(19, state->sr1, 4, 0) \\
		|	MX(20, state->sr1, 5, 0) \\
		|	MX(21, state->sr1, 6, 0) \\
		|	MX(22, state->sr1, 7, 0) \\
		|	MX(23, state->sr2, 0, 0) \\
		|	MX(24, state->sr2, 1, 0) \\
		|	MX(25, state->sr2, 2, 0) \\
		|	MX(26, state->sr2, 3, 0) \\
		|	MX(27, state->sr2, 4, 0) \\
		|	MX(28, state->sr2, 5, 0) \\
		|	MX(29, state->sr2, 6, 0) \\
		|	MX(30, state->sr2, 7, 0) \\
		|	MX(31, state->sr4, 0, 0) \\
		|	MX(32, state->sr4, 1, 0) \\
		|	MX(33, state->sr4, 2, 0) \\
		|	MX(34, state->sr4, 3, 0) \\
		|	MX(35, state->sr4, 4, 0) \\
		|	MX(36, state->sr4, 5, 0) \\
		|	MX(37, state->sr4, 6, 0) \\
		|	MX(38, state->sr4, 7, 0) \\
		|
		|#define WCS2SR(wcsbit, srnam, srbit, inv) \\
		|	srnam |= ((state->wcs >> BUS_UIR_LSB(wcsbit)) & 1) << (7 - srbit);
		|#define SR2WCS(wcsbit, srnam, srbit, inv) \\
		|	state->wcs |= ((srnam >> (7 - srbit)) & 1) << BUS_UIR_LSB(wcsbit);
		|#define INVM(wcsbit, srnam, srbit, inv) state->wcs ^= (uint64_t)inv << BUS_UIR_LSB(wcsbit);
		|
		|#define TOSR() \\
		|	do { \\
		|		state->ff1 = 0; \\
		|		state->ff2 = 0; \\
		|		state->ff3 = 0; \\
		|		state->sr0 = 0; \\
		|		state->sr1 = 0; \\
		|		state->sr2 = 0; \\
		|		state->sr4 = 0; \\
		|		PERMUTE(WCS2SR); \\
		|	} while (0)
		|
		|#define TOWCS() \\
		|	do { \\
		|		state->wcs = 0; \\
		|		PERMUTE(SR2WCS); \\
		|	} while (0)
		|
		|	unsigned uad, cnt;
		|	BUS_UAC_READ(cnt);
		|	BUS_UAD_READ(uad);
		|	if (PIN_DUAS=>) {
		|		uad ^= BUS_UAD_MASK;
		|	} else {
		|		uad = BUS_UAD_MASK;
		|	}
		|	state->addr = (uad & cnt);
		|	state->addr ^= BUS_UAC_MASK;
		|
		|	if (PIN_UCLK.posedge()) {
		|		if (PIN_USEL=>) {
		|			state->wcs = state->ram[state->addr];
		|			state->wcs ^= 0xffff800000;
		|		} else {
		|			unsigned diag = 0xff;
		|			TOSR();
		|			state->ff1 >>= 1;
		|			state->ff1 |= ((diag >> 7) & 1) << 7;
		|			state->ff1 ^= 0x80;
		|			state->ff2 >>= 1;
		|			state->ff2 |= ((diag >> 6) & 1) << 7;
		|			state->ff2 ^= 0x80;
		|			state->sr1 >>= 1;
		|			state->sr1 |= (state->sr0 & 1) << 3;
		|			state->sr0 >>= 1;
		|			state->sr0 |= (state->ff3 & 1) << 2;
		|			state->ff3 = ((diag >> 5) & 1);
		|			state->ff3 ^= 1;
		|			state->sr2 >>= 1;
		|			state->sr2 |= ((diag >> 4) & 1) << 7;
		|			state->sr4 >>= 1;
		|			state->sr4 |= ((diag >> 3) & 1) << 7;
		|			TOWCS();
		|		}
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	} 
		|
		|	output.uir = state->wcs;
		|
		|	uint64_t tmp = state->ram[state->addr];
		|
		|	unsigned aadr = (tmp >> BUS_UIR_LSB(5)) & 0x3f;
		|	output.ald = (aadr == 0x13);
		|
		|	unsigned badr = (tmp >> BUS_UIR_LSB(11)) & 0x3f;
		|	output.bld = (badr == 0x13);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVALWCS", PartModel("XVALWCS", XVALWCS))
