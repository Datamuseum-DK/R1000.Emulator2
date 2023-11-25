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
   F151 8-Input Multiplexer
   ========================

   Ref: Fairchild DS09481 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F151(PartFactory):
    ''' F151 8-Input Multiplexer '''

    autopin = True

    def private(self):
        ''' private variables '''
        for i in "abcdefgh":
            yield from self.event_or(
               i + "_event",
               "PIN_" + i.upper(),
               "PIN_Enot.posedge_event()",
               "BUS_S",
            )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	unsigned adr = 0;
		|
		|	BUS_S_READ(adr);
		|	if (PIN_Enot=>) adr |= 8;
		|	bool s;
		|	switch (adr) {
		|	case 0: s = PIN_A=>; next_trigger(a_event); break;
		|	case 1: s = PIN_B=>; next_trigger(b_event); break;
		|	case 2: s = PIN_C=>; next_trigger(c_event); break;
		|	case 3: s = PIN_D=>; next_trigger(d_event); break;
		|	case 4: s = PIN_E=>; next_trigger(e_event); break;
		|	case 5: s = PIN_F=>; next_trigger(f_event); break;
		|	case 6: s = PIN_G=>; next_trigger(g_event); break;
		|	case 7: s = PIN_H=>; next_trigger(h_event); break;
		|	default:
		|		s = false;
		|''')
        if not self.comp.nodes["Enot"].net.is_const():

            file.fmt('''
		|		next_trigger(PIN_Enot.negedge_event());
		|''')

        file.fmt('''
		|		break;
		|	}
		|	TRACE(
		|	    << PIN_A?
		|	    << PIN_B?
		|	    << PIN_C?
		|	    << PIN_D?
		|	    << PIN_E?
		|	    << PIN_F?
		|	    << PIN_G?
		|	    << PIN_H?
		|	    << " s "
		|	    << BUS_S_TRACE()
		|	    << " e "
		|	    << PIN_Enot?
		|	    << " n "
		|	    << adr
		|	    << " | "
		|	    << s
		|	);
		|	output.y = s;
		|	output.ynot = !s;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F151", PartModel("F151", F151))
    part_lib.add_part("F151V", PartModel("F151", F151))
