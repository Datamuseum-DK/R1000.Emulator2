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
   SEQ FIU parity
   ==============

'''

from part import PartModel, PartFactory

class XFIUPAR(PartFactory):
    ''' SEQ FIU parity '''

    def state(self, file):
        file.fmt('''
		|	bool perr;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		PIN_FPERR<=(state->perr);
		|		state->ctx.job = 0;
		|		return;
		|	}
		|
		|	uint32_t fiu, fiup, par;
		|
		|	BUS_FIU_READ(fiu);
		|	BUS_FIUP_READ(fiup);
		|
		|	par = fiu;
		|	par = (par ^ (par >> 4)) & 0x0f0f0f0f;
		|	par = (par ^ (par >> 2)) & 0x03030303;
		|	par = (par ^ (par >> 1)) & 0x01010101;
		|	par = (par >> 7) | (par & 1);
		|	par = (par >> 7) | (par & 3);
		|	par = (par >> 7) | (par & 7);
		|	bool perr = par != (fiup & 0xf);
		|	if (perr != state->perr) {
		|		state->ctx.job = 1;
		|		state->perr = perr;
		|		next_trigger(5, SC_NS);
		|		TRACE(
		|		    << " fiu " << BUS_FIU_TRACE()
		|		    << " fiup " << BUS_FIUP_TRACE()
		|		    << std::hex 
		|		    << " par " << par
		|		    << " perr " << perr
		|		);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUPAR", PartModel("XFIUPAR", XFIUPAR))
