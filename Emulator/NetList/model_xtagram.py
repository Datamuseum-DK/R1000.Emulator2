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
from pin import Pin
from node import Node

class XTAGRAM(PartFactory):

    ''' NXM SRAM '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_A_WIDTH];
		|	uint64_t last;
		|	const char *what;
		|''')

    def extra(self, file):
        super().extra(file)
        file.fmt('''
		|static const char *READING = "r";
		|static const char *WRITING = "w";
		|''')

        if not self.comp.nodes["OE"].net.is_pd():
            file.fmt('''
		|static const char *ZZZING = "z";
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "rd_event",
            "PIN_OE.posedge_event()",
            "PIN_WE.negedge_event()",
            "BUS_A",
        )

    def sensitive(self):
        yield "PIN_OE"
        yield "PIN_WE"
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
		|	if (PIN_OE=>) {
		|		if (state->what == READING) {
		|			BUS_Q_Z();
		|		} else if (state->what == WRITING) {
		|			BUS_D_READ(data);
		|			state->ram[adr] = data;
		|		}
		|		next_trigger(PIN_OE.negedge_event());
		|		state->what = ZZZING;
		|	} else if (!PIN_WE=>) {
		|		if (state->what == READING)
		|			BUS_Q_Z();
		|		BUS_D_READ(data);
		|		state->ram[adr] = data;
		|		state->what = WRITING;
		|	} else {
		|		if (state->what == WRITING) {
		|			BUS_D_READ(data);
		|			state->ram[adr] = data;
		|		}
		|		data = state->ram[adr];
		|		if (state->what != READING || data != state->last) {
		|			BUS_Q_WRITE(data);
		|			state->last = data;
		|		}
		|		state->what = READING;
		|		next_trigger(rd_event);
		|	}
		|
		|	TRACE(
		|	    << state->what
		|	    << " we " << PIN_WE?
		|	    << " oe " << PIN_OE?
		|	    << " a " << BUS_A_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	);
		|''')

class XTAGRAM8(PartFactory):

    ''' NXM SRAM '''

    def state(self, file):
        file.fmt('''
		|	uint8_t ram[1<<BUS_A_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_OE"
        yield "PIN_WE"
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
		|	if (PIN_OE=>) {
		|		BUS_Q_WRITE(0xff);
		|		next_trigger(PIN_OE.negedge_event());
		|	} else if (PIN_WE.posedge()) {
		|		if (PIN_DIR=> || PIN_VEN=>) {
		|			BUS_D_READ(data);
		|		} else {
		|			BUS_V_READ(data);
		|		}
		|		state->ram[adr] = data;
		|		BUS_Q_WRITE(data);
		|	} else if (PIN_WE=>) {
		|		data = state->ram[adr];
		|		BUS_Q_WRITE(data);
		|	}
		|
		|	TRACE(
		|	    << " we " << PIN_WE?
		|	    << " oe " << PIN_OE?
		|	    << " a " << BUS_A_TRACE()
		|	    << " v " << BUS_V_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTAGRAM8", PartModel("XTAGRAM8", XTAGRAM8))
    part_lib.add_part("XTAGRAM64", PartModel("XTAGRAM64", XTAGRAM))
