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
		|	bool bhit, ahit;
		|	bool ahit0, ahit1, bhit4, bhit5;
		|	bool labort;
		|	bool dradpal_p22;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_AEH"
        yield "PIN_ALH"
        yield "PIN_BEH"
        yield "PIN_BLH"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	bool clk2x_neg = PIN_CLK.negedge();
		|	bool clk2x_pos = PIN_CLK.posedge();
		|	bool h1 = PIN_H1=>;
		|	bool q1 = PIN_Q1=>;
		|	bool q1pos = clk2x_neg && h1;
		|	bool q2pos = clk2x_pos && h1;
		|	bool q3pos = clk2x_neg && !h1;
		|	bool q4pos = clk2x_pos && !h1;
		|	bool aehit = PIN_AEH=>;
		|	bool alhit = PIN_ALH=>;
		|	bool behit = PIN_BEH=>;
		|	bool blhit = PIN_BLH=>;
		|	bool miss = aehit && alhit && behit && blhit;
		|	bool exthit = PIN_EHIT=>;
		|	bool high_board = !PIN_LOBRD=>;
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|	bool mcyc2 = PIN_MC2=>;
		|	bool mcyc2_next = PIN_MC2N=>;
		|
		|	if (q3pos) {
		|		state->ahit0 = !aehit           &&  behit &&  blhit;
		|		state->ahit1 =  aehit && !alhit &&  behit &&  blhit;
		|		state->bhit4 =                     !behit;
		|		state->bhit5 =                      behit && !blhit;
		|	}
		|	if (q1pos) {
		|		state->ahit0145 = (
		|		    (state->bhit5) ||
		|		    (state->bhit4) ||
		|		    (behit && blhit && state->ahit0) ||
		|		    (behit && blhit && state->ahit1)
		|		);
		|		state->bhit0246 = (
		|		    (state->bhit4) ||
		|		    (!behit &&                           !state->bhit5) ||
		|		    ( behit && blhit &&  state->ahit0) ||
		|		    (!aehit && blhit && !state->ahit1 && !state->bhit5)
		|		);
		|	}
		|	if (q3pos) {
		|		output.tagw = mcyc2 && !mcyc2_next && (
		|		    cmd == 0xc || cmd == 0xd || cmd == 0x7 || cmd == 0x2
		|		);
		|	}
		|	output.z_seta = !(state->ahit0145 && !exthit);
		|	output.z_setb = !(state->bhit0246 && !exthit);
		|	output.seta = output.z_seta;
		|	output.setb = output.z_setb;
		|
		|	if (!q1) {
		|		output.aht = alhit && !(state->ahit0 || state->ahit1 || !aehit);
		|		output.bht = blhit && !(state->bhit4 || state->bhit5 || !behit);
		|		output.baht = output.aht;
		|		output.bbht = output.bht;
		|	}
		|
		|	unsigned pset;
		|	BUS_PSET_READ(pset);
		|
		|	bool eabort_y = !(PIN_EABT=> && PIN_ELABT=>);
		|	bool labort_y = !(PIN_LABT=> && PIN_ELABT=> && !h1);
		|
		|	if (clk2x_pos) {
		|
		|		bool seta_sel = !(
		|			((0x8 <= pset && pset <= 0xb) && high_board) ||
		|			((0x0 <= pset && pset <= 0x3) && !high_board)
		|		);
		|		bool setb_sel = !(
		|			((0xc <= pset && pset <= 0xf) && high_board) ||
		|			((0x4 <= pset && pset <= 0x7) && !high_board)
		|		);
		|
		|		bool txoen = mcyc2 || q4pos || (cmd != 0x7);
		|		output.txeoe = !(pset & 1) && txoen;
		|		output.txloe =  (pset & 1) && txoen;
		|
		|		output.txxwe = (cmd == 0x7 && q4pos && !mcyc2_next && mcyc2);
		|		bool cmd_2cd = (cmd == 0x2) || (cmd == 0xc) || (cmd == 0xd);
		|		output.txewe = (
		|			(output.txxwe && !(pset & 1)) ||
		|			(cmd_2cd && q4pos &&  mcyc2 && !mcyc2_next) ||
		|			(cmd_2cd && q2pos && !mcyc2 && !state->labort && state->output.txewe)
		|		);
		|		output.txlwe = (
		|			(output.txxwe && (pset & 1)) ||
		|			(cmd_2cd && q4pos &&  mcyc2 && !mcyc2_next) ||
		|			(cmd_2cd && q2pos && !mcyc2 && !state->labort && state->output.txlwe)
		|		);
		|		output.tgace = !(output.txxwe && seta_sel);
		|		output.tgbce = !(output.txxwe && setb_sel);
		|
		|		output.rclke = labort_y;
		|
		|		if (q4pos) {
		|			state->labort = labort_y;
		|			output.eabrt = eabort_y;
		|			output.labrt = state->labort;
		|			output.tsc14 = !mcyc2_next && output.labrt;
		|		}
		|	}
		|
		|	if (clk2x_neg) {
		|		if (!mcyc2) {
		|			output.da2sl = false;
		|			if (state->dradpal_p22 && state->output.da2sl) {
		|				output.daa2d = behit && aehit;
		|			}
		|		} else if (q1pos) {
		|			output.da2sl = false;
		|			output.daa1d = false;
		|			output.daa2d = true;
		|		} else {	// q3pos
		|
		|			bool pht26 = !(
		|				((pset & 0xb) == 0xa &&  high_board) ||
		|				((pset & 0xb) == 0x2 && !high_board)
		|			);
		|
		|			output.da2sl = miss && (((cmd & 0x6) == 0x4) || ((cmd & 0xc) == 0x0));
		|
		|			output.daa1d = !miss;
		|
		|			output.daa2d = behit && aehit && (
		|			    ( !alhit ) ||
		|			    ( !blhit ) ||
		|			    ( pht26 ) ||
		|			    ( (cmd & 0x6) == 0x4 ) ||
		|			    ( (cmd & 0xc) == 0x0 )
		|			);
		|		}
		|
		|		state->dradpal_p22 = mcyc2;
		|	}
		|	if (clk2x_neg) {
		|		// TAGAPAL
		|		bool p_lru_update = output.lrup;
		|		output.lrup =
		|		    ( q3pos && (!mcyc2_next) && mcyc2 && (cmd == 0xc || cmd == 0xd)) ||
		|		    ( q3pos && (!mcyc2_next) && mcyc2 && (cmd == 0x2 || cmd == 0x3)) ||
		|		    ( q1pos && (!state->labort) && p_lru_update );
		|		output.t12y =
		|		    ( q1pos && ((cmd & 0x6) == 0x4)) ||
		|		    ( q1pos && ((cmd & 0xc) == 0x0)) || 
		|		    ( q1pos && !mcyc2 ) ||
		|		    ( mcyc2 && (pset & 3) > 1 && ((cmd & 0x6) == 0x6)) ||
		|		    ( mcyc2 && (pset & 3) > 1 && ((cmd & 0xa) == 0xa)) ||
		|		    ( mcyc2 && (pset & 3) > 1 && ((cmd & 0xc) == 0x8));
		|		output.t13y =
		|		    ( q3pos && ((cmd & 0x6) == 0x4)) ||
		|		    ( q3pos && ((cmd & 0xc) == 0x0)) ||
		|		    ( q3pos && !mcyc2 ) ||
		|		    ( mcyc2 && ((pset & 3) == 1 || (pset & 3) == 2) && ((cmd & 0x6) == 0x6)) ||
		|		    ( mcyc2 && ((pset & 3) == 1 || (pset & 3) == 2) && ((cmd & 0xa) == 0xa)) ||
		|		    ( mcyc2 && ((pset & 3) == 1 || (pset & 3) == 2) && ((cmd & 0xc) == 0x8));
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM28", PartModel("XM28", XM28))
