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
		|	uint64_t *ram;
		|	uint64_t wcs, ff1, ff2, ff3, sr0, sr1, sr2, sr4;
		|''')

    def init(self, file):
        file.fmt('''
		|	state->ram = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
		|''')

    def sensitive(self):
        yield "BUS_UAD"
        yield "PIN_UCLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned uad;
		|	BUS_UAD_READ(uad);
		|
		|	if (PIN_UCLK.posedge()) {
		|		state->wcs = state->ram[uad];
		|		state->wcs ^= 0xffff800000;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	} 
		|
		|	output.uir = state->wcs;
		|
		|	uint64_t tmp = state->ram[uad];
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
