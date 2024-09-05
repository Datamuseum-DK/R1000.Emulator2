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
		|	uint64_t ram[1<<14];	// Turbo
		|	uint8_t rame[1<<14];	// Turbo
		|
		|	uint16_t bitc[1 << 20];	// Turbo
		|	uint64_t bitt[1 << 21];	// Turbo
		|	unsigned set, cl, wd;
		|	uint16_t cdreg, cqreg;
		|	uint64_t tdreg, tqreg;
		|	uint64_t vdreg, vqreg;
		|
		|	bool utrace_set;
		|	enum microtrace utrace;
		|	unsigned sr, word;
		|	bool nme;
		|	bool ome;
		|	bool nml;
		|	bool oml;
		|	bool k12, k13;
		|	uint64_t breg, qreg;
		|	unsigned hash;
		|	uint64_t mar_space, mar_name, mar_page;
		|	bool txoe, txdin;
		|''')

    def sensitive(self):
        #yield "BUS_ADR"	Q4
        yield "PIN_CLK"
        yield "BUS_CMD"
        #yield "PIN_CSTP"	Q4
        #yield "BUS_CWE"	CLK.pos()
        #yield "BUS_CWL"	CLK.neg()
        #yield "PIN_DIR"	CLK.pos()
        #yield "BUS_DV"		WCK.pos()
        #yield "PIN_EVEN"	CLK.pos
        #yield "PIN_EWE"	CLK.pos
        #yield "BUS_K"		CLK.pos(12)+neg(13)
        #yield "PIN_LDMR"	Q4
        #yield "PIN_LVEN"	CLK.pos
        #yield "PIN_LWE"	CLK.pos
        #yield "PIN_OE"		CLK.pos
        #yield "PIN_Q4"		CLK
        yield "PIN_QCK.pos()"
        yield "PIN_QVOE"
        #yield "BUS_SPC"	Q4
        #yield "PIN_TGOE"	CLK.pos
        #yield "PIN_WCK"	CLK
        #yield "PIN_WE"		CLK.pos

        yield "PIN_CAS"
        yield "PIN_QCOE"
        yield "PIN_ICK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4pos = PIN_Q4.posedge();
		|	bool q2pos = PIN_Q2.posedge();
		|
		|	if (!state->utrace_set) {
		|		if (strstr(this->name(), ".ACACHE") != NULL)
		|			state->utrace = UT_ATAGMEM;
		|		else if (strstr(this->name(), ".BCACHE") != NULL)
		|			state->utrace = UT_BTAGMEM;
		|		assert (state->utrace > 0);
		|		state->utrace_set = true;
		|	}
		|	unsigned adr = 0;
		|	uint64_t data = 0;
		|
		|	if (PIN_WCK.posedge()) {
		|		BUS_DV_READ(state->breg);
		|		BUS_DC_READ(state->cdreg);
		|		BUS_DT_READ(state->tdreg);
		|		BUS_DV_READ(state->vdreg);
		|	}
		|
		|	adr = state->hash;
		|	adr &= ~3;
		|	if (state->k12)
		|		adr |= 2;
		|	if (state->k13)
		|		adr |= 1;
		|
		|	data = state->ram[adr];
		|
		|	uint8_t pdata;
		|	if (PIN_EVEN=>) {
		|		pdata = state->rame[adr & ~1];
		|	} else {
		|		pdata = state->rame[adr | 1];
		|	}
		|
		|	if (PIN_QCK.posedge()) {
		|		state->qreg = data & 0xffffffffffff80ff;	// VAL bits
		|		state->qreg |= (pdata & 0xfe) << 7;	// VAL49-55
		|	}
		|
		|	bool pos = PIN_CLK.posedge();
		|	bool neg = PIN_CLK.negedge();
		|
		|	uint64_t ta, ts;
		|	bool name, offset;
		|
		|	ta = data;
		|	ts = ta & 0x7;
		|	ta = ta >> 19;
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|
		|	name = (state->mar_name != (ta >> 13));
		|	offset = (state->mar_page != (ta & 0x1fff)) || (state->mar_space != ts);
		|
		|	output.nme = !state->nme && !((cmd != 3) && state->ome);
		|	output.nml = !state->nml && !((cmd != 3) && state->oml);
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
		|	uint64_t vd = state->breg;
		|	uint8_t pd = 0xff;
		|
		|	if (pos && !PIN_OE=> && PIN_WE) {
		|		state->ram[adr] = vd & ~(0xfeULL << 7);	// VAL bits
		|	}
		|
		|	bool tgoe = state->txoe;
		|	bool dir = state->txdin;
		|	if (pos && !PIN_OE=> && PIN_EWE) {
		|		if (!dir && PIN_EVEN=> && tgoe) {
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
		|	if (pos && !PIN_OE=> && PIN_LWE) {
		|		if (!dir && PIN_LVEN=> && tgoe) {
		|			data = (pd & 0x02) >> 1;	// P6
		|			data |= (vd >> 7) & 0xfe;	// VAL49-55
		|		} else {
		|			BUS_CWL_READ(data);
		|			data &= 0x3f;
		|			data |= (state->rame[adr | 1] & 0xc0);
		|		}
		|		state->rame[adr | 1] = data;
		|	}
		|	output.cre = state->rame[adr & ~1] << 1;
		|	output.crl = state->rame[adr | 1] << 1;
		|	output.cre &= ~3;
		|	output.crl &= ~3;
		|	output.cre |= (data >> 6) & 3;
		|	output.crl |= (data >> 6) & 3;
		|
		|	if (pos)
		|		state->k12 = PIN_K12=>;
		|	if (neg)
		|		state->k13 = PIN_K13=>;
		|
		|	if (q4pos) {
		|		bool mcyc2_next = PIN_MC2N=>;
		|		state->txoe = (cmd == 0x6 || cmd == 0x7) && (!mcyc2_next) && (!output.myset);
		|		state->txdin = !(cmd == 0x7 && (!mcyc2_next));
		|	}
		|
		|	if (q4pos && !PIN_LDMR=> && PIN_CSTP) {
		|		uint64_t a;
		|		uint32_t s;
		|
		|		BUS_SPC_READ(s);
		|		BUS_ADR_READ(a);
		|		state->mar_space = s;
		|		state->mar_name = (a>>25) & 0xffffffffULL;
		|		state->mar_page = (a>>12) & 0x1fff;
		|		output.ps = (a>>BUS_ADR_LSB(27)) & 0xf;
		|		bool high_board = !PIN_ISLOW=>;
		|		if (PIN_ISA=>) {
		|			output.myset = !(
		|				((output.ps & 0xc) == 0x8 &&  high_board) ||
		|				((output.ps & 0xc) == 0x0 && !high_board)
		|			);
		|		} else {
		|			output.myset = !(
		|				((output.ps & 0xc) == 0xc &&  high_board) ||
		|				((output.ps & 0xc) == 0x4 && !high_board)
		|			);
		|		}
		|
		|		state->word = a & 0x3f;
		|		state->hash = 0;
		|#define GBIT(fld,bit,width) ((fld >> (width - (bit + 1))) & 1)
		|		if (GBIT(s, 1, BUS_SPC_WIDTH) ^
		|		    GBIT(a, 12, BUS_ADR_WIDTH) ^
		|		    GBIT(a, 49, BUS_ADR_WIDTH))
		|			state->hash |= 1<<13;
		|		if (GBIT(a, 40, BUS_ADR_WIDTH) ^ GBIT(a, 13, BUS_ADR_WIDTH))
		|			state->hash |= 1<<12;
		|		if (GBIT(a, 41, BUS_ADR_WIDTH) ^ GBIT(a, 14, BUS_ADR_WIDTH))
		|			state->hash |= 1<<11;
		|		if (GBIT(a, 42, BUS_ADR_WIDTH) ^ GBIT(a, 15, BUS_ADR_WIDTH))
		|			state->hash |= 1<<10;
		|		if (GBIT(a, 39, BUS_ADR_WIDTH) ^ GBIT(a, 16, BUS_ADR_WIDTH))
		|			state->hash |= 1<<9;
		|		if (GBIT(a, 43, BUS_ADR_WIDTH) ^ GBIT(a, 17, BUS_ADR_WIDTH))
		|			state->hash |= 1<<8;
		|		if (GBIT(a, 47, BUS_ADR_WIDTH) ^ GBIT(a, 18, BUS_ADR_WIDTH))
		|			state->hash |= 1<<7;
		|		if (GBIT(a, 46, BUS_ADR_WIDTH) ^ GBIT(a, 19, BUS_ADR_WIDTH))
		|			state->hash |= 1<<6;
		|		if (GBIT(a, 45, BUS_ADR_WIDTH) ^ GBIT(a, 20, BUS_ADR_WIDTH))
		|			state->hash |= 1<<5;
		|		if (GBIT(a, 44, BUS_ADR_WIDTH) ^ GBIT(a, 21, BUS_ADR_WIDTH))
		|			state->hash |= 1<<4;
		|		if (GBIT(a, 50, BUS_ADR_WIDTH) ^ GBIT(s, 0, BUS_SPC_WIDTH))
		|			state->hash |= 1<<3;
		|		if (GBIT(a, 48, BUS_ADR_WIDTH) ^ GBIT(s, 2, BUS_SPC_WIDTH))
		|			state->hash |= 1<<2;
		|
		|	}
		|
		|	if (PIN_CAS.negedge()) {
		|		BUS_SET_READ(state->set);
		|	}
		|	if (q2pos) {
		|		state->cl = state->hash >> 2;
		|		state->wd = state->word;
		|	}
		|
		|	uint32_t radr =
		|		(state->set << 18) |
		|		(state->cl << 6) |
		|		state->wd;
		|
		|	assert(radr < (1 << 20));
		|	if (PIN_CAS.negedge()) {
		|		if (PIN_RWE=>) {
		|			state->bitc[radr] = state->cdreg;
		|			state->bitt[radr+radr] = state->tdreg;
		|			state->bitt[radr+radr+1] = state->vdreg;
		|		}
		|	}
		|	if (PIN_ICK.posedge() && !PIN_CAS=>) {
		|		state->cqreg = state->bitc[radr];
		|		state->tqreg = state->bitt[radr+radr];
		|		state->vqreg = state->bitt[radr+radr+1];
		|	}
		|	output.z_qc = PIN_QCOE=>;
		|	output.z_qt = output.z_qc;
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv && output.z_qt) {
		|		output.qv = state->qreg;
		|	}
		|	if (!output.z_qc) {
		|		output.qc = state->cqreg;
		|		output.qt = state->tqreg;
		|		output.qv = state->vqreg;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCACHE", PartModelDQ("XCACHE", XCACHE))
