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
   F251 8-Input Multiplexer with 3-STATE Outputs
   ==============================================

   Ref: Fairchild DS009504 April 1988 Revised September 2000
'''

from part import PartModel, PartFactory

class F251(PartFactory):
    ''' F251 8-Input Multiplexer '''

    autopin = True

    def private(self):
        if "OE" in self.comp:
            yield from self.event_or(
                "idle_event",
                "PIN_OE.negedge_event()",
            )

    def doit(self, file):

        file.fmt('''
		|	unsigned adr = 0;
		|	bool s;
		|
		|	BUS_S_READ(adr);
		|	switch(adr) {
		|	case 0: s = PIN_A=>; break;
		|	case 1: s = PIN_B=>; break;
		|	case 2: s = PIN_C=>; break;
		|	case 3: s = PIN_D=>; break;
		|	case 4: s = PIN_E=>; break;
		|	case 5: s = PIN_F=>; break;
		|	case 6: s = PIN_G=>; break;
		|	case 7: s = PIN_H=>; break;
		|	}
		|''')

        if "OE" in self.comp:
            file.fmt('''
		|	bool oe = PIN_OE=>;
		|	if (oe) {
		|		idle_next = &idle_event;
		|	}
		|''')

        if "Y" in self.comp and "OE" in self.comp:
            file.fmt('''
		|	output.z_y = oe;
		|''')
        if "Y" in self.comp:
            file.fmt('''
		|	output.y = s;
		|''')

        if "Ynot" in self.comp and "OE" in self.comp:
            file.fmt('''
		|	output.z_ynot = oe;
		|''')
        if "Ynot" in self.comp:
            file.fmt('''
		|	output.ynot = !s;
		|''')

class ModelF251(PartModel):
    ''' Delete unused pins '''

    def assign(self, comp, _part_lib):

        oe_node = comp["OE"]
        if oe_node.net.is_pd():
            oe_node.remove()

        y_node = comp["Y"]
        if len(y_node.net) == 1:
            y_node.remove()

        ynot_node = comp["Ynot"]
        if len(ynot_node.net) == 1:
            ynot_node.remove()

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F251", ModelF251("F251", F251))
