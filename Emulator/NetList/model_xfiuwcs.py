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
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_CLK.posedge() && !PIN_SFST=>) {
		|		unsigned addr;
		|		BUS_UAD_READ(addr);
		|
		|		uint64_t wcs = state->ram[addr];
		|
		|		output.ofsl = (wcs >> 40) & BUS_OFSL_MASK;
		|		output.lfl = (wcs >> 32) & BUS_LFL_MASK;
		|		output.lfcn = (wcs >> 30) & BUS_LFCN_MASK;
		|		output.opsl = (wcs >> 28) & BUS_OPSL_MASK;
		|		output.vmsl = (wcs >> 26) & BUS_VMSL_MASK;
		|		output.fill = (wcs >> 25) & 1;
		|		output.osrc = (wcs >> 24) & 1;
		|		//output.tivi = (wcs >> 20) & BUS_TIVI_MASK;
		|		output.ldo = (wcs >> 19) & 1;
		|		output.ldv = (wcs >> 18) & 1;
		|		output.ldt = (wcs >> 17) & 1;
		|		output.ldm = (wcs >> 16) & 1;
		|		output.mstr = (wcs >> 10) & BUS_MSTR_MASK;
		|		output.rsrc = (wcs >> 9) & 1;
		|		output.lsrc = (wcs >> 1) & 1;
		|		output.ofsrc = (wcs >> 0) & 1;
		|
		|		unsigned tvoe = 0x00;
		|
		|		unsigned tivi = (wcs >> 20) & 0xf;
		|
		|		switch(tivi & 3) {
		|		case 0x0: tvoe |= 0x08; break;	// VAR_VI
		|		case 0x1: tvoe |= 0x04; break;	// VAL_VI
		|		case 0x2: tvoe |= 0x0a; break;	// FIU_VI+VAR_VI
		|		case 0x3: tvoe |= 0x01; break;	// FRAME_ADR
		|		}
		|
		|		switch(tivi & 0xc) {
		|		case 0x0: tvoe |= 0x80; break;	// TAR_TI
		|		case 0x4: tvoe |= 0xc0; break;	// FIU_TI+TAR_TI
		|		case 0x8: tvoe |= 0x20; break;	// TYPE_TI
		|		case 0xc:
		|			tvoe = 0x10;	// MAR
		|			break;
		|		}
		|		output.tvoe = tvoe ^ 0xff;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUWCS", PartModel("XFIUWCS", XFIUWCS))
