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
   F174 Hex D-Type Flip-Flop with Master Reset
   ===========================================

   Ref: Fairchild DS009489 April 1988 Revised September 2000
'''

from part import PartModel, PartFactory

class F174(PartFactory):

    ''' F174 Hex D-Type Flip-Flop with Master Reset '''

    autopin = True

    def state(self, file):
        ''' Extra state variable '''
        file.fmt('''
		|       unsigned idle;
		|''')

    def private(self):
        ''' private variables '''
        if self.comp.nodes["CLR"].net.is_pu():
            yield from self.event_or(
                "idle_event",
                "BUS_D",
            )
        else:
            yield from self.event_or(
                "idle_event",
                "PIN_CLR",
                "BUS_D",
            )

    def sensitive(self):
        assert not self.comp["CLK"].net.is_const()
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (!PIN_CLR=>) {
		|		output.q = 0;
		|	} else if (PIN_CLK.posedge()) {
		|		BUS_D_READ(output.q);
		|	}
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|       if (++state->idle > 100) {
		|               state->idle = 0;
		|		unsigned tmp;
		|		BUS_D_READ(tmp);
		|		if (tmp == output.q)
		|               	next_trigger(idle_event);
		|       }
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F174", PartModel("F174", F174))
