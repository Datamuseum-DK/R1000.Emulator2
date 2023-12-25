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
   F113 (Dual) JK Negative Edge-Triggered Flip-Flop
   ================================================

   Ref: Fairchild DS009473 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F113(PartFactory):

    ''' F113 (Dual) JK Negative Edge-Triggered Flip-Flop '''

    def sensitive(self):
        yield "PIN_CLK_.neg()"
        if not self.comp.nodes["PR_"].net.is_const():
            yield "PIN_PR_"

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tbool dreg;\n")
        file.write("\tint job;\n")

    def init(self, file):
        file.write("\tstate->job = 1;\n")
        file.write("\tstate->dreg = 0;\n")

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what;
		|	bool nxt = state->dreg;
		|
		|	TRACE(
		|	    << state->job
		|	    << " clk↓ " << PIN_CLK_.negedge()
		|	    << " k " << PIN_K?
		|	    << " j " << PIN_J?
		|	    << " pr " << PIN_PR_?
		|	    << " q "
		|	    << state->dreg
		|	);
		|	if (state->job) {
		|		PIN_Q<=(state->dreg);
		|		PIN_Q_<=(!state->dreg);
		|		state->job = 0;
		|	}
		|
		|	if (!PIN_PR_=>) {
		|		what = " PR ";
		|		nxt = true;
		|	} else if (!PIN_CLK_.negedge()) {
		|		what = " ? ";
		|	} else if (PIN_J=> && PIN_K=>) {
		|		what = " inv ";
		|		nxt = !state->dreg;
		|	} else if (!PIN_J=> && PIN_K=>) {
		|		what = " clr ";
		|		nxt = false;
		|	} else if (PIN_J=> && !PIN_K=>) {
		|		what = " set ";
		|		nxt = true;
		|	} else {
		|		what = " nop ";
		|		next_trigger(PIN_J.posedge_event() | PIN_K.posedge_event());
		|	}
		|	if (nxt != state->dreg) {
		|		state->job = 1;
		|		state->dreg = nxt;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F113", PartModel("F113", F113))
