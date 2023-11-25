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
   256-bit TTL bipolar PROM (32x8)
   ===============================

   Ref: Signetics 82S123A, product specification, June 6 1985
'''


from part import PartModel, PartFactory

class PBxxx(PartFactory):
    ''' 256-bit TTL bipolar PROM (32x8) '''

    autopin = True

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint8_t prom[32];\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	load_programmable(this->name(), state->prom, sizeof state->prom, arg);
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        if 'OE' in self.comp and not self.comp["OE"].net.is_const():
            assert False
            file.fmt('''
		|	if (!PIN_OE=>) {
		|		BUS_Y_WRITE(data);
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	} 
		|''')

        file.fmt('''
		|	unsigned adr = 0;
		|
		|	BUS_A_READ(adr);
		|	unsigned data = state->prom[adr];
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " d "
		|	    << AS(data & 0x80)
		|	    << AS(data & 0x40)
		|	    << AS(data & 0x20)
		|	    << AS(data & 0x10)
		|	    << AS(data & 0x08)
		|	    << AS(data & 0x04)
		|	    << AS(data & 0x02)
		|	    << AS(data & 0x01)
		|	);
		|	output.y = data;
		|''')

class ModelPBxxx(PartModel):
    ''' PBxxx Rom '''

    def assign(self, comp, part_lib):
        if comp.nodes["OE"].net.is_pd():
            for node in comp:
                if node.pin.name[0] == "Y":
                    node.pin.set_role("output")
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("PBxxx", ModelPBxxx("PBXXX", PBxxx))
