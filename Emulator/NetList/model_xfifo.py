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
   256X16 FIFO
   ===========

'''


from part import PartModel, PartFactory

class XFIFO(PartFactory):

    ''' 256X16 FIFO '''

    def state(self, file):
        file.fmt('''
		|	uint32_t ram[1<<8];
		|	uint32_t rptr;
		|	uint32_t wptr;
		|	uint32_t oreg;
		|''')

    def sensitive(self):
        yield "PIN_CLR"
        yield "PIN_RD.pos()"
        yield "PIN_WR.pos()"
        yield "PIN_OEnot"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint32_t d;
		|
		|	BUS_D_READ(d);
		|	TRACE(
		|	    << " CLR " << PIN_CLR
		|	    << " WR↑ " << PIN_WR.posedge()
		|	    << " RD↑ " << PIN_RD.posedge()
		|	    << " OE~ " << PIN_OEnot
		|	    << " D " << BUS_D_TRACE()
		|	    << " " << std::hex << d
		|	    << " diff " << (((0x100 + state->wptr) - state->rptr) & 0xff)
		|	);
		|
		|	if (!PIN_CLR=>) {
		|		state->rptr = 0;
		|		state->wptr = 0;
		|	} else {
		|		if (PIN_WR.posedge()) {
		|			state->ram[state->wptr++] = d;
		|			state->wptr &= 0xff;
		|		}
		|		if (PIN_RD.posedge()) {
		|			state->oreg = state->ram[state->rptr++];
		|			state->rptr &= 0xff;
		|		}
		|	}
		|	if (!PIN_OEnot)
		|		BUS_Q_WRITE(state->oreg);
		|	else
		|		BUS_Q_Z();
		|
		|	PIN_E<=(state->rptr == state->wptr);
		|	PIN_NE<=(state->rptr != state->wptr);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIFO", PartModel("XFIFO", XFIFO))
