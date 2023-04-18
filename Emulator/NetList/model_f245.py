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
   F245 Octal bidirectional buffers
   ==========================================
'''

from part import PartModel, PartFactory
from component import Component
from node import Node
from net import Net
from pin import Pin

class F245(PartFactory):
    ''' ... '''

class ModelF245(PartModel):
    ''' F245 bidirectional buffers'''

    def assign(self, comp, part_lib):
        ''' Split into two separate components '''
        width = 0
        for node in comp.iter_nodes():
            if node.pin.name[0] == "A":
                width += 1

        assert not comp["DIR"].net.is_pd() and not comp["DIR"].net.is_pu()

        # We need an inverted version of the DIR signal
        inv_comp = Component(
            compref = comp.ref + "_INV",
            compvalue = comp.value,
            comppart = "F00"
        )
        comp.scm.add_component(inv_comp)
        inv_comp.name = comp.name + "_INV"
        inv_comp.part = part_lib[inv_comp.partname]

        Node(comp["DIR"].net, inv_comp, Pin("D0", "D0", "input"))
        Node(comp["DIR"].net, inv_comp, Pin("D1", "D1", "input"))

        inv_net = Net(self.name + "_AB_DIR")
        comp.scm.add_net(inv_net)
        Node(inv_net, inv_comp, Pin("Q", "Q", "output"))

        inv_comp.part.assign(inv_comp, part_lib)

        for suff, oe2_net in (
            ("AB", inv_net),
            ("BA", comp["DIR"].net),
        ):
            buf_comp = Component(
                compref = comp.ref + suff,
                compvalue = comp.value,
                comppart = "XBUF%d" % width
            )
            comp.scm.add_component(buf_comp)
            buf_comp.name = comp.name + suff
            buf_comp.part = part_lib[buf_comp.partname]

            if comp["OE"].net.is_pd():
                Node(oe2_net, buf_comp, Pin("OE", "OE", "input"))
            else:
                or_comp = Component(
                    compref = comp.ref + "_" + suff + "_OR",
                    compvalue = comp.value,
                    comppart = "F32"
                )
                comp.scm.add_component(or_comp)
                or_comp.name = comp.name + "_" + suff + "_OR"
                or_comp.part = part_lib[or_comp.partname]

                oe_net = Net(self.name + "_" + suff + "_OE")
                comp.scm.add_net(oe_net)

                Node(oe_net, or_comp, Pin("Q", "Q", "output"))
                Node(oe2_net, or_comp, Pin("D0", "D0", "input"))
                Node(comp["OE"].net, or_comp, Pin("D1", "D1", "input"))

                Node(oe_net, buf_comp, Pin("OE", "OE", "input"))

            for node in comp.nodes.values():
                if suff[1] == node.pin.name[0]:
                    new_pin = Pin(
                        "Y" + node.pin.ident[1:],
                        "Y" + node.pin.name[1:],
                        "output",
                    )
                elif suff[0] == node.pin.name[0]:
                    new_pin = Pin(
                        "I" + node.pin.ident[1:],
                        "I" + node.pin.name[1:],
                        "input",
                    )
                else:
                    continue
                Node(
                    node.net,
                    buf_comp,
                    new_pin,
                )

            buf_comp.part.assign(buf_comp, part_lib)
        comp.eliminate()

def register(part_lib):
    ''' Register component model '''

    for part in (
        "F245",
        "XBIDIR11",
        "XBIDIR16",
        "XBIDIR32",
        "XBIDIR64",
    ):
        part_lib.add_part(part,        ModelF245(part, F245))
