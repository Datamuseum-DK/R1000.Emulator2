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
		|	uint64_t ram[1<<15];	// Turbo
		|	uint8_t rame[1<<15];	// Turbo
		|
		|	uint16_t bitc[1 << 21];	// Turbo
		|	uint64_t bitt[1 << 22];	// Turbo
		|	unsigned cl, wd;
		|	uint16_t cdreg, cqreg;
		|	uint64_t tdreg, tqreg;
		|	uint64_t vdreg, vqreg;
		|
		|	bool utrace_set;
		|	enum microtrace utrace;
		|	unsigned sr, word;
		|	unsigned a0;
		|	uint64_t qreg;
		|	unsigned hash;
		|	uint64_t mar_space, mar_name, mar_page;
		|	bool cstop;
		|	bool myset;
		|	unsigned hit_lru;
		|	bool eabort, labort;
		|	bool p_mcyc2_next;
		|	unsigned q4cmd;
		|	unsigned q4cont;
		|	unsigned hits;
		|	bool cyt;
		|	unsigned mylru, myhits;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_H1.pos()"

    def extra(self, file):
        file.fmt('''
		|static unsigned
		|dolru(unsigned lru, unsigned before, unsigned cmd)
		|{
		|	unsigned then = (before >> 2) & 0xf;
		|	unsigned now = then;
		|	if (now == lru) {
		|		now = 7;
		|		if (cmd == 0xd)
		|			now |= 0x10;
		|	} else if (now > lru) {
		|		now -= 1;
		|	}
		|	if ((then & 0x8) || (now & 0x8))
		|		std::cerr <<"BADLRU " << std::hex << lru << " " << before << " " << then << " " << now << " " << cmd << "\\n";
		|	return ((before & 0x43) | (now << 2));
		|}
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned find_set(unsigned cmd);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|unsigned
		|SCM_«mmm» ::
		|find_set(unsigned cmd)
		|{
		|	unsigned set2 = 0;
		|	if (state->hits & 0x05) {
		|		set2 = 0;
		|	} else if (state->hits & 0x0a) {
		|		set2 = 1;
		|	} else if (state->hits & 0x50) {
		|		set2 = 2;
		|	} else if (state->hits & 0xa0) {
		|		set2 = 3;
		|	} else if (cmd == 0xe && ((state->output.ps & ~4) == 2)) {
		|		set2 = 1;
		|	} else {
		|		set2 = 0;
		|	}
		|	return (set2);
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|#define CMD_PMW	(1<<0xf)	// PHYSICAL_MEM_WRITE
		|#define CMD_PMR	(1<<0xe)	// PHYSICAL_MEM_READ
		|#define CMD_LMW	(1<<0xd)	// LOGICAL_MEM_WRITE
		|#define CMD_LMR	(1<<0xc)	// LOGICAL_MEM_READ
		|#define CMD_C01	(1<<0xb)	// COPY 0 TO 1
		|#define CMD_MTT	(1<<0xa)	// MEMORY_TO_TAGSTORE
		|#define CMD_C10	(1<<0x9)	// COPY 1 TO 0
		|#define CMD_SFF	(1<<0x8)	// SET HIT FLIP FLOPS
		|#define CMD_PTW	(1<<0x7)	// PHYSICAL TAG WRITE
		|#define CMD_PTR	(1<<0x6)	// PHYSICAL TAG READ
		|#define CMD_INI	(1<<0x5)	// INITIALIZE MRU
		|#define CMD_LTR	(1<<0x4)	// LOGICAL TAG READ
		|#define CMD_NMQ	(1<<0x3)	// NAME QUERY
		|#define CMD_LRQ	(1<<0x2)	// LRU QUERY
		|#define CMD_AVQ	(1<<0x1)	// AVAILABLE QUERY
		|#define CMD_IDL	(1<<0x0)	// IDLE
		|
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	bool pos = PIN_CLK.posedge();
		|	bool neg = PIN_CLK.negedge();
		|	bool h1pos = PIN_H1.posedge();
		|
		|	bool labort = !(PIN_LABT=> && PIN_ELABT=>);
		|
		|	if (h1pos) {
		|		unsigned mcmd = state->q4cmd;
		|		bool p_cmdcont = state->q4cont;
		|		bool p_early_abort = state->eabort;
		|		bool p_mcyc2_next_hd = state->p_mcyc2_next;
		|		if (p_early_abort && p_mcyc2_next_hd) {
		|			output.cmd = 0;
		|		} else {
		|			output.cmd = mcmd ^ 0xf;
		|		}
		|		state->p_mcyc2_next =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|		        ((!p_cmdcont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		|		    );
		|		output.cyo =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd)
		|		    );
		|		state->cyt = p_mcyc2_next_hd;
		|	}
		|
		|	bool mcyc2 = !state->cyt;
		|
		|	unsigned cmd = output.cmd;
		|	unsigned bcmd = 1 << cmd;
		|#define CMDS(x) ((bcmd & (x)) != 0)
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
		|	output.dlru = true;
		|
		|	if (q4pos && !PIN_LDWDR=>) {
		|		BUS_DC_READ(state->cdreg);
		|		BUS_DT_READ(state->tdreg);
		|		BUS_DV_READ(state->vdreg);
		|	}
		|
		|	adr = state->hash << 2;
		|	if (CMDS(CMD_PTR|CMD_PTW|CMD_PMR|CMD_PMW)) {
		|		if ((output.ps & 3) > 1)
		|			adr |= 2;
		|		if ((output.ps & 3) == 1 || (output.ps & 3) == 2)
		|			adr |= 1;
		|	} else {
		|		adr |= state->a0;
		|	}
		|
		|	if (q1pos) {
		|		state->a0 = 1;
		|	} else if (q2pos) {
		|		state->a0 = 3;
		|	} else if (q3pos) {
		|		state->a0 = 2;
		|	} else if (q4pos) {
		|		state->a0 = 0;
		|	}
		|
		|	unsigned eadr = (adr & ~1) | (output.ps & 1);
		|
		|	data = state->ram[adr];
		|
		|	if (q1pos && mcyc2 && CMDS(CMD_PMR|CMD_LMR|CMD_PTR)) {
		|		uint8_t pdata = state->rame[eadr];
		|		state->qreg = data & ~(0x7fULL << 6);
		|		state->qreg |= (pdata & 0x7f) << 6;
		|	}
		|
		|	if (!CMDS(CMD_IDL) && (pos || neg)) {
		|		uint64_t ta = data >> 19;
		|		uint64_t ts = data & 0x7;
		|
		|		bool name = (state->mar_name == (ta >> 13));
		|		bool offset = (state->mar_page == (ta & 0x1fff)) && (state->mar_space == ts);
		|
		|		if (neg) {
		|			output.nme = name && (CMDS(CMD_NMQ) || offset);
		|		}
		|		if (pos) {
		|			output.nml = name && (CMDS(CMD_NMQ) || offset);
		|		}
		|	}
		|
		|	bool ihit = PIN_ISA=> ? output.hita : output.hitb;
		|	if (q2pos && CMDS(CMD_LMW|CMD_PMW) && mcyc2 && !ihit && !state->labort) {
		|		unsigned set = find_set(cmd);
		|		uint32_t radr2 =
		|			(set << 18) |
		|			(state->cl << 6) |
		|			state->wd;
		|
		|		state->bitc[radr2] = state->cdreg;
		|		state->bitt[radr2+radr2] = state->tdreg;
		|		state->bitt[radr2+radr2+1] = state->vdreg;
		|	}
		|
		|	if (q2pos) {
		|		BUS_DL_READ(state->hit_lru);
		|	}
		|	if (CMDS(CMD_PTW)) {
		|		if (q2pos && mcyc2 && state->myset) {
		|			TRACE(
		|			    << " WT " << std::hex
		|			    << adr << " = " << state->vdreg
		|			    << " was " << state->ram[adr]
		|			    << " cmd " << cmd
		|			    << " set " << output.ps
		|			    << " my " << state->myset
		|			);
		|			state->ram[adr] = state->vdreg & ~(0x7fULL << 6);
		|			state->rame[eadr] = (state->vdreg >> 6) & 0x7f;
		|		}
		|	} else if (pos && mcyc2 && !state->labort && CMDS(CMD_LRQ|CMD_LMW|CMD_LMR)) {
		|#if 0
		|if (state->hit_lru != 7)
		|ALWAYS_TRACE(
		|	<< std::hex << " LRU"
		|	<< " hits " << state->myhits
		|	<< " cmd " << cmd
		|	<< " lru " << state->hit_lru
		|	<< " mylru " << state->mylru
		|	<< " lo " << (unsigned)state->rame[adr & ~1]
		|	<< " hi " << (unsigned)state->rame[adr |  1]
		|);
		|#endif
		|		state->rame[adr & ~1] = dolru(state->hit_lru, state->rame[adr & ~1], cmd);
		|		state->rame[adr |  1] = dolru(state->hit_lru, state->rame[adr |  1], cmd);
		|	}
		|
		|	if (cmd) {
		|		unsigned adr2 = state->hash << 2;
		|		if (CMDS(CMD_PTR|CMD_PTW|CMD_PMR|CMD_PMW)) {
		|			if ((output.ps & 3) > 1)
		|				adr2 |= 2;
		|			if ((output.ps & 3) == 1 || (output.ps & 3) == 2)
		|				adr2 |= 1;
		|		} else {
		|			adr2 |= state->a0;
		|		}
		|		output.cre = state->rame[adr2 & ~1] & BUS_CRE_MASK;
		|		output.crl = state->rame[adr2 | 1] & BUS_CRL_MASK;
		|	}
		|
		|	if (q4pos && !PIN_LDMR=> && state->cstop) {
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
		|			state->myset = (
		|				((output.ps & 0xc) == 0x8 &&  high_board) ||
		|				((output.ps & 0xc) == 0x0 && !high_board)
		|			);
		|		} else {
		|			state->myset = (
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
		|			state->hash |= 1<<11;
		|		if (GBIT(a, 40, BUS_ADR_WIDTH) ^ GBIT(a, 13, BUS_ADR_WIDTH))
		|			state->hash |= 1<<10;
		|		if (GBIT(a, 41, BUS_ADR_WIDTH) ^ GBIT(a, 14, BUS_ADR_WIDTH))
		|			state->hash |= 1<<9;
		|		if (GBIT(a, 42, BUS_ADR_WIDTH) ^ GBIT(a, 15, BUS_ADR_WIDTH))
		|			state->hash |= 1<<8;
		|		if (GBIT(a, 39, BUS_ADR_WIDTH) ^ GBIT(a, 16, BUS_ADR_WIDTH))
		|			state->hash |= 1<<7;
		|		if (GBIT(a, 43, BUS_ADR_WIDTH) ^ GBIT(a, 17, BUS_ADR_WIDTH))
		|			state->hash |= 1<<6;
		|		if (GBIT(a, 47, BUS_ADR_WIDTH) ^ GBIT(a, 18, BUS_ADR_WIDTH))
		|			state->hash |= 1<<5;
		|		if (GBIT(a, 46, BUS_ADR_WIDTH) ^ GBIT(a, 19, BUS_ADR_WIDTH))
		|			state->hash |= 1<<4;
		|		if (GBIT(a, 45, BUS_ADR_WIDTH) ^ GBIT(a, 20, BUS_ADR_WIDTH))
		|			state->hash |= 1<<3;
		|		if (GBIT(a, 44, BUS_ADR_WIDTH) ^ GBIT(a, 21, BUS_ADR_WIDTH))
		|			state->hash |= 1<<2;
		|		if (GBIT(a, 50, BUS_ADR_WIDTH) ^ GBIT(s, 0, BUS_SPC_WIDTH))
		|			state->hash |= 1<<1;
		|		if (GBIT(a, 48, BUS_ADR_WIDTH) ^ GBIT(s, 2, BUS_SPC_WIDTH))
		|			state->hash |= 1<<0;
		|	}
		|
		|	if (q2pos) {
		|		state->cl = state->hash;
		|		state->wd = state->word;
		|	}
		|
		|
		|	if (q3pos) {
		|		bool diag_sync = !PIN_BDISYN=>;
		|		bool diag_freeze = !PIN_BDIFRZ=>;
		|		state->cstop = !(diag_sync || diag_freeze);
		|	}
		|
		|	if (q4pos) {
		|		BUS_MCMD_READ(state->q4cmd);
		|		state->q4cont = PIN_CONT=>;
		|	}
		|	if (q4pos) {
		|		state->labort = labort;
		|		state->eabort = !(PIN_EABT=> && PIN_ELABT=>);
		|	}
		|	if (q1pos) {
		|		output.lrup = (!state->labort) && output.lrup;
		|	}
		|	if (q3pos) {
		|		output.lrup =
		|		    (!state->p_mcyc2_next) && state->cyt && CMDS(CMD_LMW|CMD_LMR|CMD_NMQ|CMD_LRQ);
		|	}
		|
		|	if (q3pos) {
		|		state->hits = 0;
		|		state->hits |= !PIN_AEHIT=> << 7;
		|		state->hits |= !PIN_ALHIT=> << 6;
		|		state->hits |= !PIN_BEHIT=> << 5;
		|		state->hits |= !PIN_BLHIT=> << 4;
		|	}
		|	if (q1pos) {
		|		state->hits |= !PIN_AEHIT=> << 3;
		|		state->hits |= !PIN_ALHIT=> << 2;
		|		state->hits |= !PIN_BEHIT=> << 1;
		|		state->hits |= !PIN_BLHIT=> << 0;
		|		if        (state->hits & 0x20) { output.seta = 0; output.setb = 0;
		|		} else if (state->hits & 0x10) { output.seta = 0; output.setb = 1;
		|		} else if (state->hits & 0x02) { output.seta = 1; output.setb = 0;
		|		} else if (state->hits & 0x01) { output.seta = 1; output.setb = 1;
		|		} else if (state->hits & 0x80) { output.seta = 0; output.setb = 0;
		|		} else if (state->hits & 0x40) { output.seta = 0; output.setb = 1;
		|		} else if (state->hits & 0x08) { output.seta = 1; output.setb = 0;
		|		} else                         { output.seta = 1; output.setb = 1;
		|		}
		|
		|		output.hita = true;
		|		output.hitb = true;
		|		if (state->hits & 0xcc)
		|			output.hita = false;
		|		if (state->hits & 0x33)
		|			output.hitb = false;
		|		state->myhits = state->hits;
		|		if (PIN_ISA=> && (state->hits & 0xcc)) {
		|			     if (state->hits & 0x80)	state->mylru = state->rame[(adr & ~3) | 0];
		|			else if (state->hits & 0x40)	state->mylru = state->rame[(adr & ~3) | 1];
		|			else if (state->hits & 0x08)	state->mylru = state->rame[(adr & ~3) | 2];
		|			else if (state->hits & 0x04)	state->mylru = state->rame[(adr & ~3) | 3];
		|			state->mylru >>= 2;
		|			state->mylru &= 0xf;
		|			output.z_ql = false;
		|			output.ql = state->mylru;
		|		} else if ((!PIN_ISA=>) && (state->hits & 0x33)) {
		|			     if (state->hits & 0x20)	state->mylru = state->rame[(adr & ~3) | 0];
		|			else if (state->hits & 0x10)	state->mylru = state->rame[(adr & ~3) | 1];
		|			else if (state->hits & 0x02)	state->mylru = state->rame[(adr & ~3) | 2];
		|			else if (state->hits & 0x01)	state->mylru = state->rame[(adr & ~3) | 3];
		|			state->mylru >>= 2;
		|			state->mylru &= 0xf;
		|			output.z_ql = false;
		|			output.ql = state->mylru;
		|		} else {
		|			state->mylru = 0xf;
		|			output.z_ql = true;
		|		}
		|	}
		|	if (q1pos && mcyc2 && CMDS(CMD_LMR|CMD_PMR) && !labort) {
		|		unsigned set = find_set(cmd);
		|		uint32_t radr =
		|			(set << 18) |
		|			(state->cl << 6) |
		|			state->wd;
		|		assert(radr < (1 << 20));
		|
		|		state->cqreg = state->bitc[radr];
		|		state->tqreg = state->bitt[radr+radr];
		|		state->vqreg = state->bitt[radr+radr+1];
		|	}
		|
		|	bool b_tvdrv = PIN_TVDRV=>;
		|	bool b_vdrv = PIN_VDRV=>;
		|	bool ahit = output.hita;
		|	bool bhit = output.hitb;
		|
		|	if (PIN_ISA=>) {
		|		bool high_board = !PIN_ISLOW=>;
		|		output.qtdr = !bhit || (ahit && high_board) || b_tvdrv;
		|		output.qvdr = !bhit || (ahit && high_board) || b_vdrv;
		|	} else {
		|		output.qtdr = bhit ||          b_tvdrv;
		|		output.qvdr = bhit ||          b_vdrv;
		|	}
		|	if (!output.qtdr)
		|		output.qvdr = false;
		|
		|	output.z_qc = output.qtdr;
		|	output.z_qt = output.qtdr;
		|	output.z_qv = output.qvdr;
		|
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
