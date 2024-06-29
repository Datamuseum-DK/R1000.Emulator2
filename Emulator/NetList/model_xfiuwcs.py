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
   FIU Writable Control Store
   ==========================

'''

from part import PartModel, PartFactory

class XFIUWCS(PartFactory):
    ''' FIU Writable Control Store '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|	uint64_t wcs, sr0, sr1, sr2, sr3, sr4, ff5;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_WE.pos()"
        yield "PIN_SUIR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|#define PERMUTE(MX) \\
		|	MX( 1, state->sr0, 0) /* OFFS_LIT0 */ \\
		|	MX( 2, state->sr0, 1) /* OFFS_LIT1 */ \\
		|	MX( 3, state->sr0, 2) /* OFFS_LIT2 */ \\
		|	MX( 4, state->sr0, 3) /* OFFS_LIT3 */ \\
		|	MX( 5, state->sr0, 4) /* OFFS_LIT4 */ \\
		|	MX( 6, state->sr0, 5) /* OFFS_LIT5 */ \\
		|	MX( 7, state->sr0, 6) /* OFFS_LIT6 */ \\
		|	MX( 9, state->sr0, 7) /* LFL0 */ \\
		|	MX(10, state->sr1, 0) /* LFL1 */ \\
		|	MX(11, state->sr1, 1) /* LFL2 */ \\
		|	MX(12, state->sr1, 2) /* LFL3 */ \\
		|	MX(13, state->sr1, 3) /* LFL4 */ \\
		|	MX(14, state->sr1, 4) /* LFL5 */ \\
		|	MX(15, state->sr1, 5) /* LFL6 */ \\
		|	MX(16, state->sr1, 6) /* LFREG_CNTL0 */ \\
		|	MX(17, state->sr1, 7) /* LFREG_CNTL1 */ \\
		|	MX(18, state->sr2, 0) /* OP_SEL0 */ \\
		|	MX(19, state->sr2, 1) /* OP_SEL1 */ \\
		|	MX(20, state->sr2, 2) /* VMUX_SEL0 */ \\
		|	MX(21, state->sr2, 3) /* VMUX_SEL1 */ \\
		|	MX(22, state->sr2, 4) /* FILL_MODE_SRC */ \\
		|	MX(23, state->sr2, 5) /* OREG_SRC */ \\
		|	MX( 0, state->sr2, 6) /* - */ \\
		|	MX( 8, state->sr2, 7) /* CHAIN2 */ \\
		|	MX(24, state->sr3, 0) /* TIVI_SRC0 */ \\
		|	MX(25, state->sr3, 1) /* TIVI_SRC1 */ \\
		|	MX(26, state->sr3, 2) /* TIVI_SRC2 */ \\
		|	MX(27, state->sr3, 3) /* TIVI_SRC3 */ \\
		|	MX(28, state->sr3, 4) /* LOAD_OREG */ \\
		|	MX(29, state->sr3, 5) /* LOAD_VAR */ \\
		|	MX(30, state->sr3, 6) /* LOAD_TAR */ \\
		|	MX(31, state->sr3, 7) /* LOAD_MDR */ \\
		|	MX(33, state->sr4, 0) /* MEM_START0 */ \\
		|	MX(34, state->sr4, 1) /* MEM_START1 */ \\
		|	MX(35, state->sr4, 2) /* MEM_START2 */ \\
		|	MX(36, state->sr4, 3) /* MEM_START3 */ \\
		|	MX(37, state->sr4, 4) /* MEM_START4 */ \\
		|	MX(38, state->sr4, 5) /* RDATA_SRC */ \\
		|	MX(32, state->sr4, 6) /* - */ \\
		|	MX(39, state->sr4, 7) /* UIR.P */ \\
		|	MX(46, state->ff5, 0) /* LENGTH_SRC */ \\
		|	MX(47, state->ff5, 1) /* OFFS_SRC */ \\
		|
		|#define BUS_UIR_LSB(lsb) (47 - (lsb))
		|
		|#define WCS2SR(wcsbit, srnam, srbit) \\
		|	srnam |= ((state->wcs >> BUS_UIR_LSB(wcsbit)) & 1) << (7 - srbit);
		|
		|#define SR2WCS(wcsbit, srnam, srbit) \\
		|	state->wcs |= ((srnam >> (7 - srbit)) & 1) << BUS_UIR_LSB(wcsbit);
		|
		|#define TOSR() \\
		|	do { \\
		|		state->sr0 = 0; \\
		|		state->sr1 = 0; \\
		|		state->sr2 = 0; \\
		|		state->sr3 = 0; \\
		|		state->sr4 = 0; \\
		|		state->ff5 = 0; \\
		|		PERMUTE(WCS2SR); \\
		|	} while (0)
		|
		|#define TOWCS() \\
		|	do { \\
		|		state->wcs = 0; \\
		|		PERMUTE(SR2WCS); \\
		|	} while (0)
		|
		|	unsigned addr;
		|	if (PIN_DUAS=>) {
		|		BUS_UAC_READ(addr);
		|	} else {
		|		BUS_UAD_READ(addr);
		|	}
		|
		|	addr &= BUS_UAD_MASK;
		|
		|	if (PIN_CLK.posedge() && !PIN_CKEN=> && !PIN_SFST=>) {
		|		if (PIN_MODE=>) {
		|			state->wcs = state->ram[addr];
		|		} else {
		|			unsigned diag;
		|			BUS_DGI_READ(diag);
		|			TOSR();
		|			state->sr0 >>= 1;
		|			state->sr0 |= ((diag >> 7) & 1) << 7;
		|			state->sr1 >>= 1;
		|			state->sr1 |= ((diag >> 6) & 1) << 7;
		|			state->sr2 >>= 1;
		|			state->sr2 |= ((diag >> 5) & 1) << 7;
		|			state->sr3 >>= 1;
		|			state->sr3 |= ((diag >> 4) & 1) << 7;
		|			state->sr4 >>= 1;
		|			state->sr4 |= ((diag >> 3) & 1) << 7;
		|			state->ff5 >>= 1;
		|			state->ff5 |= ((diag >> 2) & 1) << 7;
		|			TOWCS();
		|		}
		|
		|		output.ofsl = (state->wcs >> 40) & BUS_OFSL_MASK;
		|		output.lfl = (state->wcs >> 32) & BUS_LFL_MASK;
		|		output.lfcn = (state->wcs >> 30) & BUS_LFCN_MASK;
		|		output.opsl = (state->wcs >> 28) & BUS_OPSL_MASK;
		|		output.vmsl = (state->wcs >> 26) & BUS_VMSL_MASK;
		|		output.fill = (state->wcs >> 25) & 1;
		|		output.osrc = (state->wcs >> 24) & 1;
		|		output.tivi = (state->wcs >> 20) & BUS_TIVI_MASK;
		|		output.ldo = (state->wcs >> 19) & 1;
		|		output.ldv = (state->wcs >> 18) & 1;
		|		output.ldt = (state->wcs >> 17) & 1;
		|		output.ldm = (state->wcs >> 16) & 1;
		|		output.mstr = (state->wcs >> 10) & BUS_MSTR_MASK;
		|		output.rsrc = (state->wcs >> 9) & 1;
		|		output.lsrc = (state->wcs >> 1) & 1;
		|		output.ofsrc = (state->wcs >> 0) & 1;
		|
		|	}
		|	output.z_dgo = PIN_SUIR=>;
		|	if (!output.z_dgo) {
		|		unsigned dout = 0;
		|		TOSR();
		|		dout |= (state->sr0 & 1) << 7;
		|		dout |= (state->sr1 & 1) << 6;
		|		dout |= (state->sr2 & 1) << 5;
		|		dout |= (state->sr3 & 1) << 4;
		|		dout |= (state->sr4 & 1) << 3;
		|		dout |= (state->ff5 & 0x40) >> 4;
		|		dout |= 0x3;
		|		output.dgo = dout;
		|	}
		|	if (PIN_WE.posedge()) {
		|		state->ram[addr] = state->wcs;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUWCS", PartModel("XFIUWCS", XFIUWCS))
