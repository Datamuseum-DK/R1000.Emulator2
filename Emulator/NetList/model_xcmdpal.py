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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	int p_mcyc2_next;
		|''')

    def sensitive(self):
        yield "PIN_H1.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_H1.posedge()) {
		|		unsigned mcmd;
		|		BUS_MCMD_READ(mcmd);
		|		bool p_cmdcont = PIN_CCNT=>;
		|		bool p_early_abort = PIN_ABRT=>;
		|		bool p_mcyc2_next_hd = state->p_mcyc2_next;
		|		int out_mcyc2_next;
		|		unsigned cmd = 0;
		|		if (p_early_abort && p_mcyc2_next_hd) {
		|			cmd = 0;
		|		} else {
		|			cmd = mcmd ^ 0xf;
		|		}
		|		out_mcyc2_next =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|		        ((!p_cmdcont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		|		    );
		|		output.cyo =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd)
		|		    );
		|		output.cyt = p_mcyc2_next_hd;
		|
		|		output.cmd = cmd;
		|		state->p_mcyc2_next = output.mc2n = out_mcyc2_next;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCMDPAL", PartModel("XCMDPAL", XCMDPAL))
