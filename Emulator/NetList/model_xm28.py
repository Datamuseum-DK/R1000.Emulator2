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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	bool ahit0145, bhit0246;
		|	bool ah012, bh456;
		|	bool bhit, ahit;
		|	bool set2, set3;
		|	bool ahit0, ahit1, bhit4, bhit5;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
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
		|
		|	bool neg = PIN_CLK.negedge();
		|	bool pos = PIN_CLK.posedge();
		|	bool h1 = PIN_H1=>;
		|	bool q1 = PIN_Q1=>;
		|	bool aehit = PIN_AEH=>;
		|	bool alhit = PIN_ALH=>;
		|	bool behit = PIN_BEH=>;
		|	bool blhit = PIN_BLH=>;
		|	bool drvhit = PIN_DRH=>;
		|	bool exthit = PIN_EHIT=>;
		|
		|	TRACE(
		|		<< " clkv^ " << neg << pos
		|		<< " aeh " << PIN_AEH?
		|		<< " alh " << PIN_ALH?
		|		<< " beh " << PIN_BEH?
		|		<< " blh " << PIN_BLH?
		|		<< " q1v " << PIN_Q1.negedge()
		|		<< " drh " << PIN_DRH?
		|		<< " job " << state->ctx.job
		|	);
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
		|	state->ah012 = !(state->ahit0 || state->ahit1 || !aehit);
		|	state->bh456 = !(state->bhit4 || state->bhit5 || !behit);
		|	bool set2 = !(state->ahit0145 && !exthit);
		|	bool set3 = !(state->bhit0246 && !exthit);
		|
		|	if (!q1) {
		|		state->ahit = !(alhit && state->ah012);
		|		state->bhit = !(blhit && state->bh456);
		|		output.aht = !state->ahit;
		|		output.bht = !state->bhit;
		|	}
		|	output.baht = !(drvhit && state->ahit);
		|	output.bbht = !(drvhit && state->bhit);
		|
		|	if (pos) {
		|		unsigned cmd;
		|		BUS_CMD_READ(cmd);
		|		unsigned pset;
		|		BUS_PSET_READ(pset);
		|		bool mcyc2_next = PIN_MC2N=>;
		|		bool late_abort = PIN_LABRT=>;
		|		bool high_board = PIN_HIGH=>;
		|		bool seta_sel = !(
		|			((0x8 <= pset && pset <= 0xb) && high_board) ||
		|			((0x0 <= pset && pset <= 0x3) && !high_board)
		|		);
		|		bool setb_sel = !(
		|			((0xc <= pset && pset <= 0xf) && high_board) ||
		|			((0x4 <= pset && pset <= 0x7) && !high_board)
		|		);
		|
		|		bool mc2 = PIN_MC2=>;
		|
		|		output.txoen =                (mc2 || !h1 || (cmd != 0x7));
		|		output.txeoe = !(pset & 1) && (mc2 || !h1 || (cmd != 0x7));
		|		output.txloe =  (pset & 1) && (mc2 || !h1 || (cmd != 0x7));
		|
		|		output.txxwe = (cmd == 0x7 && !h1 && !mcyc2_next && mc2);
		|		output.txewe = (
		|			(cmd == 0x7 &&                 !h1 && !mcyc2_next &&  mc2 && !(pset & 1)) ||
		|			(cmd == 0x2 &&                 !h1 && !mcyc2_next &&  mc2) ||
		|			(cmd == 0x2 &&                  h1 &&                !mc2 && !late_abort && state->output.txewe) ||
		|			((cmd == 0xc || cmd == 0xd) && !h1 && !mcyc2_next &&  mc2) ||
		|			((cmd == 0xc || cmd == 0xd) &&  h1 &&                !mc2 && !late_abort && state->output.txewe)
		|		);
		|		output.txlwe = (
		|			(cmd == 0x7 &&                 !h1 && !mcyc2_next &&  mc2 && (pset & 1)) ||
		|			(cmd == 0x2 &&                 !h1 && !mcyc2_next &&  mc2) ||
		|			(cmd == 0x2 &&                  h1 &&                !mc2 && !late_abort && state->output.txlwe) ||
		|			((cmd == 0xc || cmd == 0xd) && !h1 && !mcyc2_next &&  mc2) ||
		|			((cmd == 0xc || cmd == 0xd) &&  h1 &&                !mc2 && !late_abort && state->output.txlwe)
		|		);
		|		output.tgace = !(cmd == 0x7 && !h1 && !mcyc2_next && mc2 && seta_sel);
		|		output.tgbce = !(cmd == 0x7 && !h1 && !mcyc2_next && mc2 && setb_sel);
		|		output.tsc14 = !h1 && !mcyc2_next;
		|	}
		|
		|	if (
		|		set2 != state->set2 ||
		|		set3 != state->set3
		|	) {
		|		state->set2 = set2;
		|		state->set3 = set3;
		|		state->ctx.job |= 2;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM28", PartModel("XM28", XM28))
