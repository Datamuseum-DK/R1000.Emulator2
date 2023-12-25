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
   MEM32 CMDPAL
   ============

'''

from part import PartModel, PartFactory

class XCMDPAL(PartFactory):
    ''' MEM32 CMDPAL '''

    def state(self, file):
        file.fmt('''
		unsigned cmd;
		int p_mcyc2;
		int p_mcyc1;
		int p_mcyc2_next;
		|''')

    def sensitive(self):
        yield "PIN_H2.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_CMD_WRITE(state->cmd);
		|		PIN_MC2N<=(state->p_mcyc2_next);
		|		PIN_MC1<=(state->p_mcyc1);
		|		PIN_MC2<=(state->p_mcyc2);
		|		return;
		|	}
		|	bool p_h2 = PIN_H2=>;
		|	unsigned mcmd;
		|	BUS_MCMD_READ(mcmd);
		|	bool p_cmdcont = PIN_CCNT=>;
		|	bool p_early_abort = PIN_ABRT=>;
		|	bool p_mcyc1_hd = state->p_mcyc1;
		|	bool p_mcyc2_next_hd = state->p_mcyc2_next;
		|	bool p_mcyc2_hd = state->p_mcyc2;
		|	int out_mcyc2_next;
		|	int out_mcyc1;
		|	int out_mcyc2;
		|	unsigned cmd = 0;
		|	if (p_early_abort && p_h2 && p_mcyc2_hd) {
		|		cmd = 0;
		|	} else if (p_early_abort && !p_h2 && p_mcyc2_next_hd) {
		|		cmd = 0;
		|	} else {
		|		cmd = mcmd ^ 0xf;
		|	}
		|	out_mcyc2_next =
		|	    !(
		|	        ((!p_h2) && (mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|	        ((!p_cmdcont) && (!p_early_abort) && (!p_mcyc2_next_hd)) ||
		|	        (  p_h2  && (!p_mcyc2_next_hd))
		|	    );
		|	out_mcyc1 =
		|	    !(
		|	        ((!p_h2) && (mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|	        (  p_h2  && (!p_mcyc1_hd))
		|	    );
		|	out_mcyc2 =
		|	    !(
		|	        ((!p_h2) && (!p_mcyc2_next_hd)) ||
		|	        (  p_h2  && (!p_mcyc2_hd))
		|	    );
		|	if (
		|	    (cmd != state->cmd) ||
		|	    (out_mcyc2_next != state->p_mcyc2_next) ||
		|	    (out_mcyc1 != state->p_mcyc1) ||
		|	    (out_mcyc2 != state->p_mcyc2)) {
		|		state->cmd = cmd;;
		|		state->p_mcyc2_next = out_mcyc2_next;
		|		state->p_mcyc1 = out_mcyc1;
		|		state->p_mcyc2 = out_mcyc2;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	TRACE(
		|	    << " h2 " << PIN_H2?
		|	    << " mcmd " << BUS_MCMD_TRACE()
		|	    << " ccnt " << PIN_CCNT?
		|	    << " abrt " << PIN_ABRT?
		|	    << " | "
		|	    << " j " << state->ctx.job
		|	    << " cmd " << state->cmd
		|	    << " mc1 " << state->p_mcyc1
		|	    << " mc2 " << state->p_mcyc2
		|	    << " mc2n " << state->p_mcyc2_next
		|	);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCMDPAL", PartModel("XCMDPAL", XCMDPAL))
