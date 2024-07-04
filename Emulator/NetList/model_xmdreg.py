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
   MEM Diag Reg
   ============

'''

from part import PartModelDQ, PartFactory

class XMDREG(PartFactory):
    ''' MEM Diag Reg '''

    autopin = True

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_QTOE"

    def state(self, file):
        file.fmt('''
		|	uint64_t typ, val;
		|	uint8_t par, chk0, chk1;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_CLK.posedge()) {
		|		unsigned chk = 0;
		|		BUS_DT_READ(state->typ);
		|		BUS_DV_READ(state->val);
		|		BUS_DC_READ(chk);
		|		state->chk0 = chk >> 5;
		|		state->chk1 = chk & 0x1f;
		|		if (chk & 0x100)	state->chk0 |= 0xf0;
		|		if (chk & 0x100)	state->chk1 |= 0xe0;
		|		state->par = 0xff;
		|	}
		|
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt)
		|		output.qt = state->typ;
		|
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv)
		|		output.qv = state->val;
		|
		|	output.z_qc = PIN_QCOE=>;
		|	if (!output.z_qc) {
		|		output.qc = (state->chk0 & 0xf) << 5;
		|		output.qc |= state->chk1 & 0x1f;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMDREG", PartModelDQ("XMDREG", XMDREG))
