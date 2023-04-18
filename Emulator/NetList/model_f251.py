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
   F251 8-Input Multiplexer with 3-STATE Outputs
   ==============================================

   Ref: Fairchild DS009504 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F251(PartFactory):

    ''' F251 8-Input Multiplexer '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        if not self.comp['OE'].net.is_const():
            file.fmt('''
		|
		|	if (PIN_OE=>) {
		|		TRACE(<<"Z");
		|		PIN_Y = sc_logic_Z;
		|		PIN_Ynot = sc_logic_Z;
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|''')

        file.fmt('''
		|	unsigned adr = 0;
		|	bool s;
		|
		|	BUS_S_READ(adr);
		|	switch(adr) {
		|	case 0: s = PIN_A=>; break;
		|	case 1: s = PIN_B=>; break;
		|	case 2: s = PIN_C=>; break;
		|	case 3: s = PIN_D=>; break;
		|	case 4: s = PIN_E=>; break;
		|	case 5: s = PIN_F=>; break;
		|	case 6: s = PIN_G=>; break;
		|	case 7: s = PIN_H=>; break;
		|	}
		|	PIN_Y<=(s);
		|	PIN_Ynot<=(!s);
		|
		|	TRACE(
		|	    << " oe "
		|	    << PIN_OE?
		|	    << " i "
		|	    << PIN_A? << PIN_B? << PIN_C? << PIN_D?
		|	    << PIN_E? << PIN_F? << PIN_G? << PIN_H?
		|	    << " s " << BUS_S_TRACE()
		|	    << " | "
		|	    << s
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F251", PartModel("F251", F251))
