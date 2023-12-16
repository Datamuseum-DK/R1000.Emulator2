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
   SEQ 34 Code Segment
   ===================

'''

from part import PartModel, PartFactory

class XCODSEG(PartFactory):
    ''' SEQ 34 Code Segment '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned pcseg, retseg, last;
		|''')

    def init(self, file):
        file.fmt('''
		|	// for SEQ_MACRO_RPC_TESTS
		|	state->output.cseg = 0xffffffff;
		|''')

    def sensitive(self):
        yield "PIN_MCLK.pos()"
        yield "PIN_RCLK.pos()"
        yield "PIN_CSEL"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (PIN_RCLK.posedge()) {
		|		state->retseg = state->pcseg;
		|	}
		|	if (PIN_MCLK.posedge()) {
		|		unsigned val;
		|		BUS_VAL_READ(val);
		|		val ^= BUS_VAL_MASK;
		|		state->pcseg = val;
		|	}
		|	if (!PIN_CSEL) {
		|		output.cseg = state->pcseg;
		|	} else {
		|		output.cseg = state->retseg;
		|	}
		|	if (output.cseg && state->last != output.cseg) {
		|		state->last = output.cseg;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCODSEG", PartModel("XCODSEG", XCODSEG))
