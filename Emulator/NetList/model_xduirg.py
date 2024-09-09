#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   4096 (512 Words by 8 bits) PROM
   ===============================

'''

from part import PartModel, PartFactory

class XDUIRG(PartFactory):

    ''' 4096 (512 Words by 8 bits) PROM '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
                "adr_event",
                "BUS_A",
            )

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def state(self, file):
        ''' Extra state variable '''

        file.fmt('''
		|	uint8_t prom[512];
		|	uint8_t zeros;
		|	uint8_t ones;
		|''')

    def init(self, file):

        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom, sizeof state->prom, arg);
		|	state->zeros = 0xff;
		|	state->ones = 0x00;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned adr = 0;
		|	BUS_A_READ(adr);
		|	adr <<= 1;
		|	adr |= PIN_H1=>;
		|	if (PIN_CLK.posedge()) {
		|		output.d = state->prom[adr];
		|		TRACE(<< std::hex << " ADR " << adr << " D " << output.d);
		|		state->zeros &= output.d;
		|		state->ones |= output.d;
		|	}
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|	if (output.d == state->prom[adr] &&
		|	    output.d == state->prom[adr ^ 1])
		|		next_trigger(adr_event);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XDUIRG", PartModel("XDUIRG", XDUIRG))
