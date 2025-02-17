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

class MEM(PartFactory):

    ''' MEM32 CACHE '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<15];	// Turbo 12 bit line, 3 bit set
		|	uint8_t rame[1<<15];	// Turbo 12 bit line, 3 bit set
		|	uint64_t bitt[1 << 22];	// Turbo 12 bit line, 3 bit set, 6 bit word, 1 bit T/V
		|
		|	unsigned cl, wd;
		|	uint64_t tdreg, tqreg;
		|	uint64_t vdreg, vqreg;
		|
		|	unsigned word;
		|	uint64_t qreg;
		|	unsigned hash;
		|	uint64_t mar_space, mar_name, mar_page;
		|	bool cstop;
		|	unsigned hit_lru;
		|	bool eabort, labort;
		|	bool p_mcyc2_next;
		|	unsigned q4cmd;
		|	unsigned q4cont;
		|	unsigned hits;
		|	bool cyo, cyt;
		|	unsigned cmd, bcmd;
		|	unsigned mar_set;
		|''')

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
		|	s = mp_spc_bus;
		|	a = mp_adr_bus;
		|	state->mar_space = s;
		|	state->mar_name = (a>>32) & 0xffffffffULL;
		|	state->mar_page = (a>>19) & 0x1fff;
		|	state->mar_set = (a>>BUS64_LSB(27)) & 0xf;
		|
		|	state->word = (a >> 7) & 0x3f;
		|	state->hash = 0;
		|	state->hash ^= cache_line_tbl_h[(a >> 42) & 0x3ff];
		|	state->hash ^= cache_line_tbl_l[(a >> 13) & 0xfff];
		|	state->hash ^= cache_line_tbl_s[state->mar_space & 0x7];
		|}
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "PIN_H2.neg()"

    def init(self, file):
        file.fmt('''
		|	state->bcmd = 1 << state->cmd;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|
		|	bool q4pos = PIN_Q4.posedge();
		|	bool h1pos = PIN_H2.negedge();
		|
		|	bool labort = !(mp_mem_abort_l && mp_mem_abort_el);
		|
		|							if (h1pos) {
		|								bool p_early_abort = state->eabort;
		|								bool p_mcyc2_next_hd = state->p_mcyc2_next;
		|								if (p_early_abort && p_mcyc2_next_hd) {
		|									state->cmd = 0;
		|								} else {
		|									state->cmd = state->q4cmd ^ 0xf;
		|								}
		|								state->bcmd = 1 << state->cmd;
		|								state->p_mcyc2_next =
		|								    !(
		|								        ((state->q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|								        ((!state->q4cont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		|								    );
		|								state->cyo = !((state->q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd);
		|								state->cyt = p_mcyc2_next_hd;
		|
		|								if (state->cyo) {
		|									if        (state->hits & BSET_4) { mp_mem_set = 0;
		|									} else if (state->hits & BSET_5) { mp_mem_set = 1;
		|									} else if (state->hits & BSET_6) { mp_mem_set = 2;
		|									} else if (state->hits & BSET_7) { mp_mem_set = 3;
		|									} else if (state->hits & BSET_0) { mp_mem_set = 0;
		|									} else if (state->hits & BSET_1) { mp_mem_set = 1;
		|									} else if (state->hits & BSET_2) { mp_mem_set = 2;
		|									} else                           { mp_mem_set = 3;
		|									}
		|
		|									mp_mem_hit = 0xf;
		|									if (state->hits & (BSET_0|BSET_1|BSET_2|BSET_3))
		|										mp_mem_hit &= ~1;
		|									if (state->hits & (BSET_4|BSET_5|BSET_6|BSET_7))
		|										mp_mem_hit &= ~8;
		|									if (state->hits) {
		|										unsigned tadr = state->hash << 3;
		|										     if (state->hits & BSET_0)	state->hit_lru = state->rame[tadr | 0];
		|										else if (state->hits & BSET_1)	state->hit_lru = state->rame[tadr | 1];
		|										else if (state->hits & BSET_2)	state->hit_lru = state->rame[tadr | 2];
		|										else if (state->hits & BSET_3)	state->hit_lru = state->rame[tadr | 3];
		|										else if (state->hits & BSET_4)	state->hit_lru = state->rame[tadr | 4];
		|										else if (state->hits & BSET_5)	state->hit_lru = state->rame[tadr | 5];
		|										else if (state->hits & BSET_6)	state->hit_lru = state->rame[tadr | 6];
		|										else if (state->hits & BSET_7)	state->hit_lru = state->rame[tadr | 7];
		|										state->hit_lru >>= 2;
		|										state->hit_lru &= 0xf;
		|									} else {
		|										state->hit_lru = 0xf;
		|									}
		|								}
		|								if (!state->cyt) {
		|									if (CMDS(CMD_PTR)) {
		|										unsigned padr = (state->hash << 3) | (state->mar_set & 0x7);
		|										state->qreg = state->ram[padr] & ~(0x7fULL << 6);
		|										state->qreg |= (state->rame[padr] & 0x7f) << 6;
		|									}
		|								}
		|
		|								if (!state->cyt) {
		|									if (CMDS(CMD_LMR|CMD_PMR) && !labort) {
		|										unsigned set = find_set(state->cmd);
		|										uint32_t radr =	(set << 18) | (state->cl << 6) | state->wd;
		|										assert(radr < (1 << 21));
		|										state->tqreg = state->bitt[radr+radr];
		|										state->vqreg = state->bitt[radr+radr+1];
		|									}
		|								}
		|	
		|								if (!state->cyt) {
		|									bool ihit = mp_mem_hit == 0xf;
		|									if (CMDS(CMD_LMW|CMD_PMW) && !ihit && !state->labort) {
		|										unsigned set = find_set(state->cmd);
		|										uint32_t radr = (set << 18) | (state->cl << 6) | state->wd;
		|										assert(radr < (1 << 21));
		|										state->bitt[radr+radr] = state->tdreg;
		|										state->bitt[radr+radr+1] = state->vdreg;
		|									}
		|
		|									if (CMDS(CMD_PTW)) {
		|										bool my_board = false;
		|										bool which_board = state->mar_set >> 3;
		|										if (which_board == my_board) {
		|											unsigned padr = (state->hash << 3) | (state->mar_set & 0x7);
		|											state->ram[padr] = state->vdreg & ~(0x7fULL << 6);
		|											state->rame[padr] = (state->vdreg >> 6) & 0x7f;
		|										}
		|									} else if (!state->labort && CMDS(CMD_LRQ|CMD_LMW|CMD_LMR)) {
		|										unsigned padr = state->hash << 3;
		|										for (unsigned u = 0; u < 8; u++)
		|											state->rame[padr + u] = dolru(state->hit_lru, state->rame[padr + u], state->cmd);
		|									}
		|								}
		|
		|								bool not_me = mp_mem_hit == 0xf;
		|							
		|								if (!mp_memv_oe && mp_memtv_oe) {
		|									if (not_me) {
		|										mp_val_bus = ~0ULL;
		|									} else {
		|										mp_val_bus = state->qreg;
		|									}
		|								} else if (!mp_memtv_oe) {
		|									if (not_me) {
		|										mp_typ_bus = ~0ULL;
		|										mp_val_bus = ~0ULL;
		|									} else {
		|										mp_typ_bus = state->tqreg;
		|										mp_val_bus = state->vqreg;
		|									}
		|								}
		|							}
		|
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|
		|																											if (q4pos) {
		|																												state->cl = state->hash;
		|																												state->wd = state->word;
		|
		|																												state->cstop = mp_sync_freeze == 0;
		|
		|																												if (!mp_load_wdr) {
		|																													state->tdreg = mp_typ_bus;
		|																													state->vdreg = mp_val_bus;
		|																												}
		|
		|																												if (!mp_load_mar && state->cstop) {
		|																													load_mar();
		|																												}
		|
		|																												if (!state->cyo) {
		|																													state->hits = 0;
		|																													unsigned badr = state->hash << 3;
		|																													if (is_hit(badr | 0, badr | 0, 0)) state->hits |= BSET_0;
		|																													if (is_hit(badr | 1, badr | 1, 1)) state->hits |= BSET_1;
		|																													if (is_hit(badr | 2, badr | 2, 2)) state->hits |= BSET_2;
		|																													if (is_hit(badr | 3, badr | 3, 3)) state->hits |= BSET_3;
		|																													if (is_hit(badr | 4, badr | 4, 4)) state->hits |= BSET_4;
		|																													if (is_hit(badr | 5, badr | 5, 5)) state->hits |= BSET_5;
		|																													if (is_hit(badr | 6, badr | 6, 6)) state->hits |= BSET_6;
		|																													if (is_hit(badr | 7, badr | 7, 7)) state->hits |= BSET_7;
		|																												}
		|																												state->q4cmd = mp_mem_ctl;
		|																												state->q4cont = mp_mem_continue;
		|																												state->labort = labort;
		|																												state->eabort = !(mp_mem_abort_e && mp_mem_abort_el);
		|																											}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("MEM", PartModelDQ("MEM", MEM))
