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
   TYP Spc
   =======

'''

from part import PartModel, PartFactory

class XTSPC(PartFactory):
    ''' TYP Spc '''

    autopin = True

    def sensitive(self):
        yield "PIN_CLK"
        yield "BUS_MARCTL"
        yield "BUS_B"
        yield "PIN_FSP"
        yield "PIN_TAEN"
        yield "PIN_VAEN"
        yield "PIN_DON"
        yield "PIN_DOFF"

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_TAEN",
            "PIN_VAEN",
            "PIN_DON",
            "PIN_DOFF",
        )

    def state(self, file):
        file.fmt('''
		|       bool poe;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool pos = PIN_CLK.posedge();
		|
		|	output.aspe = !(
		|		!(PIN_TAEN=> && PIN_VAEN=> && PIN_DON=>) &&
		|		PIN_DOFF=>
		|	);
		|	output.z_asp = output.aspe;
		|
		|	if (pos) {
		|		state->poe = output.aspe;
		|	}
		|
		|	if (pos || !output.z_asp) {
		|		unsigned marctl;
		|		BUS_MARCTL_READ(marctl);
		|		bool force_sp_h1 = PIN_FSP=>;
		|
		|		if (!force_sp_h1) {
		|			output.asp = 0x7;
		|		} else if (marctl & 0x8) {
		|			output.asp = (marctl & 0x7) ^ 0x7;
		|		} else {
		|			unsigned b;
		|			BUS_B_READ(b);
		|			output.asp = b ^ 0x7;
		|		}
		|	}
		|	if (output.z_asp && state->poe) {
		|		next_trigger(idle_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTSPC", PartModel("XTSPC", XTSPC))
