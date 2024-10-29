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

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<15];	// Turbo 12 bit line, 3 bit set
		|	uint8_t rame[1<<15];	// Turbo 12 bit line, 3 bit set
		|
		|	uint16_t bitc[1 << 21];	// Turbo 12 bit line, 3 bit set, 6 bit word
		|	uint64_t bitt[1 << 22];	// Turbo 12 bit line, 3 bit set, 6 bit word, 1 bit T/V
		|
		|	unsigned cl, wd;
		|	uint16_t cdreg, cqreg;
		|	uint64_t tdreg, tqreg;
		|	uint64_t vdreg, vqreg;
		|
		|	unsigned word;
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
		|	bool cyo, cyt;
		|	unsigned myhits;
		|	unsigned cmd, bcmd;
		|	unsigned mar_set;
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "PIN_H1.pos()"

    def extra(self, file):
        file.include("Infra/cache_line.h")
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
		|#define CMDS(x) ((state->bcmd & (x)) != 0)
		|
		|#define BSET_0	0x01
		|#define BSET_1	0x02
		|#define BSET_2	0x04
		|#define BSET_3	0x08
		|#define BSET_4	0x10
		|#define BSET_5	0x20
		|#define BSET_6	0x40
		|#define BSET_7	0x80
		|''')

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
		|	bool is_hit(unsigned adr, unsigned eadr, unsigned set);
		|	void load_mar(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|unsigned
		|SCM_«mmm» ::
		|find_set(unsigned cmd)
		|{
		|	unsigned set2 = 0;
		|	if (state->hits & (BSET_3|BSET_7)) {
		|		set2 = 3;
		|	} else if (state->hits & (BSET_2|BSET_6)) {
		|		set2 = 2;
		|	} else if (state->hits & (BSET_1|BSET_5)) {
		|		set2 = 1;
		|	} else if (state->hits & (BSET_0|BSET_4)) {
		|		set2 = 0;
		|	} else if (cmd == 0xe && ((state->mar_set & ~4) == 2)) {
		|		set2 = 2;
		|	} else {
		|		set2 = 3;
		|	}
		|	if (state->hits & (BSET_4|BSET_5|BSET_6|BSET_7)) {
		|		set2 |= 4;
		|	}
		|	return (set2);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|is_hit(unsigned adr, unsigned eadr, unsigned set)
		|{
		|	if (state->labort)
		|		return false;
		|
		|	if CMDS(CMD_IDL)
		|		return (true);
		|
		|	unsigned tag = state->rame[eadr];
		|
		|	unsigned page_state = tag & 3;
		|	// R1000_Micro_Arch_Mem.pdf p19:
		|	//    00: Loading, 01: Read-only, 10: Read-Write, 11: Invalid
		|
		|	uint64_t data = state->ram[adr];
		|	uint64_t ta = data >> 19;
		|	uint64_t ts = data & 0x7;
		|
		|	bool name = (state->mar_name == (ta >> 13));
		|	bool offset = (state->mar_page == (ta & 0x1fff)) && (state->mar_space == ts);
		|	if CMDS(CMD_AVQ)
		|		return (page_state == 0);
		|	if CMDS(CMD_LTR)
		|		return (name && offset && page_state != 0);
		|	if CMDS(CMD_LRQ)
		|		return (((tag >> 2) & 0xf) == 0);
		|	if CMDS(CMD_NMQ)
		|		return (name && (page_state != 0));
		|	if CMDS(CMD_LMR)
		|		return (name && offset && (page_state == 1 || page_state == 2));
		|	if CMDS(CMD_LMW)
		|		return (name && offset && page_state == 1);
		|	return (state->mar_set == set);
		|}
		|
		|void
		|SCM_«mmm» ::
		|load_mar(void)
		|{
		|	uint64_t a;
		|	uint32_t s;
		|
		|	BUS_SPC_READ(s);
		|	BUS_ADR_READ(a);
		|	state->mar_space = s;
		|	state->mar_name = (a>>25) & 0xffffffffULL;
		|	state->mar_page = (a>>12) & 0x1fff;
		|	state->mar_set = (a>>BUS_ADR_LSB(27)) & 0xf;
		|
		|	state->word = a & 0x3f;
		|	state->hash = 0;
		|	state->hash ^= cache_line_tbl_h[(a >> 35) & 0x3ff];
		|	state->hash ^= cache_line_tbl_l[(a >> 6) & 0xfff];
		|	state->hash ^= cache_line_tbl_s[state->mar_space & 0x7];
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
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
		|			state->cmd = 0;
		|		} else {
		|			state->cmd = mcmd ^ 0xf;
		|		}
		|		state->p_mcyc2_next =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|		        ((!p_cmdcont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		|		    );
		|		state->cyo =
		|		    !(
		|		        ((mcmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd)
		|		    );
		|		state->cyt = p_mcyc2_next_hd;
		|	}
		|
		|	bool mcyc2 = !state->cyt;
		|
		|	unsigned cmd = state->cmd;
		|	state->bcmd = 1 << cmd;
		|
		|	unsigned adr = 0;
		|
		|	if (q4pos && !PIN_LDWDR=>) {
		|		BUS_DC_READ(state->cdreg);
		|		BUS_DT_READ(state->tdreg);
		|		BUS_DV_READ(state->vdreg);
		|	}
		|
		|	adr = state->hash << 3;
		|	if (CMDS(CMD_PTR|CMD_PTW|CMD_PMR|CMD_PMW)) {
		|		adr |= state->mar_set & 0x7;
		|		//if ((state->mar_set & 3) > 1)
		|		//	adr |= 2;
		|		//if ((state->mar_set & 3) == 1 || (state->mar_set & 3) == 2)
		|		//	adr |= 1;
		|	} else {
		|		adr |= state->a0;
		|	}
		|
		|	if (q1pos) {
		|		state->a0 = 1;
		|	} else if (q2pos) {
		|		state->a0 = 2;
		|	} else if (q3pos) {
		|		state->a0 = 3;
		|	} else if (q4pos) {
		|		state->a0 = 0;
		|	}
		|
		|	unsigned eadr = (adr & ~1) | (state->mar_set & 1);
		|
		|	if (q1pos && mcyc2 && CMDS(CMD_PMR|CMD_LMR|CMD_PTR)) {
		|		uint64_t data = state->ram[adr];
		|		uint8_t pdata = state->rame[eadr];
		|		state->qreg = data & ~(0x7fULL << 6);
		|		state->qreg |= (pdata & 0x7f) << 6;
		|	}
		|
		|	bool ihit = output.hita && output.hitb;
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
		|	if (CMDS(CMD_PTW)) {
		|		bool my_board = !PIN_ISLOW=>;
		|		bool which_board = state->mar_set >> 3;
		|		if (q2pos && mcyc2 && which_board == my_board) {
		|			state->ram[adr] = state->vdreg & ~(0x7fULL << 6);
		|			state->rame[eadr] = (state->vdreg >> 6) & 0x7f;
		|		}
		|	} else if (q2pos && mcyc2 && !state->labort && CMDS(CMD_LRQ|CMD_LMW|CMD_LMR)) {
		|		unsigned a0 = state->hash << 3;
		|		for (unsigned u = 0; u < 8; u++)
		|			state->rame[a0 + u] = dolru(state->hit_lru, state->rame[a0 + u], cmd);
		|	}
		|
		|	if (q4pos && !PIN_LDMR=> && state->cstop) {
		|		load_mar();
		|	}
		|
		|	if (q2pos) {
		|		state->cl = state->hash;
		|		state->wd = state->word;
		|	}
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
		|
		|	if (q4pos && !state->cyo) {
		|		state->hits = 0;
		|		unsigned badr = state->hash << 3;
		|		if (is_hit(badr | 0, badr | 0, 0)) state->hits |= BSET_0;
		|		if (is_hit(badr | 1, badr | 1, 1)) state->hits |= BSET_1;
		|		if (is_hit(badr | 2, badr | 2, 2)) state->hits |= BSET_2;
		|		if (is_hit(badr | 3, badr | 3, 3)) state->hits |= BSET_3;
		|		if (is_hit(badr | 4, badr | 4, 4)) state->hits |= BSET_4;
		|		if (is_hit(badr | 5, badr | 5, 5)) state->hits |= BSET_5;
		|		if (is_hit(badr | 6, badr | 6, 6)) state->hits |= BSET_6;
		|		if (is_hit(badr | 7, badr | 7, 7)) state->hits |= BSET_7;
		|	}
		|	if (q1pos) {
		|		if        (state->hits & BSET_4) { output.seta = 0; output.setb = 0;
		|		} else if (state->hits & BSET_5) { output.seta = 0; output.setb = 1;
		|		} else if (state->hits & BSET_6) { output.seta = 1; output.setb = 0;
		|		} else if (state->hits & BSET_7) { output.seta = 1; output.setb = 1;
		|		} else if (state->hits & BSET_0) { output.seta = 0; output.setb = 0;
		|		} else if (state->hits & BSET_1) { output.seta = 0; output.setb = 1;
		|		} else if (state->hits & BSET_2) { output.seta = 1; output.setb = 0;
		|		} else                           { output.seta = 1; output.setb = 1;
		|		}
		|
		|		output.hita = true;
		|		output.hitb = true;
		|		if (state->hits & (BSET_0|BSET_1|BSET_2|BSET_3))
		|			output.hita = false;
		|		if (state->hits & (BSET_4|BSET_5|BSET_6|BSET_7))
		|			output.hitb = false;
		|		state->myhits = state->hits;
		|		if (state->hits) {
		|			unsigned tadr = state->hash << 3;
		|			     if (state->hits & BSET_0)	state->hit_lru = state->rame[tadr | 0];
		|			else if (state->hits & BSET_1)	state->hit_lru = state->rame[tadr | 1];
		|			else if (state->hits & BSET_2)	state->hit_lru = state->rame[tadr | 2];
		|			else if (state->hits & BSET_3)	state->hit_lru = state->rame[tadr | 3];
		|			else if (state->hits & BSET_4)	state->hit_lru = state->rame[tadr | 4];
		|			else if (state->hits & BSET_5)	state->hit_lru = state->rame[tadr | 5];
		|			else if (state->hits & BSET_6)	state->hit_lru = state->rame[tadr | 6];
		|			else if (state->hits & BSET_7)	state->hit_lru = state->rame[tadr | 7];
		|			state->hit_lru >>= 2;
		|			state->hit_lru &= 0xf;
		|		} else {
		|			state->hit_lru = 0xf;
		|		}
		|	}
		|	if (q4pos) {
		|		state->labort = labort;
		|		state->eabort = !(PIN_EABT=> && PIN_ELABT=>);
		|	}
		|
		|	if (q1pos && mcyc2 && CMDS(CMD_LMR|CMD_PMR) && !labort) {
		|		unsigned set = find_set(cmd);
		|		uint32_t radr =
		|			(set << 18) |
		|			(state->cl << 6) |
		|			state->wd;
		|		assert(radr < (1 << 21));
		|
		|		state->cqreg = state->bitc[radr];
		|		state->tqreg = state->bitt[radr+radr];
		|		state->vqreg = state->bitt[radr+radr+1];
		|	}
		|
		|	bool b_tvdrv = PIN_TVDRV=>;
		|	bool b_vdrv = PIN_VDRV=>;
		|
		|	bool high_board = !PIN_ISLOW=>;
		|	output.qtdr = b_tvdrv || (output.hita && output.hitb && high_board);
		|	output.qvdr = b_vdrv || (output.hita && output.hitb && high_board);
		|
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
