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
   FIU A-bus parity
   ================

'''

from part import PartModel, PartFactory

class XFAPAR(PartFactory):
    ''' FIU A-bus parity '''

    def state(self, file):
        file.fmt('''
		|	bool moe;
		|	unsigned po;
		|	bool ckopar;
		|	bool offserr;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_MOE<=state->moe;
		|		if (state->moe) {
		|			BUS_PO_Z();
		|		} else {
		|			BUS_PO_WRITE(state->po);
		|		}
		|		return;
		|	}
		|
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q4pos = PIN_Q4.posedge();
		|
		|	unsigned pi = 0;
		|	unsigned b = 0;
		|	unsigned mar_space = 0;
		|	bool space_pev = false;
		|	if (q2pos || q4pos) {
		|		BUS_MSP_READ(mar_space);
		|		space_pev = !(
		|		    ((mar_space >> 0) & 1) ^
		|		    ((mar_space >> 1) & 1) ^
		|		    ((mar_space >> 2) & 1)
		|		);
		|		BUS_B_READ(b);
		|		if (space_pev)
		|			b |= 0x100;
		|		BUS_PI_READ(pi);
		|	}
		|
		|	if (q2pos) {
		|		bool tmp = (b & 1) != (pi & 1);
		|		state->offserr = tmp && state->ckopar;
		|		pi >>= 1;
		|		b >>= 1;
		|		bool ck_adrpar = PIN_CKP=>;
		|		bool perr = (pi != b) && ck_adrpar;
		|		//PIN_AERR<=(!perr);
		|		//PIN_OERR<=(!state->offserr);
		|		bool aerr = !(
		|		    perr ||
		|		    state->offserr ||
		|		    !PIN_TERR=>
		|		);
		|		PIN_AERR<=(aerr);
		|	}
		|	if (q4pos) {
		|		state->ckopar = PIN_CKPN=>;
		|
		|		state->po = b;
		|		state->po &= 0x1fd;
		|		if (PIN_IO2=>)
		|			state->po |= 2;
		|		state->moe = PIN_FAE=>;
		|		if (!state->moe) {
		|			state->ctx.job = 1;
		|			next_trigger(5, sc_core::SC_NS);
		|		}
		|	} else if (PIN_Q4.negedge() && !state->moe) {
		|		state->moe = true;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFAPAR", PartModel("XFAPAR", XFAPAR))
