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
   F169 (Dual) D-Type Positive Edge-Triggered Flip-Flop
   ===================================================

   Ref: Fairchild DS009469 April 1988 Revised September 2000
'''

from part import PartModel, PartFactory

class F169(PartFactory):

    ''' F169 (Dual) D-Type Positive Edge-Triggered Flip-Flop '''

    autopin = True

    def state(self, file):
        ''' Extra state variable '''

        file.fmt('''
		|	uint32_t count;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        if "CO" not in self.comp.nodes:
            return
        if not self.comp.nodes["ENP"].net.is_const():
            yield "PIN_ENP"
        if not self.comp.nodes["ENT"].net.is_const():
            yield "PIN_ENT"
        if not self.comp.nodes["UP"].net.is_const():
            yield "PIN_UP"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_CLK.posedge()) {
		|		if (!PIN_LD=>) {
		|			BUS_D_READ(state->count);
		|		} else if (!PIN_ENP=> && !PIN_ENT=>) {
		|			if (PIN_UP=>) {
		|				state->count = (state->count + 0x1) & BUS_D_MASK;
		|			} else {
		|				state->count = (state->count + BUS_D_MASK) & BUS_D_MASK;
		|			}
		|		} else {
		|''')
        i = []
        if not self.comp.nodes["LD"].net.is_const():
            i.append("PIN_LD.negedge_event()")
        if not self.comp.nodes["ENP"].net.is_const():
            i.append("PIN_ENP.default_event()")
        if not self.comp.nodes["ENT"].net.is_const():
            i.append("PIN_ENT.default_event()")

        file.write("\t\t\tnext_trigger(%s);\n" % (" | ".join(i)))

        file.fmt('''
		|		}
		|	}
		|	output.q = state->count;
		|''')
        if "CO" in self.comp.nodes:
            file.fmt('''
		|	bool carry;
		|	if (PIN_ENT=>)
		|		carry = true;
		|	else if (PIN_UP=> && (state->count == BUS_D_MASK))
		|		carry = false;
		|	else if (!PIN_UP=> && (state->count == 0x0))
		|		carry = false;
		|	else
		|		carry = true;
		|	output.co = carry;
		|''')

class ModelF169(PartModel):
    ''' F169 counters '''

    def assign(self, comp, part_lib):

        co_node = comp["CO"]
        if len(co_node.net) == 1:
            print("CO not used", comp)
            co_node.remove()
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F169", ModelF169("F169", F169))
    part_lib.add_part("F169X2", ModelF169("F169X2", F169))
    part_lib.add_part("F169X4", ModelF169("F169X4", F169))
