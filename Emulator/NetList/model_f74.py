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
   F74 (Dual) D-Type Positive Edge-Triggered Flip-Flop
   ===================================================

   Ref: Fairchild DS009469 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F74(PartFactory):

    ''' F74 (Dual) D-Type Positive Edge-Triggered Flip-Flop '''

    def sensitive(self):
        if self.comp["CLK"].net.is_const():
            return
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["PR_"].net.is_const():
            yield "PIN_PR_"
        if not self.comp.nodes["CL_"].net.is_const():
            yield "PIN_CL_"

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tbool dreg[2];\n")
        file.write("\tint job;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->job = 1;
		|	state->dreg[0] = true;
		|	state->dreg[1] = false;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        if self.comp["CLK"].net.is_const():
            return
        super().doit(file)

        events = []
        if not self.comp.nodes["PR_"].net.is_const():
            events.append("PIN_PR_.default_event()")
        if not self.comp.nodes["CL_"].net.is_const():
            events.append("PIN_CL_.default_event()")

        file.add_subst("«pr_or_cl»", " | ".join(events))

        if not self.comp.nodes["D"].net.is_const():
            events.append("PIN_D.default_event()")

        file.add_subst("«d_or_pr_or_cl»", " | ".join(events))

        # file.write("\t\tnext_trigger(%s);\n" % (" | ".join(i)))
        file.fmt('''
		|	bool oldreg[2], now;
		|	const char *what = " ? ";
		|
		|	if (state->job) {
		|		PIN_Q<=(state->dreg[0]);
		|		PIN_Q_<=(state->dreg[1]);
		|		state->job = 0;
		|	}
		|	memcpy(oldreg, state->dreg, sizeof oldreg);
		|	if (!(PIN_CL_=>) && !(PIN_PR_=>)) {
		|		if (!state->dreg[0] || !state->dreg[1]) {
		|			state->dreg[0] = state->dreg[1] = true;
		|			state->job = 1;
		|			what = " 2L ";
		|		} else {
		|			next_trigger(«pr_or_cl»);
		|		}
		|	} else if (!(PIN_CL_=>)) {
		|		if (state->dreg[0]) {
		|			state->dreg[0] = false;
		|			state->dreg[1] = true;
		|			state->job = 1;
		|		} else {
		|			next_trigger(«pr_or_cl»);
		|		}
		|		what = " CLR ";
		|	} else if (!(PIN_PR_=>)) {
		|		if (!state->dreg[0]) {
		|			state->dreg[0] = true;
		|			state->dreg[1] = false;
		|			state->job = 1;
		|		} else {
		|			next_trigger(«pr_or_cl»);
		|		}
		|		what = " SET ";
		|	} else if (PIN_CLK.posedge()) {
		|		now = PIN_D=>;
		|		if (state->dreg[0] != now) {
		|			state->dreg[0] = now;
		|			state->dreg[1] = !now;
		|			state->job = 1;
		|			what = " CHG ";
		|		}
		|	}
		|	if (memcmp(oldreg, state->dreg, sizeof oldreg) || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << what
		|		    << " clr " << PIN_CL_=>
		|		    << " set " << PIN_PR_=>
		|		    << " data " << PIN_D=>
		|		    << " clk " << PIN_CLK=>
		|		    << " job " << state->job
		|		    << " | "
		|		    << state->dreg[0]
		|		    << state->dreg[1]
		|		);
		|	}
		|	if (state->job)
		|		next_trigger(5, sc_core::SC_NS);
		|	else if (!(PIN_D=> ^ state->dreg[0]))
		|		next_trigger(«d_or_pr_or_cl»);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F74", PartModel("F74", F74))
