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
   F24[04] Octal buffers (3-state)
   ===============================

   Ref: Philips IC15 1994 Dec 05
'''

from part import PartModel, PartFactory, optimize_oe_output
from component import Component

class Xbuf(PartFactory):

    ''' F24[04] Octal buffers (3-state) '''

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint64_t data;\n")
        file.write("\tint job;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->job = -1;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t tmp;
		|
		|	if (state->ctx.do_trace & 2) {
		|		TRACE(
		|			<< " job " << state->job
		|''')

        if "OE" in self.comp:
            file.fmt('''
		|			<< " oe " << PIN_OE?
		|''')

        file.fmt('''
		|			<< " i " << BUS_I_TRACE()
		|		);
		|	}
		|	if (state->job > 0) {
		|		tmp = state->data;
		|''')

        if self.name[-2:] == "_I":
            file.fmt('''
		|		tmp ^= BUS_I_MASK;
		|''')

        file.fmt('''
		|		TRACE(<< " out " << std::hex << tmp);
		|		BUS_Y_WRITE(tmp);
		|		state->job = 0;
		|''')

        if "OE" not in self.comp or self.comp.nodes["OE"].net.is_pd():
            file.fmt('''
		|	}
		|
		|	BUS_I_READ(tmp);
		|	if (tmp != state->data || state->job < 0) {
		|		state->data = tmp;
		|		state->job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')
        else:
            file.fmt('''
		|	} else if (state->job < 0) {
		|		BUS_Y_Z();
		|	}
		|
		|	if (PIN_OE=>) {
		|		BUS_Y_Z();
		|		state->job = -1;
		|		next_trigger(PIN_OE.negedge_event());
		|	} else {
		|		BUS_I_READ(tmp);
		|		if (tmp != state->data || state->job < 0) {
		|			state->data = tmp;
		|			state->job = 1;
		|			next_trigger(5, SC_NS);
		|		}
		|	}
		|''')

class ModelXbuf(PartModel):
    ''' Xbuf registers '''

    def __init__(self, invert):
        super().__init__("XBUF")
        self.invert = invert

    def assign(self, comp, part_lib):
        for node in comp:
            if node.pin.name[0] != 'Y':
                node.pin.set_role("input")
        if "OE0" in comp:
            self.f24x(comp)
        else:
            oe_node = comp["OE"]
            if oe_node.net.is_pd():
                oe_node.remove()
                for node in comp:
                    if node.pin.name[0] == "Y":
                        node.pin.set_role("output")
            super().assign(comp, part_lib)

    def f24x(self, comp):
        ''' Special-case F240 and F244 '''
        oenode0 = comp["OE0"]
        oenode1 = comp["OE1"]
        if oenode0.net == oenode1.net:
            oenode1.remove()
            oenode0.remove()
            if oenode0.net.is_pd():
                for node in comp:
                    if node.pin.name[0] == 'Y':
                        node.pin.set_role("output")
            else:
                oenode0.pin.name = "OE"
                oenode0.insert()
            return

        comp2 = Component(
            comp.ref + "_B",
            comp.value,
            comp.partname,
        )
        comp.scm.add_component(comp2)
        comp2.name = comp.name + "_B"
        comp2.location = comp.location
        comp2.part = self
        for src, dst in (
            ("I4", "I0"),
            ("I5", "I1"),
            ("I6", "I2"),
            ("I7", "I3"),
            ("Y4", "Y0"),
            ("Y5", "Y1"),
            ("Y6", "Y2"),
            ("Y7", "Y3"),
        ):
            node = comp[src]
            node.remove()
            node.pin.name = dst
            node.pin.update()
            node.component = comp2
            node.insert()

        oenode0.remove()
        oenode0.pin.name = "OE"
        oenode0.insert()

        oenode1.remove()
        oenode1.pin.name = "OE"
        oenode1.component = comp2
        oenode1.insert()

        for this in (comp, comp2):
            node = this["OE"]
            if node.net.is_pd():
                node.remove()
                for node in this:
                    if node.pin.name[0] == "Y":
                        node.pin.set_role("output")
            elif len(node.net) == 1 or node.net.is_pu():
                this.eliminate()

    def configure(self, comp, part_lib):
        sig = self.make_signature(comp)
        ident = self.name + "_" + sig
        if self.invert:
            ident += "_I"
        if "INV" in comp and comp["INV"].net.is_pd():
            ident += "_I"
        if ident not in part_lib:
            part_lib.add_part(ident, Xbuf(ident))
        comp.part = part_lib[ident]

    def optimize(self, comp):
        optimize_oe_output(comp, "OE", "Y")

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F244", ModelXbuf(False))
    part_lib.add_part("F240", ModelXbuf(True))
    part_lib.add_part("XBUF3", ModelXbuf(False))
    part_lib.add_part("XBUF4", ModelXbuf(False))
    part_lib.add_part("XBUF6", ModelXbuf(False))
    part_lib.add_part("XBUF8", ModelXbuf(False))
    part_lib.add_part("XBUF9", ModelXbuf(False))
    part_lib.add_part("XBUF12", ModelXbuf(False))
    part_lib.add_part("XBUF14", ModelXbuf(False))
    part_lib.add_part("XBUF16", ModelXbuf(False))
    part_lib.add_part("XBUF20", ModelXbuf(False))
    part_lib.add_part("XBUF21", ModelXbuf(False))
    part_lib.add_part("XBUF24", ModelXbuf(False))
    part_lib.add_part("XBUF32", ModelXbuf(False))
    part_lib.add_part("XFBUF32", ModelXbuf(False))
    part_lib.add_part("XBUF48", ModelXbuf(False))
    part_lib.add_part("XBUF56", ModelXbuf(False))
    part_lib.add_part("XBUF64", ModelXbuf(False))
    part_lib.add_part("BUF64", ModelXbuf(False))
    part_lib.add_part("XBUF67", ModelXbuf(False))
