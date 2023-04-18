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
   F579 8-bit bidirectional binary counter (3-State)
   =================================================

   Ref: Fairchild DS009568 April 1988, Revised October 2000
'''


from part import PartModel, PartFactory

class F579(PartFactory):

    ''' F579 8-bit bidirectional binary counter (3-State) '''

    def state(self, file):
        file.fmt('''
		|	unsigned reg;
		|	bool z;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        if not self.comp.nodes["MR"].net.is_const():
            yield "PIN_MR"
        if not self.comp.nodes["OE"].net.is_const():
            yield "PIN_OE"
        if not self.comp.nodes["CS"].net.is_const():
            yield "PIN_CS"
        if not self.comp.nodes["CEP"].net.is_const():
            yield "PIN_CEP"
        if not self.comp.nodes["CET"].net.is_const():
            yield "PIN_CET"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = NULL;
		|
		|	if (PIN_MR=> && PIN_SR=> && !PIN_CS=> && !PIN_LD=>) {
		|		// Parallel Load
		|		BUS_IO_Z();
		|	}
		|
		|	if (!PIN_MR=>) {
		|		// Async reset
		|		state->reg = 0;
		|		what = "mr ";
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		if (!PIN_SR=>) {
		|			// Sync reset
		|			state->reg = 0;
		|			what = "sr ";
		|		} else if (!PIN_CS=> && !PIN_LD=>) {
		|			// Parallel Load
		|			BUS_IO_READ(state->reg);
		|			what = "pl ";
		|		} else if (PIN_CEP=> || PIN_CET=>) {
		|			// Hold
		|		} else if (PIN_UslashBnot=>) {
		|			// Count Up
		|			state->reg += 1;
		|			what = "up ";
		|		} else {
		|			// Count Down
		|			state->reg += BUS_IO_MASK;
		|			what = "dn ";
		|		}
		|		state->reg &= BUS_IO_MASK;
		|	}
		|
		|	if (PIN_CET=>)
		|		PIN_CO<=(1);
		|	else if (PIN_UslashBnot=>)
		|		PIN_CO<=(state->reg != BUS_IO_MASK);
		|	else
		|		PIN_CO<=(state->reg != 0x00);
		|
		|	if (!PIN_CS=> && PIN_LD=> && !PIN_OE=>) {
		|		BUS_IO_WRITE(state->reg);
		|		if (state->z && what == NULL)
		|		    what = "out ";
		|		state->z = false;
		|	} else {
		|		BUS_IO_Z();
		|		if (!state->z && what == NULL)
		|		    what = "Z ";
		|		state->z = true;
		|	}
		|
		|	if (what == NULL && (state->ctx.do_trace & 2))
		|		what = "- ";
		|	if (what != NULL) {
		|		TRACE(
		|		    << what
		|		    << " clk↑ " << PIN_CLK.posedge()
		|		    << " io " << BUS_IO_TRACE()
		|		    << " oe_ " << PIN_OE?
		|		    << " cs_ " << PIN_CS?
		|		    << " pe_ " << PIN_LD?
		|		    << " u/d_ " << PIN_UslashBnot?
		|		    << " cet_ " << PIN_CET?
		|		    << " cep_ " << PIN_CEP?
		|		    << " sr_ " << PIN_SR?
		|		    << " mr_ " << PIN_MR?
		|		    << " cnt 0x" << std::hex << state->reg
		|		);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F579", PartModel("F579", F579))
    part_lib.add_part("F579X2", PartModel("F579X2", F579))
