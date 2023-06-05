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
   SEQ Writeable Control Store
   ===========================

'''

from part import PartModel, PartFactory

class XSEQWCS(PartFactory):
    ''' SEQ Writeable Control Store '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_UA_WIDTH];
		|	uint64_t srd0, srd1, srd2, srd3, srd5, srd6;
		|	uint64_t wcs;
		|	bool ff0, ff1, ff2;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_PDCK.pos()"
        yield "PIN_WE.pos()"
        yield "PIN_OE"
        yield "PIN_CLR"
        yield "PIN_DSP0"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)
        file.fmt('''
		|#define PERMUTE(MX) \\
		|	MX( 6, state->srd0, 7) \\
		|	MX( 7, state->srd0, 6) \\
		|	MX( 8, state->srd0, 5) \\
		|	MX( 9, state->srd0, 4) \\
		|	MX(10, state->srd0, 3) \\
		|	MX(11, state->srd0, 2) \\
		|	MX(12, state->srd0, 1) \\
		|	MX(13, state->srd0, 0) \\
		|	MX(27, state->srd1, 7) \\
		|	MX(28, state->srd1, 6) \\
		|	MX( 0, state->srd1, 5) \\
		|	MX( 1, state->srd1, 4) \\
		|	MX( 2, state->srd1, 3) \\
		|	MX( 3, state->srd1, 2) \\
		|	MX( 4, state->srd1, 1) \\
		|	MX( 5, state->srd1, 0) \\
		|	MX(15, state->srd2, 7) \\
		|	MX(17, state->srd2, 6) \\
		|	MX(16, state->srd2, 5) \\
		|	MX(22, state->srd2, 4) \\
		|	MX(23, state->srd2, 3) \\
		|	MX(26, state->srd2, 2) \\
		|	MX(25, state->srd2, 1) \\
		|	MX(24, state->srd2, 0) \\
		|	MX(34, state->srd3, 7) \\
		|	MX(33, state->srd3, 6) \\
		|	MX(19, state->srd3, 5) \\
		|	MX(18, state->srd3, 4) \\
		|	MX(31, state->srd3, 3) \\
		|	MX(21, state->srd3, 2) \\
		|	MX(20, state->srd3, 1) \\
		|	MX(32, state->srd3, 0) \\
		|	MX(38, state->srd5, 7) \\
		|	MX(37, state->srd5, 6) \\
		|	MX(40, state->srd5, 5) \\
		|	MX(39, state->srd5, 4) \\
		|	MX(41, state->srd5, 3) \\
		|	MX(14, state->srd5, 2) \\
		|	MX(30, state->srd5, 1) \\
		|	MX(29, state->srd5, 0) \\
		|	MX(35, state->srd6, 0) \\
		|	MX(36, state->srd6, 1) \\
		|
		|#define WCS2SR(wcsbit, srnam, srbit) srnam |= ((state->wcs >> (41 - wcsbit)) & 1) << (7 - srbit);
		|#define SR2WCS(wcsbit, srnam, srbit) state->wcs |= ((srnam >> (7 - srbit)) & 1) << (41 - wcsbit);
		|	unsigned um, din, tmp, ua;
		|	uint64_t par;
		|
		|	if (!PIN_CLR=>) {
		|		state->srd2 = 0;
		|		state->wcs = 0;
		|		PERMUTE(SR2WCS)
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		BUS_UM_READ(um);
		|		switch (um) {
		|		case 3: // load
		|			BUS_UA_READ(ua);
		|			state->wcs = state->ram[ua];
		|			state->srd0 = 0;
		|			state->srd1 = 0;
		|			state->srd2 = 0;
		|			state->srd3 = 0;
		|			state->srd5 = 0;
		|			state->srd6 = 0;
		|			PERMUTE(WCS2SR)
		|			assert (!(state->srd6 & 0x3f));
		|			if (!(PIN_HLR=> || PIN_SCE=>))
		|				state->srd6 |= 0x20;
		|			state->srd6 |= (PIN_NLM=>) << 4;
		|			// printf("Load [0x%04x] 0x%016jx %02jx\\n", ua, state->wcs, state->srd6);
		|			break;
		|		case 2: // >>
		|			BUS_DIN_READ(din);
		|			state->srd0 >>= 1;
		|			state->srd1 >>= 1;
		|			state->srd2 >>= 1;
		|			state->srd3 >>= 1;
		|			state->srd5 >>= 1;
		|			state->srd6 >>= 1;
		|			state->srd0 |= ((din >> 7) & 1) << 7;
		|			state->srd1 |= ((din >> 6) & 1) << 7;
		|			state->srd2 |= ((din >> 5) & 1) << 7;
		|			state->srd3 |= ((din >> 4) & 1) << 7;
		|			state->srd5 |= ((din >> 2) & 1) << 7;
		|			state->srd6 |= ((din >> 1) & 1) << 7;
		|			state->wcs = 0;
		|			PERMUTE(SR2WCS)
		|			// printf(">> 0x%016jx {%02jx %02jx %02jx %02jx %02jx %02jx} %02x\\n", state->wcs,
		|			//     state->srd0, state->srd1, state->srd2, state->srd3, state->srd5, state->srd6, din);
		|			break;
		|		case 1: // <<
		|			state->srd0 <<= 1;
		|			state->srd1 <<= 1;
		|			state->srd2 <<= 1;
		|			state->srd3 <<= 1;
		|			state->srd5 <<= 1;
		|			state->srd6 <<= 1;
		|			state->srd0 &= 0xfe;
		|			state->srd1 &= 0xfe;
		|			state->srd2 &= 0xfe;
		|			state->srd3 &= 0xfe;
		|			state->srd5 &= 0xfe;
		|			state->srd6 &= 0xe0;
		|			state->srd0 |= 1;
		|			state->srd1 |= 1;
		|			state->srd2 |= 1;
		|			state->srd5 |= 1;
		|			state->wcs = 0;
		|			PERMUTE(SR2WCS)
		|			// printf("<< 0x%016jx {%02jx %02jx %02jx %02jx %02jx %02jx}\\n", state->wcs,
		|			//     state->srd0, state->srd1, state->srd2, state->srd3, state->srd5, state->srd6);
		|			break;
		|		case 0: // noop
		|			break;
		|		}
		|		BUS_UIR_WRITE(state->wcs);
		|		par = (state->wcs ^ (state->wcs >> 32)) & 0xffffffff;
		|		par = (par ^ (par >> 16)) & 0xffff;
		|		par = (par ^ (par >> 8)) & 0xff;
		|		par = (par ^ (par >> 4)) & 0xf;
		|		par = (par ^ (par >> 2)) & 0x3;
		|		par = (par ^ (par >> 1)) & 0x1;
		|		par ^= PIN_PTST=>;
		|		PIN_PERR<=(par);
		|		PIN_HALT<=((state->srd6 >> 5) & 1);
		|		PIN_LLM<=((state->srd6 >> 4) & 1);
		|		PIN_LLMI<=(!((state->srd6 >> 4) & 1));
		|	}
		|	if (PIN_PDCK.posedge()) {
		|		BUS_UA_READ(ua);
		|		tmp = state->ram[ua];
		|		state->ff0 = !(
		|			(((tmp >> 22) & 3) == 3) ||
		|			(((tmp >> 24) & 3) != 3)
		|		);
		|		PIN_MDSP<=state->ff0;
		|		state->ff1 = ((tmp >> 12) & 0x1);
		|		state->ff2 = ((tmp >> 11) & 0x3) == 0;
		|		PIN_RAS1<=(!state->ff2);
		|		PIN_LEXI<=!(state->ff1 || state->ff2);
		|	}
		|	PIN_RAS0<=(
		|		(state->ff0 && !PIN_DSP0=>) ||
		|		(state->ff1)
		|	);
		|	if (PIN_WE.posedge()) {
		|		BUS_UA_READ(ua);
		|		state->ram[ua] = state->wcs;
		|		// printf("Save [0x%04x] 0x%016jx\\n", ua, state->wcs);
		|	}
		|	if (PIN_OE=>) {
		|		BUS_DOUT_Z();
		|	} else {
		|		tmp = 0;
		|		tmp |= (state->srd0 & 1) << 7;
		|		tmp |= (state->srd1 & 1) << 6;
		|		tmp |= (state->srd2 & 1) << 5;
		|		tmp |= (state->srd3 & 1) << 4;
		|		tmp |= (state->srd5 & 1) << 2;
		|		tmp |= ((state->srd6 & 0x10) != 0) << 1;
		|		BUS_DOUT_WRITE(tmp);
		|	}
		''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQWCS", PartModel("XSEQWCS", XSEQWCS))
