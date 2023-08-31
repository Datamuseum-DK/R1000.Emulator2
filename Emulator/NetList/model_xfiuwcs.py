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

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|	unsigned addr;
		|	uint64_t wcs, sr0, sr1, sr2, sr3, sr4, ff5;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_WE.pos()"
        yield "PIN_SUIR"
        yield "BUS_UAD_SENSITIVE()"
        yield "BUS_UAC_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|#define PERMUTE(MX) \\
		|	MX( 1, state->sr0, 0, 0) /* OFFS_LIT0 */ \\
		|	MX( 2, state->sr0, 1, 0) /* OFFS_LIT1 */ \\
		|	MX( 3, state->sr0, 2, 0) /* OFFS_LIT2 */ \\
		|	MX( 4, state->sr0, 3, 0) /* OFFS_LIT3 */ \\
		|	MX( 5, state->sr0, 4, 0) /* OFFS_LIT4 */ \\
		|	MX( 6, state->sr0, 5, 0) /* OFFS_LIT5 */ \\
		|	MX( 7, state->sr0, 6, 0) /* OFFS_LIT6 */ \\
		|	MX( 9, state->sr0, 7, 0) /* LFL0 */ \\
		|	MX(10, state->sr1, 0, 0) /* LFL1 */ \\
		|	MX(11, state->sr1, 1, 0) /* LFL2 */ \\
		|	MX(12, state->sr1, 2, 0) /* LFL3 */ \\
		|	MX(13, state->sr1, 3, 0) /* LFL4 */ \\
		|	MX(14, state->sr1, 4, 0) /* LFL5 */ \\
		|	MX(15, state->sr1, 5, 0) /* LFL6 */ \\
		|	MX(16, state->sr1, 6, 0) /* LFREG_CNTL0 */ \\
		|	MX(17, state->sr1, 7, 0) /* LFREG_CNTL1 */ \\
		|	MX(18, state->sr2, 0, 0) /* OP_SEL0 */ \\
		|	MX(19, state->sr2, 1, 0) /* OP_SEL1 */ \\
		|	MX(20, state->sr2, 2, 0) /* VMUX_SEL0 */ \\
		|	MX(21, state->sr2, 3, 0) /* VMUX_SEL1 */ \\
		|	MX(22, state->sr2, 4, 0) /* FILL_MODE_SRC */ \\
		|	MX(23, state->sr2, 5, 0) /* OREG_SRC */ \\
		|	MX( 0, state->sr2, 6, 0) /* - */ \\
		|	MX( 8, state->sr2, 7, 0) /* CHAIN2 */ \\
		|	MX(24, state->sr3, 0, 0) /* TIVI_SRC0 */ \\
		|	MX(25, state->sr3, 1, 0) /* TIVI_SRC1 */ \\
		|	MX(26, state->sr3, 2, 0) /* TIVI_SRC2 */ \\
		|	MX(27, state->sr3, 3, 0) /* TIVI_SRC3 */ \\
		|	MX(28, state->sr3, 4, 0) /* LOAD_OREG */ \\
		|	MX(29, state->sr3, 5, 0) /* LOAD_VAR */ \\
		|	MX(30, state->sr3, 6, 0) /* LOAD_TAR */ \\
		|	MX(31, state->sr3, 7, 0) /* LOAD_MDR */ \\
		|	MX(33, state->sr4, 0, 0) /* MEM_START0 */ \\
		|	MX(34, state->sr4, 1, 0) /* MEM_START1 */ \\
		|	MX(35, state->sr4, 2, 0) /* MEM_START2 */ \\
		|	MX(36, state->sr4, 3, 0) /* MEM_START3 */ \\
		|	MX(37, state->sr4, 4, 0) /* MEM_START4 */ \\
		|	MX(38, state->sr4, 5, 0) /* RDATA_SRC */ \\
		|	MX(32, state->sr4, 6, 0) /* - */ \\
		|	MX(39, state->sr4, 7, 0) /* UIR.P */ \\
		|	MX(46, state->ff5, 0, 0) /* LENGTH_SRC */ \\
		|	MX(47, state->ff5, 1, 0) /* OFFS_SRC */ \\
		|
		|#ifndef BUS_UIR_LSB
		|#  define BUS_UIR_LSB(lsb) (47 - (lsb))
		|#endif
		|
		|#define WCS2SR(wcsbit, srnam, srbit, inv) \\
		|	srnam |= ((state->wcs >> BUS_UIR_LSB(wcsbit)) & 1) << (7 - srbit);
		|
		|#define SR2WCS(wcsbit, srnam, srbit, inv) \\
		|	state->wcs |= ((srnam >> (7 - srbit)) & 1) << BUS_UIR_LSB(wcsbit);
		|
		|#define INVM(wcsbit, srnam, srbit, inv) state->wcs ^= (uint64_t)inv << BUS_UIR_LSB(wcsbit);
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
		|	if (state->ctx.job == 1) {
		|		state->ctx.job = 0;
		|
		|		BUS_OFSL_WRITE(state->wcs >> 40);
		|		BUS_LFL_WRITE(state->wcs >> 32);
		|		BUS_LFCN_WRITE(state->wcs >> 30);
		|		BUS_OPSL_WRITE(state->wcs >> 28);
		|		BUS_VMSL_WRITE(state->wcs >> 26);
		|		PIN_FILL<=((state->wcs >> 25) & 1);
		|		PIN_OSRC<=((state->wcs >> 24) & 1);
		|		BUS_TIVI_WRITE(state->wcs >> 20);
		|		PIN_LDO<=((state->wcs >> 19) & 1);
		|		PIN_LDV<=((state->wcs >> 18) & 1);
		|		PIN_LDT<=((state->wcs >> 17) & 1);
		|		PIN_LDM<=((state->wcs >> 16) & 1);
		|		BUS_MSTR_WRITE(state->wcs >> 10);
		|		PIN_RSRC<=((state->wcs >> 9) & 1);
		|		PIN_LSRC<=((state->wcs >> 1) & 1);
		|		PIN_OFSRC<=((state->wcs >> 0) & 1);
		|
		|		uint64_t par;
		|		par = state->wcs & 0x7f7fffff7f03;
		|		par = ((par >> 32) ^ par) & 0xffffffff;
		|		par = ((par >> 16) ^ par) & 0xffff;
		|		par = ((par >> 8) ^ par) & 0xff;
		|		par = ((par >> 4) ^ par) & 0xf;
		|		par = ((par >> 2) ^ par) & 0x3;
		|		par = ((par >> 1) ^ par) & 0x1;
		|		PIN_UPER<=(par);
		|	}
		|
		|	unsigned uad;
		|	if (PIN_DUAS=>) {
		|		BUS_UAC_READ(uad);
		|	} else {
		|		BUS_UAD_READ(uad);
		|	}
		|
		|	state->addr = uad & 0x3fff;
		|
		|	unsigned pa = uad & 0x40ff;
		|	pa = (pa ^ (pa >> 8)) & 0xff;
		|	pa = (pa ^ (pa >> 4)) & 0x0f;
		|	pa = (pa ^ (pa >> 2)) & 0x03;
		|	pa = (pa ^ (pa >> 1)) & 0x01;
		|	unsigned pb = uad & 0xbf00;
		|	pb = (pb ^ (pb >> 8)) & 0xff;
		|	pb = (pb ^ (pb >> 4)) & 0x0f;
		|	pb = (pb ^ (pb >> 2)) & 0x03;
		|	pb = (pb ^ (pb >> 1)) & 0x01;
		|
		|	PIN_APER<=(!pa && !pb);
		|
		|	if (PIN_CLK.posedge() && !PIN_CKEN=> && !PIN_SFST=>) {
		|		if (PIN_MODE=>) {
		|			state->wcs = state->ram[state->addr];
		|			PERMUTE(INVM);
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
		|			
		|			TOWCS();
		|		}
		|		TRACE(
		|		    << " mode " << PIN_MODE
		|		    << " diag " << BUS_DGI_TRACE()
		|		    << " wcs " << std::hex << state->wcs
		|		);
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|	if (!PIN_SUIR=>) {
		|		unsigned dout = 0;
		|		TOSR();
		|		dout |= (state->sr0 & 1) << 7;
		|		dout |= (state->sr1 & 1) << 6;
		|		dout |= (state->sr2 & 1) << 5;
		|		dout |= (state->sr3 & 1) << 4;
		|		dout |= (state->sr4 & 1) << 3;
		|		dout |= (state->ff5 & 0x40) >> 4;
		|		dout |= 0x3;
		|		BUS_DGO_WRITE(dout);
		|	} else if (PIN_SUIR.posedge()) {
		|		BUS_DGO_Z();
		|	}
		|	if (PIN_WE.posedge()) {
		|		state->ram[state->addr] = state->wcs;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUWCS", PartModel("XFIUWCS", XFIUWCS))
