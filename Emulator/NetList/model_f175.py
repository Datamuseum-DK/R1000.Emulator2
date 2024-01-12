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
   F175 D-Type Flip-Flop
   ===================================

   Ref: Fairchild DS009490 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory
from component import Component
from node import Node
from pin import Pin
from net import Net

class F175(PartFactory):

    ''' F175 D-Type Flip-Flop '''

    autopin = True

    def private(self):
        ''' private variables '''
        if self.comp.nodes["CLR"].net.is_pu():
            yield from self.event_or(
                "idle_event",
                "BUS_D",
            )
        else:
            yield from self.event_or(
                "idle_event",
                "PIN_CLR",
                "BUS_D",
            )

    def sensitive(self):
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (!PIN_CLR=>) {
		|		output.q = 0;
		|	} else if (PIN_CLK.posedge()) {
		|		BUS_D_READ(output.q);
		|	}
		|	output.q0not = !(output.q & 8);
		|	output.q1not = !(output.q & 4);
		|	output.q2not = !(output.q & 2);
		|	output.q3not = !(output.q & 1);
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|       if (state->idle > 10) {
		|               state->idle = 0;
		|		unsigned tmp;
		|		BUS_D_READ(tmp);
		|		if (tmp == output.q)
		|               	next_trigger(idle_event);
		|       }
		|''')

class ModelF175(PartModel):
    ''' ... '''

    def xassign(self, comp, part_lib):
        ''' Wholesale conversion runs slower '''
        punet = None
        for node in comp:
            if node.net.is_pu():
                punet = node.net
        if not punet:
            print("Need PU to split", comp)
            super().assign(comp, part_lib)
            return
        print("C", comp, comp["D0"].net.netbus, comp["Q0"].net.netbus)
        clknode = comp["CLK"]
        clrnode = comp["CLR"]
        for i in range(4):
            dnode = comp["D%d" % i]

            if dnode.net.is_const():
                print("  C", i, dnode.net)
                continue

            ff_comp = Component(
                compref = comp.ref + "_%c" % (65+i),
                compvalue = comp.value,
                comppart = "F74",
            )
            ff_comp.name = comp.name + "_%c" % (65+i)
            ff_comp.part = part_lib[ff_comp.partname]
            comp.scm.add_component(ff_comp)

            Node(clknode.net, ff_comp, Pin("CLK", "CLK", "input"))
            Node(clrnode.net, ff_comp, Pin("CL_", "CL_", "input"))
            Node(punet, ff_comp, Pin("PR_", "PR_", "input"))
            Node(dnode.net, ff_comp, Pin("D", "D", "input"))

            qnet = comp["Q%d" % i].net
            Node(qnet, ff_comp, Pin("Q", "Q", "output"))

            rnet = comp["Q%dnot" % i].net
            Node(rnet, ff_comp, Pin("Q_", "Q_", "output"))

            ff_comp.part.assign(ff_comp, part_lib)
        comp.eliminate()


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F175", ModelF175("F175", F175))
