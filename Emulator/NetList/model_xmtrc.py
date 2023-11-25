#!/usr/local/bin/python3
#
# Copyright (c) 2023 Poul-Henning Kamp
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
   MEM32 Tracing
   =============

'''

from part import PartModel, PartFactory

class XMTRC(PartFactory):
    ''' MEM32 Tracing '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t traram[1 << BUS_A_WIDTH];
		|	unsigned trareg;
		|''')

    def xxsensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def private(self):
        enables = (
            "PIN_CLK.posedge_event()",
            "PIN_WE.posedge_event()",
            "PIN_IAE0",
            "PIN_IAE1",
            "PIN_IBE0",
            "PIN_IBE1",
            "PIN_ICE0",
            "PIN_ICE1",
            "PIN_IDE",
        )
        yield from self.event_or(
            "ia_event",
            "BUS_IA",
            *enables,
        )
        yield from self.event_or(
            "ib_event",
            "BUS_IB",
            *enables,
        )
        yield from self.event_or(
            "ic_event",
            "BUS_IC",
            *enables,
        )
        yield from self.event_or(
            "id_event",
            "BUS_ID",
            *enables,
        )
        yield from self.event_or(
            "ram_event",
            "BUS_A",
            *enables,
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (PIN_CLK.posedge()) {
		|		BUS_ID_READ(state->trareg);
		|	}
		|
		|	unsigned trace = 0xff, adr = 0;
		|
		|	if (!PIN_IAE0=> && PIN_IAE1=>) {
		|		BUS_IA_READ(trace);
		|		next_trigger(ia_event);
		|	} else if (!PIN_IBE0=> && !PIN_IBE1=>) {
		|		BUS_IB_READ(trace);
		|		next_trigger(ib_event);
		|	} else if (!PIN_ICE0=> && !PIN_ICE1=>) {
		|		BUS_IC_READ(trace);
		|		next_trigger(ic_event);
		|	} else if (!PIN_IDE=>) {
		|		trace = state->trareg;
		|		next_trigger(id_event);
		|	} else {
		|		BUS_A_READ(adr);
		|		trace = state->traram[adr];
		|		next_trigger(ram_event);
		|	}
		|	output.q = trace;
		|	if (PIN_WE.posedge()) {
		|		BUS_A_READ(adr);
		|		state->traram[adr] = trace;
		|	}
		|
		|	TRACE(
		|		<< " clk " << PIN_CLK?
		|		<< " we " << PIN_WE?
		|		<< " ia " << PIN_IAE0? << PIN_IAE1? << " " << BUS_IA_TRACE()
		|		<< " ib " << PIN_IBE0? << PIN_IBE1? << " " << BUS_IB_TRACE()
		|		<< " ic " << PIN_ICE0? << PIN_ICE1? << " " << BUS_IC_TRACE()
		|		<< " id " << PIN_IDE? << " " << BUS_ID_TRACE()
		|		<< " a " << BUS_A_TRACE()
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMTRC", PartModel("XMTRC", XMTRC))
