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
   SEQ 52 CSA
   ==========

'''

from part import PartModel, PartFactory

class XSEQ52CSA(PartFactory):
    ''' SEQ 52 CSA '''

    def state(self, file):
        file.fmt('''
		|	bool overflow, underflow;
		|	unsigned in_csa;
		|''')

    def xxsensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_CSA_WRITE(state->in_csa);
		|		PIN_UFL<=(state->underflow);
		|		PIN_OFL<=(state->overflow);
		|	}
		|		
		|	unsigned csa_nve, csa_dec;
		|	unsigned in_csa = state->in_csa;
		|
		|	BUS_NVE_READ(csa_nve);
		|	BUS_DEC_READ(csa_dec);
		|	if (PIN_CLK.posedge()) {
		|		in_csa = csa_nve;
		|	}
		|	bool underflow = csa_nve >= (csa_dec & 7);
		|	bool overflow = csa_nve <= ((csa_dec >> 3) | 12);
		|	if (underflow != state->underflow ||
		|	    overflow != state->overflow ||
		|	    in_csa != state->in_csa) {
		|		state->ctx.job = 1;
		|		state->underflow = underflow;
		|		state->overflow = overflow;
		|		state->in_csa = in_csa;;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|		
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQ52CSA", PartModel("XSEQ52CSA", XSEQ52CSA))
