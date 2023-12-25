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
   1MEG DRAM
   =========

'''

from part import PartModel, PartFactory
from pin import Pin
from net import Net
from node import Node
from component import Component

class DRAM1MEGWIDE(PartFactory):
    ''' 1MEGxN DRAM '''

    autopin = True
    autotrace = False

    def state(self, file):
        if len(self.comp.nodes) - 13 <= 16:
            file.fmt('''
		|	uint16_t bits[1 << 20];
		|	unsigned ras, cas;
		|''')
        else:
            file.fmt('''
		|	uint64_t bits[1 << 20];
		|	unsigned ras, cas;
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint32_t adr = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_RAS.negedge())
		|		state->ras = adr;
		|	if (PIN_CAS.negedge()) {
		|		state->cas = adr;
		|		adr = (state->cas << 10) | state->ras;
		|		if (!PIN_WE=>) {
		|			output.z_q = true;
		|			BUS_D_READ(state->bits[adr]);
		|		} else {
		|			output.z_q = false;
		|			output.q = state->bits[adr];
		|		}
		|	}
		|	if (PIN_RAS.posedge() || PIN_CAS.posedge()) {
		|		output.z_q = true;
		|	}
		|	if (!PIN_CAS=> || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << " ras " << PIN_RAS.negedge()
		|		    << " cas " << PIN_CAS.negedge()
		|		    << " we " << PIN_WE?
		|		    << " a " << BUS_A_TRACE()
		|		    << " ra " << std::hex << state->ras
		|		    << " ca " << std::hex << state->cas
		|		    << " d " << BUS_D_TRACE()
		|		);
		|	}
		|
		|''')


class DRAM1MEG(PartFactory):

    ''' 1MEG DRAM '''

    def state(self, file):
        file.fmt('''
		|	unsigned ras, cas;
		|	uint32_t bits[(1<<20)>>5];
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint32_t adr = 0, data = 0, mask = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_RAS.negedge())
		|		state->ras = adr;
		|	if (PIN_CAS.negedge()) {
		|		state->cas = adr;
		|		adr = (state->cas << 10) | state->ras;
		|		mask = 1 << (adr & 0x1f);
		|		adr >>= 5;
		|		if (!PIN_WE=>) {
		|			PIN_DQ = sc_dt::sc_logic_Z;
		|			if (PIN_DQ=>)
		|				state->bits[adr] |= mask;
		|			else
		|				state->bits[adr] &= ~mask;
		|		} else {
		|			data = (state->bits[adr] & mask) != 0;
		|			PIN_DQ = AS(data);
		|		}
		|	}
		|	if (PIN_RAS.posedge() || PIN_CAS.posedge()) {
		|		PIN_DQ = sc_dt::sc_logic_Z;
		|	}
		|	if (!PIN_CAS=> || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << " ras " << PIN_RAS?
		|		    << " cas " << PIN_CAS?
		|		    << " we " << PIN_WE?
		|		    << " a " << BUS_A_TRACE()
		|		    << " dq " << PIN_DQ?
		|		    << " ras " << std::hex << state->ras
		|		    << " cas " << std::hex << state->cas
		|		    << " data " << std::hex << data
		|		    << " mask " << std::hex << mask
		|		);
		|	}
		|
		|''')

class Model1Meg(PartModel):
    ''' 1MEG DRAM '''

    def assign(self, comp, part_lib):

        node = comp["D"]
        node.remove()
        node = comp["Q"]
        node.remove()
        node.pin.name = "DQ"
        node.pin.set_role("bidirectional")
        node.insert()

        super().assign(comp, part_lib)

class ModelWide(PartModel):
    ''' 1MEGxN DRAM '''

    def assign(self, comp, part_lib):

        for node in comp.iter_nodes():
            if node.pin.name[:2] != "DQ":
                continue
            Node(node.net, comp, Pin("d", "D" + node.pin.name[2:], "input"))
            Node(node.net, comp, Pin("q", "Q" + node.pin.name[2:], "tri_state"))
            node.remove()
        inv_comp = Component(
            compref = comp.ref + "_INV",
            compvalue = comp.value,
            comppart = "F00",
        )
        comp.scm.add_component(inv_comp)
        inv_comp.name = comp.name + "_INV"
        inv_comp.part = part_lib[inv_comp.partname]

        Node(comp["WE"].net, inv_comp, Pin("D0", "D0", "input"))
        Node(comp["WE"].net, inv_comp, Pin("D1", "D1", "input"))

        inv_net = Net(comp.name + "_OE")
        comp.scm.add_net(inv_net)
        Node(inv_net, inv_comp, Pin("Q", "Q", "output"))
        Node(inv_net, comp, Pin("OE", "OE", "input"))

        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("1MEG", Model1Meg("1MEG", DRAM1MEG))
    part_lib.add_part("XDRAM", ModelWide("XDRAM", DRAM1MEGWIDE))
    part_lib.add_part("XERAM", ModelWide("XERAM", DRAM1MEGWIDE))
