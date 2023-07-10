#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   SEQ 79 Clock Generation
   =======================
'''


from part import PartModel, PartFactory

class XSEQ79(PartFactory):

    ''' XSEQ79 (Dual) D-Type Positive Edge-Triggered Flip-Flop '''

    def sensitive(self):
        yield "PIN_C2EN.pos()"

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tbool diag_enable;\n")

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_DGET<=(state->diag_enable);
		|		PIN_DGEF<=(!state->diag_enable);
		|		return;
		|	}
		|
		|	bool diag_enable = true;
		|
		|	if (PIN_C2EN.posedge()) {
		|		if (PIN_H1E=>) {
		|			diag_enable = false;
		|		} else if (PIN_DSTOP=>) {
		|			diag_enable = false;
		|		}
		|	}
		|	if (diag_enable != state->diag_enable) {
		|		state->ctx.job = 1;
		|		state->diag_enable = diag_enable;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQ79", PartModel("XSEQ79", XSEQ79))
