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
   TYP/VAL A-bus driver
   ====================

'''

from part import PartModel, PartFactory

class XTVADR(PartFactory):
    ''' TYP/VAL A-bus driver '''

    autopin = True

    def sensitive(self):
        yield "PIN_Q4"
        yield "PIN_AEN"
        yield "PIN_DON"
        yield "PIN_DOFF"
        yield "BUS_ALU"

    def private(self):
        yield from self.event_or(
            "idle_event",
            "PIN_AEN",
            "PIN_DON",
            "PIN_DOFF",
        )

    def state(self, file):
        file.fmt('''
		|	bool poe;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4pos = PIN_Q4.posedge();
		|
		|	output.adre = !(!(PIN_AEN=> && PIN_DON=>) && PIN_DOFF=>);
		|	output.z_adr = output.adre;
		|
		|	if (q4pos) {
		|		state->poe = output.adre;
		|	}
		|	unsigned spc;
		|	BUS_SPC_READ(spc);
		|
		|	uint64_t alu;
		|	BUS_ALU_READ(alu);
		|
		|	if (spc < 4 || (PIN_FRCPA=> && spc > 4)) {
		|		alu |=0xf8000000ULL;
		|	}
		|
		|	if (!output.z_adr)
		|		output.adr = alu ^ BUS_ALU_MASK;
		|
		|	if (output.z_adr && state->poe) {
		|		next_trigger(idle_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVADR", PartModel("XTVADR", XTVADR))
