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
   NXM SRAM
   ==========

'''


from part import PartModel, PartFactory

class XTAGRAMA(PartFactory):

    ''' More than a simple TAG RAM'''

    def state(self, file):
        file.fmt('''
		|	uint8_t ram[1<<BUS_A_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_CS"
        yield "PIN_BOE"
        yield "PIN_BDIR"
        yield "PIN_WE"
        # yield "BUS_D_SENSITIVE()"
        yield "BUS_A_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|	uint8_t data = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if ((PIN_CS=> && !PIN_WE=>) ||
		|	    (PIN_WE.posedge() && !PIN_CS=>)) {
		|		if (!PIN_BOE=> && !PIN_BDIR)
		|			BUS_V_READ(data);
		|		else
		|			BUS_D_READ(data);
		|		state->ram[adr] = data;
		|		BUS_Q_WRITE(data);
		|	}
		|
		|	if (PIN_BOE=> || !PIN_BDIR)
		|		BUS_V_Z();
		| 
		|	if (PIN_CS=>) {
		|		BUS_V_Z();
		|		next_trigger(PIN_CS.negedge_event());
		|	} else {
		|		data = state->ram[adr];
		|		BUS_Q_WRITE(data);
		|		if (!PIN_BOE=> && PIN_BDIR)
		|			BUS_V_WRITE(data);
		|	}
		|
		|	TRACE(
		|	    << " we " << PIN_WE?
		|	    << " cs " << PIN_CS?
		|	    << " boe " << PIN_BOE?
		|	    << " bdir " << PIN_BDIR?
		|	    << " a " << BUS_A_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	    << " v " << BUS_V_TRACE()
		|	    << " q " << BUS_Q_TRACE()
		|	);
		|''')


class XTAGRAMB(PartFactory):

    ''' NXM SRAM '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_A_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_CS.pos()"
        yield "PIN_WE.pos()"
        yield "BUS_A_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|	uint64_t data = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_CS=>) {
		|		if (!PIN_WE=>) {
		|			BUS_D_READ(data);
		|			state->ram[adr] = data;
		|		}
		|		next_trigger(PIN_CS.negedge_event());
		|	} else if (PIN_WE.posedge() && !PIN_CS=>) {
		|		BUS_D_READ(data);
		|		state->ram[adr] = data;
		|	}
		|	data = state->ram[adr];
		|	BUS_Q_WRITE(data);
		|
		|	TRACE(
		|	    << " we " << PIN_WE?
		|	    << " cs " << PIN_CS?
		|	    << " a " << BUS_A_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTAGRAMA", PartModel("XTAGRAMA", XTAGRAMA))
    part_lib.add_part("XTAGRAMB", PartModel("XTAGRAMB", XTAGRAMB))
