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
		|	unsigned col;
		|''')

    def sensitive(self):
        yield "PIN_CLKQ2"
        yield "PIN_CLKQ4.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q2pos = PIN_CLKQ2.posedge();
		|	bool q2neg = PIN_CLKQ2.negedge();
		|	bool q4neg = PIN_CLKQ4.negedge();
		|
		|	if (q2neg) {
		|		if (!PIN_ROWE=>) {
		|			BUS_ROW_READ(output.dr);
		|		} else if (!PIN_COLE=>) {
		|			output.dr = state->col;
		|		} else {
		|			output.dr = 0xff;
		|		}
		|	}
		|	if (q2pos) {
		|		BUS_COL_READ(state->col);
		|	}
		|	if (q4neg) {
		|		if (!PIN_ROWE=>) {
		|			BUS_ROW_READ(output.dr);
		|		} else if (!PIN_COLE=>) {
		|			output.dr = state->col;
		|		} else {
		|			output.dr = 0xff;
		|		}
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMTRC", PartModel("XMTRC", XMTRC))
