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
   F194 4-bit bidirectional universal shift register
   =================================================

   Ref: Philips 1989 Apr 04, IC15 Data Handbook
'''

from part import PartModel, PartFactory

class F194(PartFactory):
    ''' F194 4-bit bidirectional universal shift register '''

    autopin = True

    def sensitive(self):
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"
        yield "PIN_CLK.pos()"

    def private(self):
        if not self.comp.nodes["CLR"].net.is_pu():
            yield from self.event_or(
                "idle_event",
                "BUS_S",
                "PIN_CLR",
            )
        else:
            yield from self.event_or(
                "idle_event",
                "BUS_S",
            )

    def state(self, file):
        ''' Extra state variable '''

        file.fmt('''
		|	unsigned out;
		|''')

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->out = BUS_D_MASK;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned mode = 0;
		|	BUS_S_READ(mode);
		|
		|	if (!PIN_CLR=>) {
		|		state->out = 0;
		|	} else if (PIN_CLK.posedge()) {
		|		switch (mode) {
		|		case 3:
		|			BUS_D_READ(state->out);
		|			break;
		|		case 2:
		|			state->out >>= 1;
		|			if (PIN_RSI=>)
		|				state->out |= (1<<(BUS_D_WIDTH-1));
		|			break;
		|		case 1:
		|			state->out <<= 1;
		|			state->out &= BUS_D_MASK;
		|			if (PIN_LSI=>)
		|				state->out |= (1<<0);
		|			break;
		|		case 0:
		|			break;
		|		}
		|	}
		|	output.q = state->out;
		|''')

    def doit_idle(self, file):
        if not self.comp.nodes["CLR"].net.is_pu():
            file.fmt('''
		|	if (!PIN_CLR=>) {
		|		next_trigger(PIN_CLR.posedge_event());
		|	} else
		|''')

        file.fmt('''
		|	if (state->idle > 10 && mode == 0) {
		|		state->idle = 0;
		|		next_trigger(idle_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F194", PartModel("F194", F194))
    part_lib.add_part("XSR8", PartModel("XSR8", F194))
    part_lib.add_part("XSR16", PartModel("XSR16", F194))
