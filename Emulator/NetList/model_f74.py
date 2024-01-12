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

    autopin = True

    def private(self):
        l = [ "PIN_D" ]
        if "PR_" in self.comp:
            l.append("PIN_PR_")
        if "CL_" in self.comp:
            l.append("PIN_CL_")
        yield from self.event_or(
            "idle_event",
            *l,
        )

    def sensitive(self):
        yield "PIN_CLK.pos()"
        if "PR_" in self.comp:
            yield "PIN_PR_"
        if "CL_" in self.comp:
            yield "PIN_CL_"

    def state(self, file):
        file.write("\tbool dreg[2];\n")

    def init(self, file):

        file.fmt('''
		|	state->dreg[0] = true;
		|	state->dreg[1] = false;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (0) {
		|''')

        if "PR_" in self.comp and "CL_" in self.comp:
            file.fmt('''
		|	} else if (!(PIN_CL_=>) && !(PIN_PR_=>)) {
		|		state->dreg[0] = true;
		|		state->dreg[1] = true;
		|''')

        elif "PR_" in self.comp:
            file.fmt('''
		|	} else if (!PIN_PR_=>) {
		|		state->dreg[0] = true;
		|		state->dreg[1] = false;
		|''')

        elif "CL_" in self.comp:
            file.fmt('''
		|	} else if (!PIN_PR_=>) {
		|		state->dreg[0] = false;
		|		state->dreg[1] = true;
		|''')

        file.fmt('''
		|	} else if (PIN_CLK.posedge()) {
		|		state->dreg[0] = PIN_D=>;
		|		state->dreg[1] = !state->dreg[0];
		|	}
		|''')

        if "Q" in self.comp:
            file.fmt('''
		|	output.q = state->dreg[0];
		|''')

        if "Q_" in self.comp:
            file.fmt('''
		|	output.q_ = state->dreg[1];
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|	if (state->idle > 10 && state->dreg[0] == PIN_D=>) {
		|		state->idle = 0;
		|		next_trigger(idle_event);
		|	}
		|''')


class ModelF74(PartModel):
    ''' ... '''

    def assign(self, comp, part_lib):
        if comp["CL_"].net.is_pu():
            comp["CL_"].remove()
        if comp["PR_"].net.is_pu():
            comp["PR_"].remove()
        if len(comp["Q"].net) == 1:
            comp["Q"].remove()
        if len(comp["Q_"].net) == 1:
            comp["Q_"].remove()
        assert not comp["CLK"].net.is_const()
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F74", ModelF74("F74", F74))
