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
   F175 D-Type Flip-Flop
   ===================================

   Ref: Fairchild DS009490 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F175(PartFactory):

    ''' F175 D-Type Flip-Flop '''

    def state(self, file):
        file.fmt('''
		|	unsigned dreg;
		|	int job;
		|''')

    def init(self, file):
        file.fmt('''
		|	state->job = 1;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	unsigned nxt;
		|
		|	if (state->job || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << " job " << state->job
		|		    << " clr_ " << PIN_CLR?
		|		    << " clk " << PIN_CLK?
		|		    << " d "
		|		    << BUS_D_TRACE()
		|		    << " | "
		|		    << std::hex << state->dreg
		|		);
		|	}
		|	if (state->job) {
		|		BUS_Q_WRITE(state->dreg);
		|		PIN_Q0not<=(!(state->dreg & 8));
		|		PIN_Q1not<=(!(state->dreg & 4));
		|		PIN_Q2not<=(!(state->dreg & 2));
		|		PIN_Q3not<=(!(state->dreg & 1));
		|		state->job = 0;
		|	}
		|	nxt = state->dreg;
		|	if (!PIN_CLR=>) {
		|		nxt = 0;
		|	} else if (PIN_CLK.posedge()) {
		|		BUS_D_READ(nxt);
		|	}
		|	if ( nxt != state->dreg) {
		|		state->dreg = nxt;
		|		state->job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F175", PartModel("F175", F175))
