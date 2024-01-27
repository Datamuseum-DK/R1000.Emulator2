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
   TV RF parity RAM
   ================

'''

from part import PartModel, PartFactory

class XTVPAR(PartFactory):
    ''' TV RF parity RAM '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t apar[1 << BUS_AADR_WIDTH];
		|	uint8_t bpar[1 << BUS_BADR_WIDTH];
		|	unsigned aaddr, baddr, cchk;
		|''')

    def sensitive(self):
        yield "PIN_CLKQ2.pos()"
        yield "PIN_CLKQ4.pos()"
        yield "PIN_AWE.pos()"
        yield "PIN_BWE.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_CLKQ2.posedge()) {
		|		BUS_AADR_READ(state->aaddr);
		|		BUS_BADR_READ(state->baddr);
		|	}
		|	if (PIN_CLKQ4.posedge()) {
		|		BUS_AADR_READ(state->aaddr);
		|		BUS_BADR_READ(state->baddr);
		|		BUS_CCHK_READ(state->cchk);
		|	}
		|	if (PIN_AWE.posedge()) {
		|		state->apar[state->aaddr] = state->cchk;
		|	}
		|	if (PIN_BWE.posedge()) {
		|		state->bpar[state->baddr] = state->cchk;
		|	}
		|	output.apar = (state->apar[state->aaddr]);
		|	BUS_APAR_WRITE(output.apar);
		|	output.bpar = (state->bpar[state->baddr]);
		|	BUS_BPAR_WRITE(output.bpar);
		|	
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVPAR", PartModel("XTVPAR", XTVPAR))
