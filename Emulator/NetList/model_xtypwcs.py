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
   TYP Writable Control Store
   ==========================

'''

from part import PartModel, PartFactory

class XTYPWCS(PartFactory):
    ''' TYP Writable Control Store '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_UAC_WIDTH];
		|	unsigned addr;
		|	uint64_t wcs, ff1, ff2, ff3, sr0, sr1, sr2, sr3;
		|''')

    def xxsensitive(self):
        yield "PIN_UCLK.pos()"
        yield "PIN_WE.pos()"
        yield "PIN_FPA"
        yield "PIN_SUIR"
        yield "BUS_UAC_SENSITIVE()"
        yield "BUS_UAD_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
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
		|	MX(17, state->sr0, 1, 0) \\
		|	MX(18, state->sr0, 2, 0) \\
		|	MX(46, state->sr0, 3, 0) \\
		|	MX(19, state->sr0, 4, 0) \\
		|	MX(20, state->sr0, 5, 0) \\
		|	MX(21, state->sr0, 6, 0) \\
		|	MX(22, state->sr0, 7, 0) \\
		|	MX(23, state->sr1, 0, 0) \\
		|	MX(24, state->sr1, 1, 0) \\
		|	MX(25, state->sr1, 2, 0) \\
		|	MX(26, state->sr1, 3, 0) \\
		|	MX(27, state->sr1, 4, 0) \\
		|	MX(28, state->sr1, 5, 0) \\
		|	MX(29, state->sr1, 6, 0) \\
		|	MX(30, state->sr1, 7, 0) \\
		|	MX(31, state->sr2, 0, 0) \\
		|	MX(32, state->sr2, 1, 0) \\
		|	MX(33, state->sr2, 2, 0) \\
		|	MX(34, state->sr2, 3, 0) \\
		|	MX(35, state->sr2, 4, 0) \\
		|	MX(36, state->sr2, 5, 0) \\
		|	MX(37, state->sr2, 6, 0) \\
		|	MX(38, state->sr2, 7, 0) \\
		|	MX(39, state->sr3, 0, 0) \\
		|	MX(40, state->sr3, 1, 0) \\
		|	MX(41, state->sr3, 2, 0) \\
		|	MX(42, state->sr3, 3, 0) \\
		|	MX(43, state->sr3, 4, 0) \\
		|	MX(44, state->sr3, 5, 0) \\
		|	MX(45, state->sr3, 6, 0) \\
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
		|		state->sr3 = 0; \\
		|		PERMUTE(WCS2SR); \\
		|		state->sr3 |= state->wcs >> 63; \\
		|	} while (0)
		|
		|#define TOWCS() \\
		|	do { \\
		|		state->wcs = 0; \\
		|		PERMUTE(SR2WCS); \\
		|		state->wcs |= (state->sr3 & 1) << 63; \\
		|	} while (0)
		|
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_UIR_WRITE(state->wcs);
		|		uint64_t tmp = state->ram[state->addr];
		|		unsigned aadr = (tmp >> BUS_UIR_LSB(5)) & 0x3f;
		|		PIN_ALD<=(aadr == 0x13);
		|		unsigned badr = (tmp >> BUS_UIR_LSB(11)) & 0x3f;
		|		PIN_BLD<=(badr == 0x13);
		|		uint64_t par;
		|		par = state->wcs & BUS_UIR_MASK;
		|		par = ((par >> 32) ^ par) & 0xffffffff;
		|		par = ((par >> 16) ^ par) & 0xffff;
		|		par = ((par >> 8) ^ par) & 0xff;
		|		par = ((par >> 4) ^ par) & 0xf;
		|		par = ((par >> 2) ^ par) & 0x3;
		|		par = ((par >> 1) ^ par) & 0x1;
		|		par ^= 1;
		|		PIN_PERR<=(par);
		|		unsigned clit = 0;
		|		clit |= (state->wcs >> BUS_UIR_LSB(16)) & 0x1f;
		|		clit |= ((state->wcs >> BUS_UIR_LSB(18)) & 0x3) << 5;
		|		BUS_CLIT_WRITE(clit);
		|	}
		|
		|	unsigned uad, cnt;
		|	BUS_UAC_READ(cnt);
		|	BUS_UAD_READ(uad);
		|	if (PIN_DUAS=>) {
		|		uad ^= BUS_UAD_MASK;
		|	} else {
		|		uad = BUS_UAD_MASK;
		|	}
		|	state->addr = (uad & cnt) & BUS_UAC_MASK;
		|	state->addr ^= BUS_UAC_MASK;
		|	unsigned upar0 = uad & 0x40ff;
		|	upar0 = ((upar0 >> 8) | upar0) & 0xff;
		|	upar0 = ((upar0 >> 4) | upar0) & 0xf;
		|	upar0 = ((upar0 >> 2) | upar0) & 0x3;
		|	upar0 = ((upar0 >> 1) | upar0) & 0x1;
		|	unsigned upar1 = uad & 0xbf00;
		|	upar1 = ((upar1 >> 8) | upar1) & 0xff;
		|	upar1 = ((upar1 >> 4) | upar1) & 0xf;
		|	upar1 = ((upar1 >> 2) | upar1) & 0x3;
		|	upar1 = ((upar1 >> 1) | upar1) & 0x1;
		|	upar0 ^= 1;
		|	upar1 ^= 1;
		|	PIN_UPER<=!(upar0 | upar1);
		|
		|	if (PIN_UCLK.posedge()) {
		|		if (PIN_USEL=>) {
		|			state->wcs = state->ram[state->addr];
		|			state->wcs |= (1ULL << 63);
		|			PERMUTE(INVM);
		|		} else {
		|			unsigned diag;
		|			BUS_DGI_READ(diag);
		|			TOSR();
		|			state->ff1 >>= 1;
		|			state->ff1 |= ((diag >> 7) & 1) << 7;
		|			state->ff1 ^= 0x80;
		|			state->ff2 >>= 1;
		|			state->ff2 |= ((diag >> 6) & 1) << 7;
		|			state->ff2 ^= 0x80;
		|			state->sr0 >>= 1;
		|			state->sr0 |= (state->ff3 & 1) << 6;
		|			state->ff3 = ((diag >> 5) & 1);
		|			state->ff3 ^= 1;
		|			state->sr1 >>= 1;
		|			state->sr1 |= ((diag >> 4) & 1) << 7;
		|			state->sr2 >>= 1;
		|			state->sr2 |= ((diag >> 3) & 1) << 7;
		|			state->sr3 >>= 1;
		|			state->sr3 |= ((diag >> 2) & 1) << 7;
		|			TOWCS();
		|		}
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|	if (!PIN_SUIR=>) {
		|		unsigned dout = 0;
		|		TOSR();
		|		dout |= (state->ff1 & 1) << 7;
		|		dout |= (state->ff2 & 1) << 6;
		|		dout |= (state->sr0 & 1) << 5;
		|		dout |= (state->sr1 & 1) << 4;
		|		dout |= (state->sr2 & 1) << 3;
		|		dout |= (state->sr3 & 1) << 2;
		|		dout |= PIN_PDCY=> << 1;
		|		dout ^= 0x80;
		|		dout ^= 0xff;
		|		dout |= 0x01;
		|		BUS_DGO_WRITE(dout);
		|	} else if (PIN_SUIR.posedge()) {
		|		BUS_DGO_Z();
		|	}
		|	if (PIN_WE.posedge()) {
		|		state->ram[state->addr] = state->wcs;
		|	}
		|	unsigned csacntl0 = (state->ram[state->addr] >> BUS_UIR_LSB(45)) & 7;
		|	unsigned csacntl1 = (state->wcs >> BUS_UIR_LSB(45)) & 6;
		|	PIN_FPDT<=!(
		|		(csacntl0 == 7) &&
		|		(csacntl1 == 0)
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTYPWCS", PartModel("XTYPWCS", XTYPWCS))
