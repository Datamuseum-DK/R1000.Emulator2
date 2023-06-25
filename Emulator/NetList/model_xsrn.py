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
   F194 4-bit bidirectional universal shift register
   =================================================

   Ref: Philips 1989 Apr 04, IC15 Data Handbook
'''

from part import PartModel, PartFactory

class XSRN(PartFactory):

    ''' F194 4-bit bidirectional universal shift register '''

    def sensitive(self):
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"
        yield "PIN_CLK.pos()"

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint64_t out;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->out = BUS_Q_MASK;
		|	state->ctx.job = 1;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	const char *what = NULL;
		|	uint64_t nxt, mode = 0, tmp, i, j;
		|	const unsigned w = BUS_D_WIDTH / BUS_R_WIDTH;
		|
		|	if (state->ctx.job) {
		|		BUS_Q_WRITE(state->out);
		|		tmp = 0;
		|		j = 1U;
		|		for (i = 0; i < BUS_L_WIDTH; i++) {
		|			if (state->out & j)
		|				tmp |= (1U<<i);
		|			j <<= w;
		|		}
		|		BUS_O_WRITE(tmp);
		|		state->ctx.job = 0;
		|	}
		|	nxt = state->out;
		|
		|''')

        if not self.comp.nodes["CLR"].net.is_pu():
            file.fmt('''
		|	if (!PIN_CLR=>) {
		|		what = " clr ";
		|		state->out = 0;
		|		BUS_Q_WRITE(state->out);
		|		next_trigger(PIN_CLR.posedge_event());
		|		return;
		|	}
		|''')

        file.fmt('''
		|	if (PIN_CLK.posedge()) {
		|		BUS_S_READ(mode);
		|		switch (mode) {
		|		case 3:
		|			what = " load ";
		|			BUS_D_READ(nxt);
		|			break;
		|		case 2:
		|			what = " >> ";
		|			BUS_R_READ(tmp);
		|			nxt >>= 1;
		|			j = (1U << (w - 1));
		|			for (i = 0; i < BUS_R_WIDTH; i++) {
		|				if (tmp & (1 << i))
		|					nxt |= j;
		|				else
		|					nxt &= ~j;
		|				j <<= w;
		|			}
		|			break;
		|		case 1:
		|			what = " << ";
		|			BUS_L_READ(tmp);
		|			nxt <<= 1;
		|			nxt &= BUS_D_MASK;
		|			j = 1U;
		|			for (i = 0; i < BUS_L_WIDTH; i++) {
		|				if (tmp & (1 << i))
		|					nxt |= j;
		|				else
		|					nxt &= ~j;
		|				j <<= w;
		|			}
		|			break;
		|		case 0:
		|''')

        i = []
        if not self.comp.nodes["CLR"].net.is_pu():
            i.append("PIN_CLR.negedge_event()")
        i.append("BUS_S_EVENTS()")

        if i:
            file.write("\t\t\tnext_trigger(%s);\n" % (" | ".join(i)))

        file.fmt('''
		|			break;
		|		}
		|	}
		|	if ((state->ctx.do_trace & 2) && what == NULL)
		|		what = " - ";
		|	if (what != NULL) {
		|		TRACE(
		|		    << what
		|		    << " clr " <<  PIN_CLR?
		|		    << " r " << BUS_R_TRACE()
		|		    << " d " << BUS_D_TRACE()
		|		    << " l " << BUS_L_TRACE()
		|		    << " s " << BUS_S_TRACE()
		|		    << " cp↑ " << PIN_CLK.posedge()
		|		    << " r "
		|		    << std::hex << state->out
		|		    << " nxt "
		|		    << std::hex << nxt
		|		);
		|	}
		|	if (nxt != state->out) {
		|		state->out = nxt;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSR8X4", PartModel("XSR8X4", XSRN))
    part_lib.add_part("XSR8X5", PartModel("XSR8X5", XSRN))
    part_lib.add_part("XSR8X8", PartModel("XSR8X8", XSRN))
