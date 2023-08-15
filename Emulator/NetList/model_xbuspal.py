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
   MEM32 BUSPAL
   =============

'''

from part import PartModel, PartFactory

class XBUSPAL(PartFactory):
    ''' MEM32 BUSPAL '''

    def state(self, file):
        file.fmt('''
		|	bool p_wdrb_sel;
		|	bool p_dreg_oe;
		|	bool p_tagb_oe;
		|	bool p_taga_oe;
		|	bool p_int_boe;
		|	bool p_int_aoe;
		|	bool p_rdr_sel;
		|	bool p_wdra_sel;
		|	bool p_tagb_dir;
		|	bool p_taga_dir;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		TRACE(
		|		    << PIN_Q4?
		|		    << BUS_CMD_TRACE()
		|		    << PIN_MC2N?
		|		    << BUS_DBMD_TRACE()
		|		    << PIN_SETA?
		|		    << PIN_SETB?
		|		    << " | "
		|		    << state->p_taga_dir
		|		    << state->p_tagb_dir
		|		    << state->p_wdra_sel
		|		    << state->p_rdr_sel
		|		    << state->p_int_aoe
		|		    << state->p_int_boe
		|		    << state->p_taga_oe
		|		    << state->p_tagb_oe
		|		    << state->p_dreg_oe
		|		    << state->p_wdrb_sel
		|		);
		|	}
		|	if (state->ctx.job == 1) {
		|		PIN_TADIR<=(state->p_taga_dir);
		|		PIN_TBDIR<=(state->p_tagb_dir);
		|		PIN_INTB<=(state->p_int_boe);
		|		PIN_TAOE<=(state->p_taga_oe);
		|		PIN_TBOE<=(state->p_tagb_oe);
		|		PIN_TADIN<=(!state->p_taga_dir);
		|		PIN_TBDIN<=(!state->p_tagb_dir);
		|		state->ctx.job = 2;
		|		next_trigger(5, SC_NS);
		|		return;
		|	}
		|	if (state->ctx.job == 2) {
		|		PIN_INTAS<=(!state->p_wdra_sel);
		|		PIN_INTBS<=(!state->p_wdrb_sel);
		|		PIN_EXTSL<=(!state->p_rdr_sel);
		|		PIN_INTAN<=(!state->p_int_aoe);
		|		PIN_INTBN<=(!state->p_int_boe);
		|		PIN_DROEN<=(!state->p_dreg_oe);
		|		state->ctx.job = 0;
		|		return;
		|	}
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|	bool p_mcyc2_nxt = PIN_MC2N;
		|	unsigned dbusmode;
		|	BUS_DBMD_READ(dbusmode);
		|	bool p_seta_sel = PIN_SETA;
		|	bool p_setb_sel = PIN_SETB;
		|	bool out_taga_dir = state->p_taga_dir;
		|	bool out_tagb_dir = state->p_tagb_dir;
		|	bool out_wdra_sel = state->p_wdra_sel;
		|	bool out_rdr_sel = state->p_rdr_sel;
		|	bool out_int_aoe = state->p_int_aoe;
		|	bool out_int_boe = state->p_int_boe;
		|	bool out_taga_oe = state->p_taga_oe;
		|	bool out_tagb_oe = state->p_tagb_oe;
		|	bool out_dreg_oe = state->p_dreg_oe;
		|	bool out_wdrb_sel = state->p_wdrb_sel;
		|	if (PIN_Q4.posedge()) {
		|		out_taga_dir =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_seta_sel)) ||
		|		    (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		    (  dbusmode == 0 || dbusmode == 2 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7 );
		|		out_tagb_dir =
		|		    (  cmd == 0xa && dbusmode == 0xa && (!p_setb_sel)) ||
		|		    (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		    (  dbusmode == 8 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7 ) ||
		|		    (  dbusmode == 2 );
		|		out_wdra_sel =
		|		    !(
		|		        (dbusmode == 1 || dbusmode == 3) ||
		|		        (dbusmode == 4)
		|		    );
		|		out_rdr_sel =
		|		    !(
		|		        (dbusmode == 1) || 
		|		        (dbusmode == 6 || dbusmode == 7)
		|		    );
		|		out_int_aoe =
		|		    !(
		|		        (  (cmd == 0xa || cmd == 0xb) && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_seta_sel)) ||
		|		        (  (cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  dbusmode == 0 ) || 
		|			(  4 <= dbusmode && dbusmode <= 7 ) ||
		|		        (  dbusmode == 2 || dbusmode == 3 )
		|		    );
		|		out_int_boe =
		|		    !(
		|		        (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa && (!p_setb_sel)) ||
		|		        (  cmd == 0xb && (!p_mcyc2_nxt) && dbusmode == 1   && (!p_setb_sel)) ||
		|		        (  (cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  dbusmode == 8 ) ||
		|		        (  4 <= dbusmode && dbusmode <= 7) || 
		|		        (  dbusmode == 3 )
		|		    );
		|		out_taga_oe =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 &&   p_setb_sel ) ||
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa &&   p_setb_sel ) ||
		|		    (  (cmd == 0x6 || cmd == 0x7)   && (!p_mcyc2_nxt) && dbusmode == 1 &&   p_setb_sel ) ||
		|		    (  dbusmode == 8 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7) ||
		|		    (  dbusmode == 2 );
		|		out_tagb_oe =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_setb_sel)) ||
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa && (!p_setb_sel)) ||
		|		    (  (cmd == 0x6 || cmd == 0x7) && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_setb_sel)) ||
		|		    (  dbusmode == 0 || dbusmode == 2 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7);
		|		out_dreg_oe =
		|		    (dbusmode == 2);
		|		out_wdrb_sel =
		|		    !(
		|		        (dbusmode == 1 || dbusmode == 3) || 
		|		        (dbusmode == 5)
		|		    );
		|	}
		|
		|	if (
		|	    (out_taga_dir != state->p_taga_dir) ||
		|	    (out_tagb_dir != state->p_tagb_dir) ||
		|	    (out_wdra_sel != state->p_wdra_sel) ||
		|	    (out_rdr_sel != state->p_rdr_sel) ||
		|	    (out_int_aoe != state->p_int_aoe) ||
		|	    (out_int_boe != state->p_int_boe) ||
		|	    (out_taga_oe != state->p_taga_oe) ||
		|	    (out_tagb_oe != state->p_tagb_oe) ||
		|	    (out_dreg_oe != state->p_dreg_oe) ||
		|	    (out_wdrb_sel != state->p_wdrb_sel)) {
		|		state->p_taga_dir = out_taga_dir;
		|		state->p_tagb_dir = out_tagb_dir;
		|		state->p_wdra_sel = out_wdra_sel;
		|		state->p_rdr_sel = out_rdr_sel;
		|		state->p_int_aoe = out_int_aoe;
		|		state->p_int_boe = out_int_boe;
		|		state->p_taga_oe = out_taga_oe;
		|		state->p_tagb_oe = out_tagb_oe;
		|		state->p_dreg_oe = out_dreg_oe;
		|		state->p_wdrb_sel = out_wdrb_sel;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XBUSPAL", PartModel("XBUSPAL", XBUSPAL))
