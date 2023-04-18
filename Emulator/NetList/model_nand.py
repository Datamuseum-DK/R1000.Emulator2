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
   Model the NAND components
   =========================
'''

from part import Part, PartFactory

import util

class Nand(PartFactory):

    ''' A generic N-input NAND component '''

    def __init__(self, ident, inputs, delay, invert):
        super().__init__(ident)
        self.inputs = inputs
        self.scm = False
        self.comp = None
        self.delay = delay
        self.invert = invert

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tint job;\n")
        file.write("\tint out;\n")
        file.write("\tunsigned dly;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.write("\tstate->dly = %d;\n" % self.delay)

        file.fmt('''
		|	state->out = -1;
		|	state->job = 0;
		|	if (strstr(this->name(), "IOC.ioc_54.RDNAN0A") != NULL) {
		|		// TEST_MACRO_EVENT_SLICE.IOC @ optimized
		|		state->dly = 10;
		|	}
		|	if (strstr(this->name(), "IOC.ioc_54.RDNAN0B") != NULL) {
		|		// TEST_MACRO_EVENT_DELAY.IOC @ optimized
		|		state->dly = 10;
		|	}
		|	if (strstr(this->name(), "TYP.typ_40.CKDR5A") != NULL) {
		|		// TEST_LOOP_CNTR_OVERFLOW.TYP @ main
		|		state->dly = 2;
		|	}
		|''')

    def sensitive(self):
        ''' sensitivity list '''

        for i in range(self.inputs):
            yield "PIN_D%d" % i

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.write("\tconst int active = %d;\n" % (not self.invert))

        file.fmt('''
		|
		|	TRACE(
		|	    << " j " << state->job
		|	    << " out " << state->out
		|	    << " in "
		|''')

        for i in range(self.inputs):
            file.write("\t    << PIN_D%d\n" % i)

        file.fmt('''
		|	);
		|
		|	if (state->job) {
		|		PIN_Q<=(state->out);
		|		state->job = false;
		|	}
		|
		|''')

        file.write("\n\tif (\n\t    ")

        i = []
        for node in self.comp:
            if node.pin.name != "Q":
                i.append("PIN_%s=>" % node.pin.name)
        file.fmt(" &&\n\t    ".join(i))

        file.fmt('''
		|
		|	) {
		|		if (state->out != active) {
		|			state->out = active;
		|			if (state->dly == 0) {
		|				PIN_Q<=(state->out);
		|			} else {
		|				state->job = true;
		|				next_trigger(state->dly, SC_NS);
		|			}
		|		}
		|	} else {
		|		if (state->out != !active) {
		|			state->out = !active;
		|			if (state->dly == 0) {
		|				PIN_Q<=(state->out);
		|			} else {
		|				state->job = true;
		|				next_trigger(state->dly, SC_NS);
		|			}
		|''')

        if self.inputs > 1:
            for node in self.comp:
                if node.pin.name != "Q":
                    file.fmt("\t\t} else if (!PIN_%s=>) {\n" % node.pin.name)
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

class ModelNand(Part):
    ''' Model NAND components '''

    def __init__(self, delay, invert):
        super().__init__("NAND")
        self.delay = delay
        self.invert = invert

    def assign(self, comp, _part_lib):
        ''' Assigned to component '''
        seen = set()
        ninputs = 0
        rnodes = list(comp)
        for node in rnodes:
            # > 2 is special case for IOC::IPNOR0C etc.
            if node.net.is_pu() and len(rnodes) > 2:
                # print("Eliminating NAND PU input", node)
                node.remove()
                continue
            if node.net in seen:
                # print("Eliminating NAND input", node)
                node.remove()
                continue
            seen.add(node.net)
            if node.pin.name == "Q":
                node.pin.set_role("output")
            else:
                node.pin.set_role("input")
                ninputs += 1
        if not ninputs:
            print("NAND with no inputs left", ninputs, comp)
            for i in rnodes:
                print("   ", i)
            assert ninputs

    def configure(self, comp, part_lib):
        i = []
        j = 0
        for node in list(comp):
            if node.pin.name != "Q":
                node.pin.name = "D%d" % j
                j += 1
            if node.net.sc_type == "bool":
                i.append("B")
            else:
                i.append("L")
        inputs = len(comp.nodes) - 1
        sig = util.signature(i)
        ident = "AND%d_" % inputs + "%d_" % self.delay + sig
        if self.invert:
            ident = "N" + ident
        if ident not in part_lib:
            part_lib.add_part(ident, Nand(ident, inputs, self.delay, self.invert))
        comp.part = part_lib[ident]

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F00", ModelNand(0, True))
    part_lib.add_part("F04", ModelNand(5, True))	# Inverters are juvenile NAND gates
    part_lib.add_part("F08", ModelNand(0, False))
    part_lib.add_part("F37", ModelNand(5, True))
    part_lib.add_part("F10", ModelNand(0, True))
    part_lib.add_part("F20", ModelNand(0, True))   ### Not: OC-thing with ALU-ZERO outputs
    part_lib.add_part("F30", ModelNand(0, True))
    part_lib.add_part("F40", ModelNand(0, True))
    part_lib.add_part("F133", ModelNand(0, True))
    part_lib.add_part("AND4", ModelNand(0, False))
    part_lib.add_part("AND3", ModelNand(0, False))
    part_lib.add_part("AND2", ModelNand(0, False))
