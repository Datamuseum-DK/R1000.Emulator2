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
		|	bool ahit0, ahit1, bhit4, bhit5;
		|	bool labort, eabort;
		|	bool dradpal_p22;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_AEH"
        yield "PIN_ALH"
        yield "PIN_BEH"
        yield "PIN_BLH"
        yield "PIN_Q1"
        yield "PIN_H1"
        yield "PIN_DRH"
        yield "BUS_PSET_SENSITIVE()"
        yield "BUS_DBM_SENSITIVE()"

        #yield "BUS_TRDR_SENSITIVE()"
        #yield "BUS_LAR_SENSITIVE()"
        #yield "PIN_DDISA"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	bool clk2x_neg = PIN_CLK.negedge();
		|	bool clk2x_pos = PIN_CLK.posedge();
		|	bool h1 = PIN_H1=>;
		|	bool q1 = PIN_Q1=>;
		|	bool q4pos = PIN_Q1.negedge();
		|	bool aehit = PIN_AEH=>;
		|	bool alhit = PIN_ALH=>;
		|	bool behit = PIN_BEH=>;
		|	bool blhit = PIN_BLH=>;
		|	bool drvhit = PIN_DRH=>;
		|	bool exthit = PIN_EHIT=>;
		|	bool high_board = PIN_HIGH=>;
		|	bool mc2 = PIN_MC2=>;
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|
		|	TRACE(
		|		<< " clkv^ " << clk2x_neg << clk2x_pos
		|		<< " aeh " << PIN_AEH?
		|		<< " alh " << PIN_ALH?
		|		<< " beh " << PIN_BEH?
		|		<< " blh " << PIN_BLH?
		|		<< " q1v " << PIN_Q1.negedge()
		|		<< " drh " << PIN_DRH?
		|		<< " job " << state->ctx.job
		|	);
		|
		|	if (clk2x_neg && !h1) {
		|		state->ahit0 = !aehit           &&  behit &&  blhit;
		|		state->ahit1 =  aehit && !alhit &&  behit &&  blhit;
		|		state->bhit4 =                     !behit;
		|		state->bhit5 =                      behit && !blhit;
		|	}
		|	if (clk2x_neg && h1) {
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
		|	output.z_seta = !(state->ahit0145 && !exthit);
		|	output.z_setb = !(state->bhit0246 && !exthit);
		|	output.seta = output.z_seta;
		|	output.setb = output.z_setb;
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
		|	unsigned pset;
		|	BUS_PSET_READ(pset);
		|	unsigned dbus_mode;
		|	BUS_DBM_READ(dbus_mode);
		|
		|	output.phae = !(
		|		(pset == 0x0 && (!high_board) &&  h1   && (!(dbus_mode & 4))) ||
		|		(pset == 0x2 && (!high_board) && (!h1) && (!(dbus_mode & 4))) ||
		|		(pset == 0x8 &&   high_board  &&   h1  && (!(dbus_mode & 4))) ||
		|		(pset == 0xa &&   high_board  && (!h1) && (!(dbus_mode & 4))) ||
		|		(dbus_mode == 0xd || dbus_mode == 0xf)  
		|	);
		|
		|	output.phal = !(
		|		(pset == 0x1 && (!high_board) &&  h1   && (!(dbus_mode & 4))) ||
		|		(pset == 0x3 && (!high_board) && (!h1) && (!(dbus_mode & 4))) ||
		|		(pset == 0x9 &&   high_board  &&   h1  && (!(dbus_mode & 4))) ||
		|		(pset == 0xb &&   high_board  && (!h1) && (!(dbus_mode & 4))) ||
		|		(dbus_mode == 0xd || dbus_mode == 0xf)  
		|	);
		|
		|	output.phbe = !(
		|		(pset == 0x4 && (!high_board) &&  h1   && (!(dbus_mode & 4))) ||
		|		(pset == 0x6 && (!high_board) && (!h1) && (!(dbus_mode & 4))) ||
		|		(pset == 0xc &&   high_board  &&   h1  && (!(dbus_mode & 4))) ||
		|		(pset == 0xe &&   high_board  && (!h1) && (!(dbus_mode & 4))) ||
		|		(dbus_mode == 0xe || dbus_mode == 0xf)  
		|	);
		|
		|	output.phbl = !(
		|		(pset == 0x5 && (!high_board) &&  h1   && (!(dbus_mode & 4))) ||
		|		(pset == 0x7 && (!high_board) && (!h1) && (!(dbus_mode & 4))) ||
		|		(pset == 0xd &&   high_board  &&   h1  && (!(dbus_mode & 4))) ||
		|		(pset == 0xf &&   high_board  && (!h1) && (!(dbus_mode & 4))) ||
		|		(dbus_mode == 0xe || dbus_mode == 0xf)  
		|	);
		|
		|	output.setas = !(
		|		((pset & 0xc) == 0x8 &&  high_board) ||
		|		((pset & 0xc) == 0x0 && !high_board)
		|	);
		|
		|	output.setbs = !(
		|		((pset & 0xc) == 0xc &&  high_board) ||
		|		((pset & 0xc) == 0x4 && !high_board)
		|	);
		|
		|	output.pht26 = !(
		|		((pset & 0xb) == 0xa &&  high_board) ||
		|		((pset & 0xb) == 0x2 && !high_board)
		|	);
		|	output.dfhit = !(dbus_mode >= 0xc);
		|
		|	bool eabort_y = !(PIN_DEABT=> && PIN_EABT=> && PIN_ELABT=>);
		|	bool labort_y = !(PIN_DLABT=> && PIN_LABT=> && PIN_ELABT=> && !h1);
		|
		|	if (clk2x_pos) {
		|		bool mcyc2_next = PIN_MC2N=>;
		|		bool late_abort = state->labort;
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
		|
		|		output.rclke = labort_y;
		|	}
		|
		|	if (q4pos) {
		|		state->labort = labort_y;
		|		state->eabort = eabort_y;
		|		output.eabrt = state->eabort;
		|		output.labrt = state->labort;
		|		output.abort = !(state->labort || output.eabrt);
		|	}
		|
		|	if (clk2x_neg) {
		|		bool d_dis_adr = PIN_DDISA=>;
		|		bool trace_dra1 = PIN_TRDR1=>;
		|		bool trace_dra2 = PIN_TRDR2=>;
		|		bool lar_2 = PIN_LAR2=>;
		|		bool lar_3 = PIN_LAR3=>;
		|
		|		output.da2sl =
		|		    ((cmd & 0x6) == 0x4 && (!d_dis_adr) && (!h1) && mc2 && blhit && behit && alhit && aehit ) ||
		|		    ((cmd & 0xc) == 0x0 && (!d_dis_adr) && (!h1) && mc2 && blhit && behit && alhit && aehit );
		|
		|		output.daa1d =
		|		    (  d_dis_adr  &&                    trace_dra1 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa1d ) ||
		|		    ((!d_dis_adr) &&   h1  &&   mc2  && lar_2 ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && blhit && behit && alhit && aehit );
		|
		|		output.dba1d =
		|		    (  d_dis_adr  &&                    trace_dra1 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa1d ) ||
		|		    ((!d_dis_adr) &&   h1  &&   mc2  && lar_2 ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && blhit && behit && alhit && aehit );
		|
		|		output.daa2d =
		|		    (  d_dis_adr  &&                    trace_dra2 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa2d  && (!state->output.da2sl)) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa2d  && (!state->dradpal_p22)) ||
		|		    ((!d_dis_adr) &&   h1  &&   mc2  && lar_3 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && behit && aehit && state->dradpal_p22 && state->output.da2sl ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && (!alhit) && behit && aehit ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && (!blhit) && behit && aehit ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && state->output.pht26 && behit && aehit ) ||
		|		    ((cmd & 0x6) == 0x4 && (!d_dis_adr) && (!h1) && mc2 && behit && aehit ) ||
		|		    ((cmd & 0xc) == 0x0 && (!d_dis_adr) && (!h1) && mc2 && behit && aehit );
		|
		|		output.dba2d =
		|		    (  d_dis_adr  &&   trace_dra2 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa2d  && (!state->output.da2sl)) ||
		|		    ((!d_dis_adr) &&          (!mc2) && state->output.daa2d  && (!state->dradpal_p22)) ||
		|		    ((!d_dis_adr) &&   h1  &&   mc2  && lar_3 ) ||
		|		    ((!d_dis_adr) &&          (!mc2) && behit && aehit && state->dradpal_p22 && state->output.da2sl ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && (!alhit) && behit && aehit ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && (!blhit) && behit && aehit ) ||
		|		    ((!d_dis_adr) && (!h1) &&   mc2  && state->output.pht26 && behit && aehit ) ||
		|		    ((cmd & 0x6) == 0x4 && (!d_dis_adr) && (!h1) && mc2 && behit && aehit ) ||
		|		    ((cmd & 0xc) == 0x0 && (!d_dis_adr) && (!h1) && mc2 && behit && aehit );
		|
		|		state->dradpal_p22 = mc2;
		|
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM28", PartModel("XM28", XM28))
