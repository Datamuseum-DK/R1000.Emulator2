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
   MEM32 CACHE
   ===========
'''


from part import PartModelDQ, PartFactory
from pin import Pin
from node import Node

class XCACHE(PartFactory):

    ''' MEM32 CACHE '''

    autopin = True

    def extra(self, file):
        file.include("Infra/vend.h")

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_A_WIDTH];
		|	uint8_t rame[1<<BUS_A_WIDTH];
		|	uint8_t par[1<<BUS_A_WIDTH];
		|	bool utrace_set;
		|	enum microtrace utrace;
		|	unsigned ae, al, be, bl, sr, la, lb;
		|	bool nme;
		|	bool ome;
		|	bool nml;
		|	bool oml;
		|	bool k12, k13;
		|''')

    def sensitive(self):
        yield "PIN_WE.pos()"
        yield "PIN_EWE.pos()"
        yield "PIN_LWE.pos()"
        yield "BUS_A"
        yield "PIN_CLK"
        yield "PIN_OEE"
        yield "PIN_OEL"
        yield "PIN_EQ"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (!state->utrace_set) {
		|		if (strstr(this->name(), ".ACACHE") != NULL)
		|			state->utrace = UT_ATAGMEM;
		|		else if (strstr(this->name(), ".BCACHE") != NULL)
		|			state->utrace = UT_BTAGMEM;
		|		assert (state->utrace > 0);
		|		state->utrace_set = true;
		|	}
		|
		|	unsigned adr = 0;
		|	uint64_t data = 0;
		|
		|	BUS_A_READ(adr);
		|	adr &= ~3;
		|	if (state->k12)
		|		adr |= 2;
		|	if (state->k13)
		|		adr |= 1;
		|
		|	data = state->ram[adr];
		|	output.qt = data >> 6;
		|
		|	uint8_t pdata;
		|	if (PIN_EVEN=>) {
		|		pdata = state->rame[adr & ~1];
		|	} else {
		|		pdata = state->rame[adr | 1];
		|	}
		|
		|	output.droe = !(PIN_DIR=> && PIN_TGOE=> && (PIN_EVEN=> || PIN_LVEN=>));
		|
		|	output.z_qv = output.droe;
		|	if (!output.z_qv) {
		|		output.qv = data & 0xffffffffffff80ff;	// VAL bits
		|		output.qv |= (pdata & 0xfe) << 7;	// VAL49-55
		|	}
		|
		|	output.z_qp = output.droe;
		|	if (!output.z_qp) {
		|		output.qp = state->par[adr] & 0xfd;	// P0-5,7
		|		output.qp |= (pdata & 1) << 1;		// P6
		|	}
		|
		|	bool pos = PIN_CLK.posedge();
		|	bool neg = PIN_CLK.negedge();
		|	uint64_t tag = data, bpar = 0;
		|
		|	bool oee = PIN_OEE=>;
		|	bool oel = PIN_OEL=>;
		|	unsigned tspr;
		|	BUS_TSPR_READ(tspr);
		|	if (pos && tspr) {
		|		if (tspr == 3) {
		|			state->sr = state->la << 8;
		|			state->sr |= state->lb;
		|		} else if (tspr == 2) {
		|			state->sr >>= 1;
		|			state->sr |= PIN_DIAG=> << 15;
		|		} else if (tspr == 1) {
		|			state->sr <<= 1;
		|			state->sr &= 0xf7f7;
		|		}
		|		output.tspo = state->sr & 1;
		|	}
		|
		|	if (pos || neg) {
		|		bpar = odd_parity64(tag);
		|	}
		|	if (pos) {
		|		bool ts6l = odd_parity(state->rame[adr | 1] & 0xfe);
		|		ts6l ^= ((tag >> 15) & 1);
		|		state->al = bpar & 0xfd;
		|		state->al |= ts6l << 1;
		|		state->bl = state->par[adr] & 0xfd;
		|		state->bl |= (state->rame[adr | 1] & 0x1) << 1;
		|	}
		|	if (neg) {
		|		bool ts6e = odd_parity(state->rame[adr & ~1] & 0xfe);
		|		ts6e ^= ((tag >> 15) & 1);
		|		state->ae = bpar & 0xfd;
		|		state->ae |= ts6e << 1;
		|		state->be = state->par[adr] & 0xfd;
		|		state->be |= (state->rame[adr & ~1] & 0x1) << 1;
		|	}
		|
		|
		|	if (!oee) {
		|		state->la = state->ae;
		|		state->lb = state->be;
		|	} else if (!oel) {
		|		state->la = state->al;
		|		state->lb = state->bl;
		|	} else if (!PIN_TSMO=> && tspr != 3) {
		|		state->la = (state->sr >> 8) & 0xff;
		|		state->lb = (state->sr >> 0) & 0xff;
		|	} else {
		|		state->la = 0xff;
		|		state->lb = 0xff;
		|	}
		|	output.perr = state->la != state->lb;
		|
		|	uint64_t ta, ts, nm, pg, sp;
		|	bool name, offset;
		|
		|	ta = data;
		|	ts = ta & 0x7;
		|	ta = ta >> 19;
		|	BUS_NM_READ(nm);
		|	BUS_PG_READ(pg);
		|	BUS_SP_READ(sp);
		|
		|	if (PIN_E) {
		|		name = true;
		|		offset = true;
		|	} else {
		|		name = (nm != (ta >> BUS_PG_WIDTH));
		|		offset = (pg != (ta & BUS_PG_MASK)) || (sp != ts);
		|	}
		|	
		|	output.nme = !state->nme && !(PIN_EQ=> && state->ome);
		|	output.nml = !state->nml && !(PIN_EQ=> && state->oml);
		|
		|	if (neg) {
		|		state->nme = name;
		|		state->ome = offset;
		|		next_trigger(5, sc_core::SC_NS);
		|	} else if (pos) {	 
		|		state->nml = name;
		|		state->oml = offset;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|
		|	uint64_t vd;
		|	BUS_DV_READ(vd);
		|	uint8_t pd;
		|	BUS_DP_READ(pd);
		|
		|	if (!PIN_OE=> && PIN_WE.posedge()) {
		|		state->ram[adr] = vd & ~(0xfeULL << 7);	// VAL bits
		|		state->par[adr] = pd;
		|
		|		assert(state->utrace > 0);
		|		uint8_t utrc[18];
		|		memset(utrc, 0, sizeof utrc);
		|		utrc[0] = state->utrace;
		|		utrc[1] = state->par[adr];
		|		vbe32enc(utrc + 2, adr);
		|		vbe64enc(utrc + 6, state->ram[adr]);
		|		microtrace(utrc, sizeof utrc);
		|	}
		|
		|	if (!PIN_OE=> && PIN_EWE.posedge()) {
		|		if (!PIN_DIR=> && PIN_EVEN=> && PIN_TGOE=>) {
		|			data = (pd & 0x02) >> 1;	// P6
		|			data |= (vd >> 7) & 0xfe;	// VAL49-55
		|		} else {
		|			BUS_CWE_READ(data);
		|			data &= 0x3f;
		|			data |= (state->rame[adr & ~1] & 0xc0);
		|		}
		|		state->rame[adr & ~1] = data;
		|	}
		|
		|	if (!PIN_OE=> && PIN_LWE.posedge()) {
		|		if (!PIN_DIR=> && PIN_LVEN=> && PIN_TGOE=>) {
		|			data = (pd & 0x02) >> 1;	// P6
		|			data |= (vd >> 7) & 0xfe;	// VAL49-55
		|		} else {
		|			BUS_CWL_READ(data);
		|			data &= 0x3f;
		|			data |= (state->rame[adr | 1] & 0xc0);
		|		}
		|		state->rame[adr | 1] = data;
		|	}
		|	output.cre = state->rame[adr & ~1];
		|	output.crl = state->rame[adr | 1];
		|
		|	if (pos)
		|		state->k12 = PIN_K12=>;
		|	if (neg)
		|		state->k13 = PIN_K13=>;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCACHE", PartModelDQ("XCACHE", XCACHE))
