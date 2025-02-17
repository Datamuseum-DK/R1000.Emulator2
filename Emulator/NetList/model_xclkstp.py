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
   Clock Stop
   ==========

'''

from part import PartModel, PartFactory

class XCLKSTP(PartFactory):
    ''' Clock Stop '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "q3neg_event",
            "PIN_Q3.negedge_event()",
        )
        yield from self.event_or(
            "idle_event",
            "BUS_DIAG",
            "BUS_STOP",
        )

    def state(self, file):
        file.fmt('''
		|	bool sf_stop;
		|	bool prev;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned diag;
		|	BUS_DIAG_READ(diag);
		|
		|	unsigned clock_stop;
		|	BUS_STOP_READ(clock_stop);
		|
		|	bool q3 = PIN_Q3=>;
		|	bool q3pos = PIN_Q3.posedge();
		|
		|	if (PIN_Q3.negedge()) {
		|		state->sf_stop = !(diag == 0);
		|	}
		|
		|	if (!PIN_Q3=> || q3pos) {
		|		bool event = true;
		|		output.clkrun = true;
		|		output.iclk = true;
		|		output.sclk = true;
		|
		|		if ((clock_stop | 0x01) != BUS_STOP_MASK) {
		|			output.clkrun = false;
		|			event = false;
		|		}
		|		if (clock_stop != BUS_STOP_MASK) {
		|			output.iclk = false;
		|		}
		|		if ((clock_stop | 0x03) != BUS_STOP_MASK) {
		|			output.sclk = false;
		|		}
		|
		|		if (state->sf_stop) {
		|			output.clkrun = false;
		|			output.iclk = false;
		|			output.sclk = false;
		|		}
		|		if (q3pos) {
		|			mp_mem_abort_el = event;
		|		}
		|	}
		|	output.clkstp = !output.clkrun;
		|	if (q3) {
		|		idle_next = &q3neg_event;
		|	}
		|
		|	if (state->idle > 5 && !diag && clock_stop == 0xff) {
		|		idle_next = &idle_event;
		|	}
		|
		|''')

class XCLKSTPTV(PartFactory):
    ''' TV Clock Stop '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "q3neg_event",
            "PIN_Q3.negedge_event()",
        )
        yield from self.event_or(
            "idle_event",
            "PIN_CSAWR",
            "BUS_DIAG",
            "BUS_STOP",
        )

    def state(self, file):
        file.fmt('''
		|	bool sf_stop;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned diag;
		|	BUS_DIAG_READ(diag);
		|
		|	unsigned clock_stop;
		|	BUS_STOP_READ(clock_stop);
		|
		|	bool q3 = PIN_Q3=>;
		|	bool q3pos = PIN_Q3.posedge();
		|	bool csa_write_en = PIN_CSAWR=>;
		|
		|	if (PIN_Q3.negedge()) {
		|		state->sf_stop = !(diag == 0);
		|		output.sfstp = state->sf_stop;
		|		output.freez = (diag & 3) != 0;
		|	}
		|
		|	if (!q3 || q3pos) {
		|		output.clkrun = true;
		|		output.ramrun = true;
		|
		|		if (clock_stop != BUS_STOP_MASK) {
		|			output.clkrun = false;
		|			if (!csa_write_en)
		|				output.ramrun = false;
		|		}
		|
		|		if (state->sf_stop) {
		|			output.clkrun = false;
		|			if (!csa_write_en)
		|				output.ramrun = false;
		|		}
		|	}
		|
		|	if (q3) {
		|		idle_next = &q3neg_event;
		|	}
		|	if (state->idle > 5 && !diag && clock_stop == 0xff) {
		|		idle_next = &idle_event;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCLKSTP", PartModel("XCLKSTP", XCLKSTP))
    part_lib.add_part("XCLKSTPTV", PartModel("XCLKSTPTV", XCLKSTPTV))
