#!/usr/local/bin/python3
#
# Copyright (c) 2022 Poul-Henning Kamp
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
   Model the NOR components
   =========================
'''

from part import Part, PartFactory

import util

class Nor(PartFactory):

    ''' A generic N-input NOR component '''

    def __init__(self, ident, inputs):
        super().__init__(ident)
        self.inputs = inputs

    def pin_iterator(self):
        ''' SC pin declarations '''

        for node in self.comp:
            if node.pin.name == "Q" and node.net.sc_type == "bool":
                yield "sc_core::sc_out <bool>\t\tPIN_Q;"
            elif node.pin.name == "Q":
                yield "sc_core::sc_out <sc_dt::sc_logic>\tPIN_Q;"
            elif node.net.sc_type == "bool":
                yield "sc_core::sc_in <bool>\t\tPIN_%s;" % node.pin.name
            else:
                yield "sc_core::sc_in <sc_dt::sc_logic>\tPIN_%s;" % node.pin.name

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tint job;\n")
        file.write("\tint out;\n")
        file.write("\tunsigned dly;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->out = -1;
		|	state->job = 0;
		|	state->dly = 5;
		|''')

    def sensitive(self):
        ''' sensitivity list '''

        for i in range(self.inputs):
            yield "PIN_D%d" % i

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)
        if self.name[0] == "N":
            file.add_subst("«on»", "1")
            file.add_subst("«off»", "0")
        else:
            file.add_subst("«on»", "0")
            file.add_subst("«off»", "1")

        file.fmt('''
		|
		|	if (state->dly) {
		|		TRACE(
		|		    << " job " << state->job
		|		    << " d " << BUS_D_TRACE()
		|		    << " out " << state->out
		|		);
		|	}
		|
		|	if (state->job) {
		|		PIN_Q<=(state->out);
		|		state->job = false;
		|	}
		|
		|	unsigned tmp;
		|	BUS_D_READ(tmp);
		|	if (!tmp) {
		|		if (state->out != «on») {
		|			state->out = «on»;
		|			if (state->dly == 0) {
		|				TRACE(
		|				    << " job " << state->job
		|				    << " d " << BUS_D_TRACE()
		|				    << " out " << state->out
		|				);
		|				PIN_Q<=(state->out);
		|			} else {
		|				state->job = true;
		|				next_trigger(state->dly, sc_core::SC_NS);
		|			}
		|		}
		|	} else {
		|		if (state->out != «off») {
		|			state->out = «off»;
		|			if (state->dly == 0) {
		|				TRACE(
		|				    << " job " << state->job
		|				    << " d " << BUS_D_TRACE()
		|				    << " out " << state->out
		|				);
		|				PIN_Q<=(state->out);
		|			} else {
		|				state->job = true;
		|				next_trigger(state->dly, sc_core::SC_NS);
		|			}
		|''')

        for node in self.comp:
            if node.pin.name != "Q":
                file.fmt("\t\t} else if (PIN_%s=>) {\n" % node.pin.name)
                file.fmt("\t\t\tnext_trigger(PIN_%s.default_event());\n" % node.pin.name)

        file.fmt('''
		|		}
		|	}
		|''')

    def hookup(self, file, comp):
        pno = 0
        for node in comp:
            if node.pin.name == "Q":
                file.write("\t%s.PIN_Q(%s);\n" % (comp.name, node.net.cname))
            else:
                file.write("\t%s.PIN_D%d(%s);\n" % (comp.name, pno, node.net.cname))
                pno += 1

class ModelNor(Part):
    ''' Model NOR components '''

    def assign(self, comp, part_lib):
        ''' Assigned to component '''
        seen = set()
        n_inputs = 0
        for node in comp:
            if node.net.is_pd():
                # print("NOR with PD", node)
                node.remove()
                continue
            if node.net in seen:
                # print("NOR multiple", node)
                node.remove()
                continue
            seen.add(node.net)
            if node.pin.name == "Q":
                node.pin.set_role("output")
            else:
                node.pin.name = "D%d" % n_inputs
                node.pin.set_role("input")
                node.pin.update()
                n_inputs += 1
        assert n_inputs > 0, (comp, [x for x in comp])
        if n_inputs == 1:
            # print("NOR -> INV", comp)
            comp.partname = "F37"
            comp.part = part_lib[comp.partname]
            comp.part.assign(comp, part_lib)

    def configure(self, comp, part_lib):
        i = []
        j = 0
        for node in comp:
            if node.pin.name != "Q":
                node.pin.name = "D%d" % j
                j += 1
            if node.net.sc_type == "bool":
                i.append("B")
            else:
                i.append("L")
        inputs = len(comp.nodes) - 1
        sig = util.signature(i)
        ident = self.name + "%d_" % inputs + sig
        if ident not in part_lib:
            part_lib.add_part(ident, Nor(ident, inputs))
        comp.part = part_lib[ident]

def register(part_lib):
    ''' Register component model '''
    part_lib.add_part("F02", ModelNor("NOR"))
    part_lib.add_part("F32", ModelNor("OR"))
    part_lib.add_part("F260", ModelNor("NOR"))
    part_lib.add_part("NOR1", ModelNor("NOR"))
    part_lib.add_part("NOR2", ModelNor("NOR"))
    part_lib.add_part("NOR3", ModelNor("NOR"))
    part_lib.add_part("NOR4", ModelNor("NOR"))
