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
   2KX8 Latched EPROM
   ==================

'''


from part import PartModel, PartFactory

class P2K8R(PartFactory):

    ''' 2KX8 Latched EPROM '''

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint8_t prom[2050];\n")
        file.write("\tint last, nxt;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	load_programmable(this->name(), state->prom, sizeof state->prom, arg);
		|	state->nxt = 2048;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = NULL;
		|	int adr = 0;
		|
		|	if (state->nxt >= 0) {
		|		TRACE(
		|		    << " CK " << PIN_CK?
		|		    << " A " << BUS_A_TRACE()
		|		    << " MR_ " << PIN_MR?
		|		    << std::hex << " nxt "
		|		    << state->nxt
		|		    << " D "
		|		    << std::hex << (unsigned)state->prom[state->nxt]
		|		);
		|		BUS_Y_WRITE(state->prom[state->nxt]);
		|		state->last = state->nxt;
		|		state->nxt = -1;
		|	}
		|	if (!PIN_MR=>) {
		|		if (state->last != 2048)
		|			state->nxt = 2048;
		|		what = " MR ";
		|	} else if (PIN_CK.posedge()) {
		|		BUS_A_READ(adr);
		|		if (adr != state->last)
		|			state->nxt = adr;
		|		what = " CLK ";
		|	}
		|	if (state->nxt >= 0)
		|		next_trigger(5, SC_NS);
		|''')

class ModelP2K8R(PartModel):
    ''' P2K8R Rom '''

    def assign(self, comp, part_lib):
        assert comp.nodes["OE"].net.is_pd()
        for node in comp:
            if node.pin.name[0] == "Y":
                node.pin.set_role("output")
        super().assign(comp, part_lib)

    def configure(self, comp, part_lib):
        del comp.nodes["OE"]
        sig = self.make_signature(comp)
        ident = self.name + "_" + sig
        if ident not in part_lib:
            part_lib.add_part(ident, P2K8R(ident))
        comp.part = part_lib[ident]

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("P2K8R", ModelP2K8R("P2K8R"))
