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
   Two-choice multiplexers
   =======================

   F157 Quad 2-input data selector/multiplexer, non-inverting
   F158 Quad 2-input data selector/multiplexer, inverting
   Ref: Philips IC15 1996 Mar 12
'''


from part import PartModel, PartFactory, optimize_oe_output

class Mux2(PartFactory):

    ''' Two-choice multiplexers '''

    def __init__(self, ident, invert):
        super().__init__(ident)
        self.invert = invert

    def private(self):
        ''' private variables '''
        j = []
        if "OE" in self.comp.nodes:
            j.append("PIN_OE")
        if "E" in self.comp.nodes:
            j.append("PIN_E")
            yield from self.event_or(
                "e_event",
                *j
            )
        for  i in "ab":
            yield from self.event_or(
                i + "_event",
                "BUS_%s" % i.upper(),
                "PIN_S",
                *j
            )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned tmp;
		|
		|''')

        if "OE" in self.comp.nodes:
            file.fmt('''
		|	if (PIN_OE=>) {
		|		TRACE( << "Z" );
		|		BUS_Y_Z();
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|''')

        if "E" in self.comp.nodes:
            file.fmt('''
		|	if (PIN_E=>) {
		|		tmp = 0;
		|		next_trigger(e_event);
		|	} else if (PIN_S=>) {
		|''')
        else:
            file.fmt('''
		|	if (PIN_S=>) {
		|''')

        file.fmt('''
		|		BUS_B_READ(tmp);
		|		next_trigger(b_event);
		|	} else {
		|		BUS_A_READ(tmp);
		|		next_trigger(a_event);
		|	}
		|
		|''')

        if self.invert:
            file.fmt('''
		|
		|	tmp ^= BUS_A_MASK;
		|
		|''')

        file.fmt('''
		|
		|	TRACE (
		|''')

        if "OE" in self.comp.nodes:
            file.fmt('''
		|	    << " oe " << PIN_OE=>
		|''')

        if "E" in self.comp.nodes:
            file.fmt('''
		|	    << " e " << PIN_E=>
		|''')

        file.fmt('''
		|	    << " s " << PIN_S=>
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " | " << std::hex << tmp
		|	);
		|
		|	BUS_Y_WRITE(tmp);
		|''')

class ModelMux2(PartModel):
    ''' Model quad two input multiplexers '''

    def __init__(self, invert):
        super().__init__("MUX2")
        self.invert = invert

    def assign(self, comp, part_lib):
        for pin_name in ("E", "OE"):
            node = comp.nodes.get(pin_name)
            if node and node.net.is_pd():
                node.remove()
        if "OE" not in comp.nodes:
            for node in comp:
                if node.pin.name[0] == "Y":
                    node.pin.set_role('output')
        super().assign(comp, part_lib)

    def configure(self, comp, part_lib):
        sig = self.make_signature(comp)
        ident = self.name + "_" + sig
        invert = self.invert
        if self.invert is None and comp["INV"].net.is_pd():
            invert = True
        if invert is True:
            ident += "_I"
        if "OE" in comp.nodes:
            ident += "_Z"
        if ident not in part_lib:
            part_lib.add_part(ident, Mux2(ident, invert))
        comp.part = part_lib[ident]

    def optimize(self, comp):
        optimize_oe_output(comp, "OE", "Y")

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F157", ModelMux2(invert=False))
    part_lib.add_part("F158", ModelMux2(invert=True))
    part_lib.add_part("F257", ModelMux2(invert=False))
    part_lib.add_part("F258", ModelMux2(invert=True))
    part_lib.add_part("XMUX4", ModelMux2(invert=None))
    part_lib.add_part("XMUX5", ModelMux2(invert=None))
    part_lib.add_part("XMUX6", ModelMux2(invert=None))
    part_lib.add_part("XMUX7", ModelMux2(invert=None))
    part_lib.add_part("XMUX8", ModelMux2(invert=None))
    part_lib.add_part("XMUX10", ModelMux2(invert=None))
    part_lib.add_part("XMUX12", ModelMux2(invert=None))
    part_lib.add_part("XMUX16", ModelMux2(invert=None))
    part_lib.add_part("XMUX17", ModelMux2(invert=None))
    part_lib.add_part("XMUX20", ModelMux2(invert=None))
    part_lib.add_part("XMUX24", ModelMux2(invert=None))
    part_lib.add_part("XMUX32", ModelMux2(invert=None))
