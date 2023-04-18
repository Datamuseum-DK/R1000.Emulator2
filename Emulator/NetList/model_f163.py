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
   F163 SYNCHRONOUS 4-BIT BINARY COUNTER
   =====================================

   Ref: Fairchild Rev 1.0.2 April 2007
'''


from part import PartModel, PartFactory

class F163(PartFactory):

    ''' F163 F163 SYNCHRONOUS 4-BIT BINARY COUNTER '''

    def state(self, file):
        file.fmt('''
		|	unsigned state;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (!PIN_CLR=>) {
		|		state->state = 0;
		|	} else if (!PIN_LD=>) {
		|		state->state = 0;
		|		BUS_D_READ(state->state);
		|	} else if (PIN_ENP=> && PIN_ENT=>) {
		|		state->state = (state->state + 1) & BUS_D_MASK;
		|	}
		|	TRACE(
		|	    << " clr " << PIN_CLR?
		|	    << " clk " << PIN_CLK?
		|	    << " d " << BUS_D_TRACE()
		|	    << " enp " << PIN_ENP?
		|	    << " ld " << PIN_LD?
		|	    << " ent " << PIN_ENT?
		|	    << "|"
		|	    << std::hex
		|	    << state->state
		|	);
		|	BUS_Q_WRITE(state->state);
		|	PIN_CO<=((state->state == BUS_D_MASK) && PIN_ENT=>);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F163", PartModel("F163", F163))
    part_lib.add_part("F163X3", PartModel("F163X3", F163))
