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
        yield "PIN_QDGOE"

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
		|		unsigned mode, diag = 0, chk = 0;
		|		BUS_S_READ(mode);
		|		switch (mode) {
		|		case 1:
		|			state->par >>= 1;
		|			state->par &= 0x7f;
		|			if (state->val & (1ULL << 0)) state->par |= 0x80;
		|
		|			state->chk1 >>= 1;
		|			state->chk1 &= 0x7f;
		|			if (state->val & (1ULL <<  8)) state->chk1 |= 0x80;
		|
		|			state->chk0 >>= 1;
		|			state->chk0 &= 0x7f;
		|			if (state->val & (1ULL << 16)) state->chk0 |= 0x80;
		|
		|			state->val >>= 1;
		|			state->val &= 0x7f7f7f7f7f7f7f7f;
		|			state->val |= (state->typ & 0x0101010101010101) << 7;
		|
		|			state->typ >>= 1;
		|			state->typ &= 0x7f7f7f7f7f7f7f7f;
		|			BUS_DDG_READ(diag);
		|			if (diag & 0x80) state->typ |= (1ULL << 63);
		|			if (diag & 0x40) state->typ |= (1ULL << 55);
		|			if (diag & 0x20) state->typ |= (1ULL << 47);
		|			if (diag & 0x10) state->typ |= (1ULL << 39);
		|			if (diag & 0x08) state->typ |= (1ULL << 31);
		|			if (diag & 0x04) state->typ |= (1ULL << 23);
		|			if (diag & 0x02) state->typ |= (1ULL << 15);
		|			if (diag & 0x01) state->typ |= (1ULL <<  7);
		|			break;
		|		case 2:
		|			state->typ <<= 1;
		|			state->typ &= 0xfefefefefefefefe;
		|			state->val <<= 1;
		|			state->val &= 0xfefefefefefefefe;
		|			state->chk0 <<= 1;
		|			state->chk0 &= 0xfe;
		|			state->chk1 <<= 1;
		|			state->chk1 &= 0xfe;
		|			state->par <<= 1;
		|			state->par &= 0xfe;
		|			break;
		|		case 3:
		|			BUS_DT_READ(state->typ);
		|			BUS_DV_READ(state->val);
		|			BUS_DC_READ(chk);
		|			state->chk0 = chk >> 5;
		|			state->chk1 = chk & 0x1f;
		|			if (chk & 0x100)	state->chk0 |= 0xf0;
		|			if (chk & 0x100)	state->chk1 |= 0xe0;
		|			state->par = 0xff;
		|			break;
		|		default:
		|			break;
		|		}
		|	}
		|	output.z_qdg = true;
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
		|	output.z_qdg = PIN_QDGOE=>;
		|	if (!output.z_qdg) {
		|		output.qdg = 0;
		|		if (state->val & (1ULL << 56)) output.qdg |= 0x80;
		|		if (state->val & (1ULL << 48)) output.qdg |= 0x40;
		|		if (state->val & (1ULL << 40)) output.qdg |= 0x20;
		|		if (state->val & (1ULL << 32)) output.qdg |= 0x10;
		|		if (state->val & (1ULL << 24)) output.qdg |= 0x08;
		|		if (state->chk0 & (1ULL <<  0)) output.qdg |= 0x04;
		|		if (state->chk1 & (1ULL <<  0)) output.qdg |= 0x02;
		|		if (state->par & (1ULL <<  0)) output.qdg |= 0x01;
		|		output.qdg ^= 0xff;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMDREG", PartModelDQ("XMDREG", XMDREG))
