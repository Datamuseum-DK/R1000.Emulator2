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

    autopin = True

    def private(self):
        ''' private variables '''
        if "OE" in self.comp:
            yield from self.event_or(
                "idle_event",
                "PIN_OE",
                "PIN_LE",
            )
        else:
            yield from self.event_or(
                "idle_event",
                "PIN_LE",
            )

    def doit(self, file):
        ''' The meat of the doit() function '''

        if self.comp.part.name[-2:] == "_I":
            file.fmt('''
		|		uint64_t mask = BUS_Q_MASK;
		|''')
        else:
            file.fmt('''
		|		uint64_t mask = 0;
		|''')

        file.fmt('''
		|	if (PIN_LE=>) {
		|		BUS_D_READ(output.q);
		|		output.q ^= mask;
		|	}
		|''')

        if "OE" in self.comp:
            file.fmt('''
		|	output.z_q = PIN_OE=>;
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|	if (!PIN_LE=>) {
		|               next_trigger(idle_event);
		|	}
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
        else:
            assert not oe_node.net.is_const()
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
    part_lib.add_part("XLAT64", ModelXlat("XLAT64"))
