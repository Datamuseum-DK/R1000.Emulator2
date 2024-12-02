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
		|	BUS_UAD_READ(state->addr);
		|
		|	if (PIN_UCLK.posedge()) {
		|		state->wcs = state->ram[state->addr];
		|		state->wcs |= (1ULL << 63);
		|		state->wcs ^= 0x7fffc0000000ULL;
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
