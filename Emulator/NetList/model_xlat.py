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
   F373 Octal Transparant Latch with 3-STATE Outputs
   =================================================

   Ref: Fairchild DS009523, May 1988, Revised September 2000

'''

from part import PartModel, PartFactory, optimize_oe_output

class Xlat(PartFactory):

    ''' F373 Octal Transparant Latch with 3-STATE Outputs '''

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint64_t data;\n")
        file.write("\tint job;\n")
        file.write("\tbool z;\n")

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t tmp;
		|	bool upd = false;
		|
		|	if (state->job) {
		|		tmp = state->data;
		|''')

        if self.comp.part.name[-2:] == "_I":
            file.fmt('''
		|		tmp ^= BUS_Q_MASK;
		|''')

        file.fmt('''
		|		TRACE(" W 0x" << std::hex << tmp);
		|		BUS_Q_WRITE(tmp);
		|		state->job = 0;
		|	}
		|
		|	if (PIN_LE=>) {
		|		BUS_D_READ(tmp);
		|		if (tmp != state->data) {
		|			TRACE(<< " D 0x" << std::hex << tmp);
		|			state->data = tmp;
		|			upd = true;
		|		}
		|	} else {
		|''')

        i = [ "PIN_LE.posedge_event()"]
        if "OE" in self.comp and not self.comp["OE"].net.is_const():
            i.append("PIN_OE.default_event()")

        file.write("\t\tnext_trigger(%s);\n" % (" | ".join(i)))

        file.fmt('''
		|	}
		|''')

        if 'OE' in self.comp:
            file.fmt('''
		|	if (PIN_OE=>) {
		|		if (!state->z) {
		|			TRACE(" Z ");
		|			BUS_Q_Z();
		|			state->z = true;
		|		}
		|		return;
		|	}
		|''')

        file.fmt('''
		|	if (!state->z && !upd)
		|		return;
		|	state->z = false;
		|	state->job = 1;
		|	next_trigger(5, sc_core::SC_NS);
		|''')


class ModelXlat(PartModel):
    ''' Xlat registers '''

    def assign(self, comp, part_lib):
        oe_node = comp["OE"]
        if oe_node.net.is_pd():
            oe_node.remove()
            for node in comp:
                if node.pin.name[0] == "Q":
                    node.pin.set_role("output")
        super().assign(comp, part_lib)

    def configure(self, comp, part_lib):
        sig = self.make_signature(comp)
        ident = self.name + "_" + sig
        if 'INV' in comp and comp['INV'].net.is_pd():
            ident += "_I"
        if ident not in part_lib:
            part_lib.add_part(ident, Xlat(ident))
        comp.part = part_lib[ident]

    def optimize(self, comp):
        optimize_oe_output(comp, "OE", "Q")

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F373", ModelXlat("F373"))
    part_lib.add_part("XLAT16", ModelXlat("XLAT16"))
    part_lib.add_part("XLAT32", ModelXlat("XLAT32"))
    part_lib.add_part("XLAT56", ModelXlat("XLAT56"))
    part_lib.add_part("XLAT64", ModelXlat("XLAT64"))
