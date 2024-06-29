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
   TYP A-side mux+latch
   ====================

'''

from part import PartModel, PartFactory

class XTASIDE(PartFactory):
    ''' TYP A-side mux+latch '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "nolat_event",
            "PIN_AODIAG",
            "BUS_UA",
            "BUS_LOOP",
        )
        yield from self.event_or(
            "lat_event",
            "PIN_AODIAG",
            "BUS_UA",
            #"BUS_C",
            "PIN_LE",
        )


    def state(self, file):
        file.fmt('''
		|	uint64_t alat;
		|''')

    def sensitive(self):
        yield "PIN_AODIAG"
        yield "BUS_UA"
        yield "BUS_LOOP"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned uir_a, loop;
		|	uint64_t a = 0;
		|	bool is_lat = false;
		|
		|	if (PIN_LE) {
		|		BUS_C_READ(state->alat);
		|	}
		|	BUS_UA_READ(uir_a);
		|	if ((uir_a & 0x3c) != 0x28 || !PIN_AODIAG) {
		|		a = state->alat;
		|		is_lat = true;
		|	} else if (uir_a == 0x28) {
		|		BUS_LOOP_READ(loop);
		|		a = BUS_A_MASK;
		|		a ^= BUS_LOOP_MASK;
		|		a |= loop;
		|	} else {
		|		a = BUS_A_MASK;
		|	}
		|	output.a = a;
		|	output.ab0 = a >> 63;
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|	if (is_lat) {
		|		next_trigger(lat_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTASIDE", PartModel("XTASIDE", XTASIDE))
