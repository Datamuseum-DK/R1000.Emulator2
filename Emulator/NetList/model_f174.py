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

    ''' F174 9-Bit Parity Generator Checker '''

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
        if self.comp["CLK"].net.is_const():
            return
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        if self.comp["CLK"].net.is_const():
            return
        super().doit(file)

        file.fmt('''
		|
		|	const char *what = "";
		|	unsigned nxt;
		|
		|	TRACE(
		|	    << what
		|	    << " clr_" << PIN_CLR?
		|	    << " clk " << PIN_CLK?
		|	    << " d " << BUS_D_TRACE()
		|	    << " | " << std::hex << state->dreg
		|	);
		|	if (state->job) {
		|		BUS_Q_WRITE(state->dreg);
		|		state->job = 0;
		|	}
		|	if (!PIN_CLR=>) {
		|		nxt = 0;
		|		what = " CLR ";
		|	} else if (PIN_CLK.posedge()) {
		|		BUS_D_READ(nxt);
		|		what = " CLK ";
		|	} else {
		|		nxt = state->dreg;
		|		what = " ??? ";
		|	}
		|	if (nxt != state->dreg) {
		|		state->job = 1;
		|		state->dreg = nxt;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F174", PartModel("F174", F174))
