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
   MEM32 TPARPAL
   =============

'''

from part import PartModel, PartFactory

class XTPARPAL(PartFactory):
    ''' MEM32 TPARPAL '''

    def state(self, file):
        file.fmt('''
		|	bool p_ts_par_s1;
		|	bool p_par_err;
		|	bool p_tsa_par_err;
		|	bool p_tsb_par_err;
		|	bool p_tag_par_err;
		|	bool p_ts_epar_dis;
		|	bool p_ts_par_s0;
		|''')

    def sensitive(self):
        # yield "PIN_H1"
        yield "PIN_CTSP"
        yield "PIN_TAGPE"
        yield "PIN_TPM0"
        yield "PIN_TPM1"
        yield "PIN_TSAPER"
        yield "PIN_TSAPED"
        yield "PIN_TSBPER"
        yield "PIN_TSBPED"
        yield "PIN_MARPE"

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "h1_event",
            "PIN_H1",
            "PIN_CTSP",
            "PIN_TAGPE",
            "PIN_TPM0",
            "PIN_TPM1",
            "PIN_TSAPER",
            "PIN_TSAPED",
            "PIN_TSBPER",
            "PIN_TSBPED",
            "PIN_MARPE",
        )


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool p_ts_par_mode0 = PIN_TPM0=>;
		|	bool p_ts_par_mode1 = PIN_TPM1=>;
		|
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_TSP0<=(state->p_ts_par_s0);
		|		PIN_TSP1<=(state->p_ts_par_s1);
		|		PIN_TPD<=(state->p_ts_epar_dis);
		|		PIN_TGPEY<=(state->p_tag_par_err);
		|		PIN_TSAPE<=(state->p_tsb_par_err);
		|		PIN_TSBPE<=(state->p_tsa_par_err);
		|		PIN_PERR<=(state->p_par_err);
		|		if (!p_ts_par_mode0 || p_ts_par_mode1)
		|			next_trigger(h1_event);
		|		return;
		|	}
		|	bool p_check_tsepar = PIN_CTSP=>;
		|	bool p_tag_par_err = PIN_TAGPE=>;
		|	bool p_h1 = PIN_H1=>;
		|	bool p_tsa_perr = PIN_TSAPER=>;
		|	bool p_tsa_perr_od = PIN_TSAPED=>;
		|	bool p_tsb_perr = PIN_TSBPER=>;
		|	bool p_tsb_perr_od = PIN_TSBPED=>;
		|	bool p_mar_par_err = PIN_MARPE=>;
		|	bool out_ts_par_s0 =
		|	    !(
		|	        (                       p_ts_par_mode1  &&   p_h1 ) ||
		|	        (  p_tag_par_err  &&  (!p_ts_par_mode1)) ||
		|	        ((!p_ts_par_mode0) && (!p_ts_par_mode1)) ||
		|	        ((!p_check_tsepar) && (!p_ts_par_mode1) &&                  (!p_tsa_perr_od) && (!p_tsb_perr_od)) ||
		|	        (                     (!p_ts_par_mode1) && (!p_tsa_perr) && (!p_tsa_perr_od) && (!p_tsb_perr) && (!p_tsb_perr_od))
		|	    );
		|	bool out_ts_par_s1 =
		|	    !(
		|	        ((!p_ts_par_mode0)) ||
		|	        (                       p_ts_par_mode1  &&   p_h1 ) ||
		|	        (  p_tag_par_err  &&  (!p_ts_par_mode1)) ||
		|	        ((!p_check_tsepar) && (!p_ts_par_mode1) &&                  (!p_tsa_perr_od) && (!p_tsb_perr_od)) ||
		|	        (                     (!p_ts_par_mode1) && (!p_tsa_perr) && (!p_tsa_perr_od) && (!p_tsb_perr) && (!p_tsb_perr_od))
		|	    );
		|	bool out_ts_epar_dis =
		|	    !(
		|	        ((!p_ts_par_mode0)) ||
		|	        ((!p_ts_par_mode1) &&   p_tsa_perr_od ) ||
		|	        ((!p_ts_par_mode1) &&   p_tsb_perr_od )
		|	    );
		|	bool out_tag_par_err =
		|	    !(
		|	        (  p_ts_par_mode1 ) ||
		|	        (                     (!p_tag_par_err) && (!p_ts_par_mode0)) ||
		|	        ((!p_check_tsepar) && (!p_tag_par_err) &&                  (!p_tsa_perr_od) &&                  (!p_tsb_perr_od)) ||
		|	        (                     (!p_tag_par_err) && (!p_tsa_perr) && (!p_tsa_perr_od) && (!p_tsb_perr) && (!p_tsb_perr_od))
		|	    );
		|	bool out_tsb_par_err =
		|	    !(
		|	        ((!p_tsa_perr)) ||
		|	        ((!p_check_tsepar) &&   p_ts_par_mode1 ) ||
		|	        ((!p_check_tsepar) &&   p_ts_par_mode0 )
		|	    );
		|	bool out_tsa_par_err =
		|	    !(
		|	        ((!p_tsb_perr)) ||
		|	        ((!p_check_tsepar) &&   p_ts_par_mode1 ) ||
		|	        ((!p_check_tsepar) &&   p_ts_par_mode0 )
		|	    );
		|	bool out_par_err =
		|	    !(
		|	        ((!p_tag_par_err) &&   p_ts_par_mode1  &&                    (!p_mar_par_err)) ||
		|	        ((!p_tag_par_err) && (!p_ts_par_mode0) &&                    (!p_mar_par_err)) ||
		|	        ((!p_tag_par_err) && (!p_tsa_perr_od) && (!p_tsb_perr_od) && (!p_mar_par_err))
		|	    );
		|
		|	if (
		|	    (out_ts_par_s0 != state->p_ts_par_s0) ||
		|	    (out_ts_epar_dis != state->p_ts_epar_dis) ||
		|	    (out_tag_par_err != state->p_tag_par_err) ||
		|	    (out_tsb_par_err != state->p_tsb_par_err) ||
		|	    (out_tsa_par_err != state->p_tsa_par_err) ||
		|	    (out_par_err != state->p_par_err) ||
		|	    (out_ts_par_s1 != state->p_ts_par_s1)) {
		|		state->p_ts_par_s0 = out_ts_par_s0;
		|		state->p_ts_epar_dis = out_ts_epar_dis;
		|		state->p_tag_par_err = out_tag_par_err;
		|		state->p_tsb_par_err = out_tsb_par_err;
		|		state->p_tsa_par_err = out_tsa_par_err;
		|		state->p_par_err = out_par_err;
		|		state->p_ts_par_s1 = out_ts_par_s1;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|		TRACE(
		|		    << PIN_H1?
		|		    << " ctsp " << PIN_CTSP?
		|		    << " tpm " << PIN_TPM0? << PIN_TPM1?
		|		    << " tsaper " << PIN_TSAPER?
		|		    << " tsbper " << PIN_TSBPER?
		|		    << " marpe " << PIN_MARPE?
		|		    << " tagpe " << PIN_TAGPE?
		|		    << " tsaped " << PIN_TSAPED?
		|		    << " tsbped " << PIN_TSBPED?
		|		    << " | "
		|		    << " tsp " << state->p_ts_par_s0 << state->p_ts_par_s1
		|		    << " tpd " << state->p_ts_epar_dis
		|		    << " tgpey " << state->p_tag_par_err
		|		    << " tsape " << state->p_tsb_par_err
		|		    << " tsbpe " << state->p_tsa_par_err
		|		    << " perr " << state->p_par_err
		|		);
		|	} else if (!p_ts_par_mode0 || p_ts_par_mode1) {
		|		next_trigger(h1_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTPARPAL", PartModel("XTPARPAL", XTPARPAL))

