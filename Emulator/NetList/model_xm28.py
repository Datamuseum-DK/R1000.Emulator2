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
   MEM32 page 28
   =============

'''

# TEST_HIT_FLOPS tests [AB]_AHIT~ but not [AB]HIT~

from part import PartModel, PartFactory

class XM28(PartFactory):
    ''' MEM32 page28 '''

    def state(self, file):
        file.fmt('''
		|	bool ahit0, ahit1, bhit4, bhit5, ahit0145, bhit0246;
		|	bool ah012, bh456;
		|	bool h01, h02;
		|	bool set2, set3;
		|	bool bhit, ahit;
		|''')

    def sensitive(self):
        yield "PIN_CLK.neg()"
        yield "PIN_AEH"
        yield "PIN_ALH"
        yield "PIN_BEH"
        yield "PIN_BLH"
        yield "PIN_Q1.neg()"
        yield "PIN_DRH"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool neg = PIN_CLK.negedge();
		|	bool h1 = PIN_H1=>;
		|	bool q1 = PIN_Q1=>;
		|	bool aehit = PIN_AEH=>;
		|	bool alhit = PIN_ALH=>;
		|	bool behit = PIN_BEH=>;
		|	bool blhit = PIN_BLH=>;
		|	bool drvhit = PIN_DRH=>;
		|	bool exthit = PIN_EHIT=>;
		|
		|	if (state->ctx.job) {
		|		PIN_SET2 = state->set2 ? sc_logic_Z : sc_logic_0;
		|		PIN_SET3 = state->set3 ? sc_logic_Z : sc_logic_0;
		|		state->ctx.job = 0;
		|	}
		|
		|	if (neg && !h1) {
		|		state->ahit0 = !aehit           &&  behit &&  blhit;
		|		state->ahit1 =  aehit && !alhit &&  behit &&  blhit;
		|		state->bhit4 =                     !behit;
		|		state->bhit5 =                      behit && !blhit;
		|	}
		|	if (neg && h1) {
		|		state->ahit0145 =
		|		    (drvhit && state->bhit5) ||
		|		    (drvhit && state->bhit4) ||
		|		    (drvhit && behit && blhit && state->ahit0) ||
		|		    (drvhit && behit && blhit && state->ahit1)
		|		;
		|		state->bhit0246 =
		|		    (drvhit && state->bhit4) ||
		|		    (drvhit && !behit &&                           !state->bhit5) ||
		|		    (drvhit &&  behit && blhit &&  state->ahit0) ||
		|		    (drvhit && !aehit && blhit && !state->ahit1 && !state->bhit5)
		|		;
		|	}
		|	bool ah012 = !(state->ahit0 || state->ahit1 || !aehit);
		|	bool bh456 = !(state->bhit4 || state->bhit5 || !behit);
		|	bool set2 = !(state->ahit0145 && !exthit);
		|	bool set3 = !(state->bhit0246 && !exthit);
		|
		|	if (!q1) {
		|		state->ahit = !(alhit && ah012);
		|		state->bhit = !(blhit && bh456);
		|		PIN_AHT<=(!state->ahit);
		|		PIN_BHT<=(!state->bhit);
		|	}
		|	bool b_ahit = !(drvhit && state->ahit);
		|	PIN_BAHT<=(b_ahit);
		|	bool b_bhit = !(drvhit && state->bhit);
		|	PIN_BBHT<=(b_bhit);
		|
		|	if (
		|	    state->ahit0145 != state->h01 ||
		|	    state->bhit0246 != state->h02 ||
		|	    set2 != state->set2 ||
		|	    set3 != state->set3 ||
		|	    ah012 != state->ah012 ||
		|	    bh456 != state->bh456
		|	) {
		|		state->h01 = state->ahit0145;
		|		state->h02 = state->bhit0246;
		|		state->set2 = set2;
		|		state->set3 = set3;
		|		state->ah012 = ah012;
		|		state->bh456 = bh456;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM28", PartModel("XM28", XM28))
