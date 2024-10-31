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
   FIU MAR &co
   ===========

'''

from part import PartModelDQ, PartFactory
from pin import Pin
from node import Node

class XFMAR(PartFactory):
    ''' FIU MAR &co '''

    autopin = True

    def extra(self, file):
        file.include("Infra/cache_line.h")

    def state(self, file):
        file.fmt('''
		|	uint32_t srn, sro, par, ctopn, ctopo;
		|	unsigned nve, pdreg;
		|	unsigned moff;
		|	bool pdt;
		|''')

    def sensitive(self):
        yield "PIN_CLK2X.pos()"
        yield "BUS_OREG"
        yield "PIN_QVIOE"
        yield "PIN_QSPCOE"
        yield "PIN_QADROE"
        yield "PIN_Q4.pos()"
        yield "PIN_NMAT"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4pos = PIN_Q4.posedge();
		|	bool sclk = q4pos && !PIN_SCLKE=>;
		|
		|	unsigned a, b, dif;
		|	bool co, name_match, in_range;
		|
		|	if (sclk) {
		|		// CSAFFB
		|		state->pdt = !PIN_PRED=>;
		|
		|		// NVEMUX + CSAREG
		|		BUS_CNV_READ(state->nve);
		|	}
		|
		|	a = state->ctopo & 0xfffff;
		|	b = state->moff & 0xfffff;
		|
		|	if (sclk && !PIN_COCLK=>) {
		|		state->pdreg = a;
		|	}
		|
		|	if (state->pdt) {
		|		co = a <= state->pdreg;
		|		dif = ~0xfffff + state->pdreg - a;
		|	} else {
		|		co = b <= a;
		|		dif = ~0xfffff + a - b;
		|	}
		|	dif &= 0xfffff;
		|
		|	name_match = PIN_NMAT=>;
		|
		|	// CNAN0B, CINV0B, CSCPR0
		|	in_range = (!state->pdt && name_match) || (dif & 0xffff0);
		|	output.inrg = in_range;
		|
		|	output.hofs = 0xf + state->nve - (dif & 0xf);
		|
		|	output.chit = !(
		|		co &&
		|		!(
		|			in_range ||
		|			((dif & 0xf) >= state->nve)
		|		)
		|	);
		|
		|	if (q4pos) {
		|		output.oor = !(co || name_match);
		|	}
		|
		|	uint64_t adr;
		|	BUS_DADR_READ(adr);
		|
		|	if (q4pos) {
		|		bool load_mar = PIN_LMAR=>;
		|		bool sclk_en = !PIN_SCLKE=>;
		|
		|		if (load_mar && sclk_en) {
		|			uint64_t tmp;
		|			state->srn = adr >> 32;
		|			state->sro = adr & 0xffffff80;
		|			BUS_DSPC_READ(tmp);
		|			state->sro |= tmp << 4;
		|			state->sro |= 0xf;
		|		}
		|		output.mspc = (state->sro >> 4) & BUS_MSPC_MASK;
		|		state->moff = (state->sro >> 7) & 0xffffff;
		|
		|		output.wez = (state->moff & 0x3f) == 0;
		|		output.ntop = !	((state->moff & 0x3f) > 0x30);
		|
		|		state->par = odd_parity64(state->srn) << 4;
		|		state->par |= offset_parity(state->sro) ^ 0xf;
		|		output.nmatch =
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
		|	}
		|
		|	unsigned mar_offset = state->moff;
		|	bool inc_mar = PIN_INMAR=>;
		|	bool page_xing = PIN_PXING=>;
		|	bool sel_pg_xing = PIN_SELPG=>;
		|	bool sel_incyc_px = PIN_SELIN=>;
		|
		|	unsigned marbot = mar_offset & 0x1f;
		|	unsigned inco = marbot;
		|	if (inc_mar && inco != 0x1f)
		|		inco += 1;
		|	inco |= mar_offset & 0x20;
		|
		|	unsigned oreg;
		|	BUS_OREG_READ(oreg);
		|
		|	output.z_qadr = PIN_QADROE=>;
		|	if (!output.z_qadr) {
		|		output.qadr = (uint64_t)state->srn << 32;
		|		output.qadr |= state->sro & 0xfffff000;
		|		output.qadr |= (inco & 0x1f) << 7;
		|		output.qadr |= oreg;
		|	}
		|
		|	output.pxnx = (
		|		(page_xing && sel_pg_xing && sel_incyc_px) ||
		|		(!page_xing && sel_pg_xing && sel_incyc_px && inc_mar && marbot == 0x1f)
		|	);
		|
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|
		|	if (sclk && (csa == 0)) {
		|		state->ctopn = adr >> 32;
		|		output.nmatch =
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
		|	}
		|
		|	output.z_qvi = PIN_QVIOE=>;
		|	if (!output.z_qvi) {
		|		output.qvi = (uint64_t)state->srn << 32;
		|		output.qvi |= state->sro & 0xffffff80;
		|		output.qvi |= oreg;
		|		output.qvi ^= BUS_QVI_MASK;
		|	}
		|
		|	output.z_qspc = PIN_QSPCOE=>;
		|	if (!output.z_qspc) {
		|		output.qspc = (state->sro >> 4) & 7;
		|	}
		|
		|	if (sclk && !PIN_COCLK=>) {
		|		if (csa <= 1) {
		|			state->ctopo = adr >> 7;
		|		} else if (!(csa & 1)) {
		|			state->ctopo += 1;
		|		} else {
		|			state->ctopo += 0xfffff;
		|		}
		|		state->ctopo &= 0xfffff;
		|
		|	}
		|
		|	output.line = 0;
		|	output.line ^= cache_line_tbl_h[(state->srn >> 10) & 0x3ff];
		|	output.line ^= cache_line_tbl_l[(state->moff >> (13 - 7)) & 0xfff];
		|	output.line ^= cache_line_tbl_s[output.mspc];
		|''')



def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFMAR", PartModelDQ("XFMAR", XFMAR))
