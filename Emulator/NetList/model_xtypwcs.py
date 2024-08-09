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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_UAD_WIDTH];
		|	unsigned addr;
		|	uint64_t wcs;
		|''')

    def sensitive(self):
        yield "PIN_UCLK.pos()"
        yield "BUS_UAD"

    def doit(self, file):
        ''' The meat of the doit() function '''

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
		|#define INVM(wcsbit, srnam, srbit, inv) state->wcs ^= (uint64_t)inv << BUS_UIR_LSB(wcsbit);
		|
		|	BUS_UAD_READ(state->addr);
		|
		|	if (PIN_UCLK.posedge()) {
		|		state->wcs = state->ram[state->addr];
		|		state->wcs |= (1ULL << 63);
		|		PERMUTE(INVM);
		|		output.uir = state->wcs;
		|	}
		|
		|	unsigned csacntl0 = (state->ram[state->addr] >> BUS_UIR_LSB(45)) & 7;
		|	unsigned csacntl1 = (state->wcs >> BUS_UIR_LSB(45)) & 6;
		|	output.fpdt = !(
		|		(csacntl0 == 7) &&
		|		(csacntl1 == 0)
		|	);
		|
		|	uint64_t tmp = state->ram[state->addr];
		|	unsigned aadr = (tmp >> BUS_UIR_LSB(5)) & 0x3f;
		|	output.ald = (aadr == 0x13);
		|	unsigned badr = (tmp >> BUS_UIR_LSB(11)) & 0x3f;
		|	output.bld = (badr == 0x13);
		|
		|	unsigned clit = 0;
		|	clit |= (state->wcs >> BUS_UIR_LSB(16)) & 0x1f;
		|	clit |= ((state->wcs >> BUS_UIR_LSB(18)) & 0x3) << 5;
		|	output.clit = clit;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTYPWCS", PartModel("XTYPWCS", XTYPWCS))
