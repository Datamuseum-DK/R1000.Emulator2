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
   F521 8-Bit Identity Comparator (and multiples)
   ==============================================

   Ref: Fairchild DS009545 April 1988 Revised October 2000
'''


from part import PartModel, PartFactory

class XEQ(PartFactory):

    ''' F521 8-Bit Identity Comparator (and multiples) '''

    autopin = True

    def state(self, file):
        if "CONST" in self.name:
            file.write("\tuint64_t const_b;\n")

    def init(self, file):
        if "CONST" in self.name:
            file.write('\tstate->const_b = strtoul(arg, NULL, 16);\n')

    def sensitive(self):
        if "X521" in self.name:
           yield "PIN_C.pos()"
        else:
           yield from super().sensitive()

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        if "E" in self.comp.nodes:
            file.fmt('''
		|	if (PIN_E=>) {
		|		output.aeqb = true;
		|		TRACE ( << " e " << PIN_E?);
		|		next_trigger(PIN_E.negedge_event());
		|		return;
		|	}
		|
		|''')

        if "CONST" in self.name:
            file.fmt('''
		|	uint64_t a;
		|	BUS_A_READ(a);
		|	output.aeqb = (a != state->const_b);
		|
		|	TRACE (
		|	    << "a " << BUS_A_TRACE()
		|	    << " b " << std::hex << state->const_b
		|	);
		|''')
        else:
            file.fmt('''
		|	uint64_t a, b;
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	output.aeqb = (a != b);
		|
		|	TRACE (
		|	    << "a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	);
		|''')

class ModelXeq(PartModel):
    ''' comparator '''

    def assign(self, comp, part_lib):

        # Eliminate PIN_E if pulled down
        node_e = comp.nodes.get("E")
        if node_e and node_e.net.is_pd():
            node_e.remove()

        # Eliminate constant, identical A-B pairs
        l = []
        for i in range(len(comp.nodes)//2):
            a = comp.nodes.get("A%d" % i)
            b = comp.nodes.get("B%d" % i)
            if a is None or b is None:
                break
            if a.net.is_pu() and b.net.is_pu():
                a.remove()
                b.remove()
                continue
            if a.net.is_pd() and b.net.is_pd():
                a.remove()
                b.remove()
                continue
            l.append((a, b))
        for n, i in enumerate(l):
            a, b = i
            a.remove()
            a.pin.name = "A%d" % n
            a.insert()
            b.remove()
            b.pin.name = "B%d" % n
            b.insert()

        # Find out if the B-side is constant
        bconst = True
        bval = {}
        for node in comp.nodes.values():
            if node.pin.name[0] != "B":
                continue
            if not node.net.is_const():
                bconst = False
                break
            bval[node.pin.name] = node.net.is_pu()
        if not bconst:
            super().assign(comp, part_lib)
            return

        # B is constant
        j = 0
        for i in range(len(bval)):
            if bval["B%d" % i]:
                j |= 1 << (len(bval) - i)
        j >>= 1
        for node in list(comp.nodes.values()):
            if node.pin.name[0] == "B":
                node.remove()
        comp.value = hex(j)
        super().assign(comp, part_lib)

    def make_signature(self, comp):
        sig = super().make_signature(comp)
        if "B0" not in comp.nodes:
            sig += "_CONST"
        return sig

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F521", ModelXeq("F521", XEQ))
    part_lib.add_part("X521", ModelXeq("X521", XEQ))
    part_lib.add_part("XEQ9", ModelXeq("XEQ9", XEQ))
