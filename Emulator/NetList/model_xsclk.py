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
   State clock gate
   ================

'''

from part import PartModel, PartFactory

class XSCLK(PartFactory):
    ''' TYP A-side mux+latch '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "next_edge_event",
            "PIN_Q4E",
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_Q4E.negedge()) {
		|		output.q = BUS_D_MASK;
		|	} else if (PIN_Q4E=>) {
		|		if (!PIN_SCE=>) {
		|			BUS_D_READ(output.q);
		|		} else {
		|			output.q = BUS_D_MASK;
		|		}
		|	} else {
		|		idle_next = &next_edge_event;
		|	}		
		|''')

def register(part_lib):
    ''' Register component model '''

    for i in (2, 3, 4, 8, 12,):
        part_lib.add_part("XSCLK%d" % i, PartModel("XSCLK%d" % i, XSCLK))
