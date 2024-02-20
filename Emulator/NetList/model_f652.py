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
   F652 Transceivers/Registers
   ===========================

   Ref: Fairchild DS009581 March 1988, Revised January 2004
'''


from part import PartModel, PartFactory
from component import Component
from node import Node
from pin import Pin
from net import Net

class F652H(PartFactory):
    ''' Half Part'''

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "z_event",
            "PIN_CLK.posedge_event()",
            "PIN_OE",
        )
        yield from self.event_or(
            "s_event",
            "PIN_CLK.posedge_event()",
            "PIN_OE",
            "PIN_S",
        )

    def state(self, file):
        file.fmt('''
		|	uint64_t reg;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_OE"
        yield "PIN_S"
        yield "BUS_I_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t tmp;
		|	bool read = false;
		|	
		|	TRACE(
		|	    << " j " << state->ctx.job
		|	    << " c " << PIN_CLK
		|	    << " s " << PIN_S
		|	    << " o " << PIN_OE
		|	    << " i " << BUS_I_TRACE()
		|	    << " y " << BUS_Y_TRACE()
		|	    << " r " << std::hex << state->reg
		|	);
		|	if (PIN_CLK.posedge()) {
		|		BUS_I_READ(tmp);
		|		state->reg = tmp;
		|		read = true;
		|		TRACE(" r " << BUS_I_TRACE());
		|	}
		|	if (PIN_OE=>) {
		|		TRACE(" Z");
		|		BUS_Y_Z();
		|		next_trigger(z_event);
		|	} else if (PIN_S=>) {
		|		BUS_Y_WRITE(state->reg);
		|		TRACE(" o " << std::hex << state->reg);
		|		next_trigger(s_event);
		|	} else {
		|		if (!read)
		|			BUS_I_READ(tmp);
		|		BUS_Y_WRITE(tmp);
		|		TRACE(" i " << BUS_I_TRACE() << " " << std::hex << tmp);
		|	}
		|''')

class ModelF652(PartModel):
    ''' F652 Transceivers/Registers '''

    def assign(self, comp, part_lib):
        ''' Split into four separate components '''

        inv = Component(
            compref = comp.ref + "_I",
            compvalue = comp.value,
            comppart = "F00",
        )
        comp.scm.add_component(inv)
        inv.name = comp.name + "_I"
        inv.part = part_lib[inv.partname]

        node = comp["OEB"]
        new_pin = Pin("d", "D", "input")
        Node(node.net, inv, new_pin)

        new_pin = Pin("q", "Q", "output")
        new_net = Net(self.name + "_" + comp.name + "_I")
        comp.scm.add_net(new_net)
        Node(new_net, inv, new_pin)

        pin = node.pin
        node.remove()
        new_node = Node(new_net, comp, pin)

        inv.part.assign(inv, part_lib)

        for suff in ("_AB", "_BA",):
            new_comp = Component(
                compref = comp.ref + suff,
                compvalue = comp.value,
                comppart = comp.partname + "_H",
            )
            comp.scm.add_component(new_comp)
            new_comp.name = comp.name + suff
            new_comp.part = part_lib[new_comp.partname]
            new_comp.part.assign(new_comp, part_lib)
            for node in comp.nodes.values():
                if node.pin.name[0] == suff[2]:
                    new_pin = Pin("Y" + node.pin.ident[1:], "Y" + node.pin.name[1:], "tri_state")
                elif node.pin.name[0] == suff[1]:
                    new_pin = Pin("I" + node.pin.ident[1:], "I" + node.pin.name[1:], "input")
                elif node.pin.name == "C" + suff[1:]:
                    new_pin = Pin(node.pin.ident, "CLK", "input")
                elif node.pin.name == "S" + suff[1:]:
                    new_pin = Pin(node.pin.ident, "S", "input")
                elif node.pin.name == "OE" + suff[-1]:
                    new_pin = Pin(node.pin.ident, "OE", "input")
                else:
                    continue

                new_node = Node(
                    node.net,
                    new_comp,
                    new_pin,
                )

        comp.eliminate()


class F652(PartFactory):

    ''' F652 Transceivers/Registers '''

    def state(self, file):
        file.fmt('''
		|	uint64_t areg, breg;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t a = 0;
		|	uint64_t b = 0;
		|	char what[12];
		|
		|	what[0] = '\\0';
		|
		|	if (!PIN_OEA=> && PIN_OEB=> && !PIN_SAB=> && !PIN_SBA=>) {
		|		/* ignore "passive latch" which happens during startup */
		|		TRACE("latch a " << BUS_A_TRACE() << " b " << BUS_B_TRACE());
		|		return;
		|	}
		|
		|	if (PIN_OEA=>) {
		|		BUS_A_Z();
		|		BUS_A_READ(a);
		|		strcat(what, "Ai");
		|	} else if (PIN_SBA=>) {
		|		strcat(what, "Ar");
		|		a = state->breg;
		|	} else {
		|		strcat(what, "Ab");
		|		BUS_B_READ(a);
		|	}
		|
		|	if (!PIN_OEB=>) {
		|		BUS_B_Z();
		|		BUS_B_READ(b);
		|		strcat(what, "Bi");
		|	} else if (PIN_SAB=>) {
		|		strcat(what, "Br");
		|		b = state->areg;
		|	} else {
		|		strcat(what, "Ba");
		|		BUS_A_READ(b);
		|	}
		|
		|	if (PIN_CAB.posedge()) {
		|		state->areg = a;
		|		strcat(what, "A<");
		|	}
		|
		|	if (PIN_CBA.posedge()) {
		|		state->breg = b;
		|		strcat(what, "B<");
		|	}
		|
		|	if (!PIN_OEA=>)
		|		BUS_A_WRITE(a);
		|
		|	if (PIN_OEB=>)
		|		BUS_B_WRITE(b);
		|
		|	TRACE(
		|	    << what
		|	    << " oea " << PIN_OEA?
		|	    << " oeb " << PIN_OEB?
		|	    << " sab " << PIN_SAB?
		|	    << " sba " << PIN_SBA?
		|	    << " cab " << PIN_CAB.posedge()
		|	    << " cba " << PIN_CBA.posedge()
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " | a "
		|	    << std::hex << a
		|	    << " ra "
		|	    << std::hex << state->areg
		|	    << " b "
		|	    << std::hex << b
		|	    << " rb "
		|	    << std::hex << state->breg
		|	);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    for width in ("", "_9", "_64",):
        dev = "F652" + width
        part_lib.add_part(dev, ModelF652(dev, F652))
        part_lib.add_part(dev + "_H", PartModel(dev + "_H", F652H))
