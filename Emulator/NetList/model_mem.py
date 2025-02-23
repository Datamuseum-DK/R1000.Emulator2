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
		|	uint64_t *mem_ram;
		|	uint8_t *mem_rame;
		|	uint64_t *mem_bitt;
		|	unsigned mem_cl, mem_wd;
		|	uint64_t mem_tdreg, mem_tqreg;
		|	uint64_t mem_vdreg, mem_vqreg;
		|
		|	unsigned mem_word;
		|	uint64_t mem_qreg;
		|	unsigned mem_hash;
		|	uint64_t mem_mar_space, mem_mar_name, mem_mar_page;
		|	bool mem_cstop;
		|	unsigned mem_hit_lru;
		|	bool mem_eabort, mem_labort;
		|	bool mem_p_mcyc2_next;
		|	unsigned mem_q4cmd;
		|	unsigned mem_q4cont;
		|	unsigned mem_hits;
		|	bool mem_cyo, mem_cyt;
		|	unsigned mem_cmd, mem_bcmd;
		|	unsigned mem_mar_set;
		|''')

    def init(self, file):
        file.fmt('''
		|	state->mem_bcmd = 1 << state->mem_cmd;
		|	state->mem_bitt = (uint64_t*)CTX_GetRaw("MEM.bitt", sizeof(*state->mem_bitt) << 22);
		|       				// Turbo 12 bit line, 3 bit set, 6 bit word, 1 bit T/V
		|	state->mem_ram = (uint64_t*)CTX_GetRaw("MEM.ram", sizeof(*state->mem_ram) << 15);
		|       				// Turbo 12 bit line, 3 bit set
		|	state->mem_rame = (uint8_t*)CTX_GetRaw("MEM.rame", sizeof(*state->mem_rame) << 15);
		|       				// Turbo 12 bit line, 3 bit set
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
		|#define CMDS(x) ((state->mem_bcmd & (x)) != 0)
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
		|	void mem_h1(void);
		|	void mem_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|unsigned
		|SCM_«mmm» ::
		|find_set(unsigned cmd)
		|{
		|	unsigned set2 = 0;
		|	if (state->mem_hits & (BSET_3|BSET_7)) {
		|		set2 = 3;
		|	} else if (state->mem_hits & (BSET_2|BSET_6)) {
		|		set2 = 2;
		|	} else if (state->mem_hits & (BSET_1|BSET_5)) {
		|		set2 = 1;
		|	} else if (state->mem_hits & (BSET_0|BSET_4)) {
		|		set2 = 0;
		|	} else if (cmd == 0xe && ((state->mem_mar_set & ~4) == 2)) {
		|		set2 = 2;
		|	} else {
		|		set2 = 3;
		|	}
		|	if (state->mem_hits & (BSET_4|BSET_5|BSET_6|BSET_7)) {
		|		set2 |= 4;
		|	}
		|	return (set2);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|is_hit(unsigned adr, unsigned eadr, unsigned set)
		|{
		|	if (state->mem_labort)
		|		return false;
		|
		|	if CMDS(CMD_IDL)
		|		return (true);
		|
		|	unsigned tag = state->mem_rame[eadr];
		|
		|	unsigned page_state = tag & 3;
		|	// R1000_Micro_Arch_Mem.pdf p19:
		|	//    00: Loading, 01: Read-only, 10: Read-Write, 11: Invalid
		|
		|	uint64_t data = state->mem_ram[adr];
		|	uint64_t ta = data >> 19;
		|	uint64_t ts = data & 0x7;
		|
		|	bool name = (state->mem_mar_name == (ta >> 13));
		|	bool offset = (state->mem_mar_page == (ta & 0x1fff)) && (state->mem_mar_space == ts);
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
		|	return (state->mem_mar_set == set);
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
		|	state->mem_mar_space = s;
		|	state->mem_mar_name = (a>>32) & 0xffffffffULL;
		|	state->mem_mar_page = (a>>19) & 0x1fff;
		|	state->mem_mar_set = (a>>BUS64_LSB(27)) & 0xf;
		|
		|	state->mem_word = (a >> 7) & 0x3f;
		|	state->mem_hash = 0;
		|	state->mem_hash ^= cache_line_tbl_h[(a >> 42) & 0x3ff];
		|	state->mem_hash ^= cache_line_tbl_l[(a >> 13) & 0xfff];
		|	state->mem_hash ^= cache_line_tbl_s[state->mem_mar_space & 0x7];
		|}
		|
		|void
		|SCM_«mmm» ::
		|mem_h1(void)
		|{
		|	bool labort = !(mp_mem_abort_l && mp_mem_abort_el);
		|	bool p_early_abort = state->mem_eabort;
		|	bool p_mcyc2_next_hd = state->mem_p_mcyc2_next;
		|	if (p_early_abort && p_mcyc2_next_hd) {
		|		state->mem_cmd = 0;
		|	} else {
		|		state->mem_cmd = state->mem_q4cmd ^ 0xf;
		|	}
		|	state->mem_bcmd = 1 << state->mem_cmd;
		|	state->mem_p_mcyc2_next =
		|	    !(
		|	        ((state->mem_q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
		|	        ((!state->mem_q4cont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		|	    );
		|	state->mem_cyo = !((state->mem_q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd);
		|	state->mem_cyt = p_mcyc2_next_hd;
		|
		|	if (state->mem_cyo) {
		|		if        (state->mem_hits & BSET_4) { mp_mem_set = 0;
		|		} else if (state->mem_hits & BSET_5) { mp_mem_set = 1;
		|		} else if (state->mem_hits & BSET_6) { mp_mem_set = 2;
		|		} else if (state->mem_hits & BSET_7) { mp_mem_set = 3;
		|		} else if (state->mem_hits & BSET_0) { mp_mem_set = 0;
		|		} else if (state->mem_hits & BSET_1) { mp_mem_set = 1;
		|		} else if (state->mem_hits & BSET_2) { mp_mem_set = 2;
		|		} else                           { mp_mem_set = 3;
		|		}
		|
		|		mp_mem_hit = 0xf;
		|		if (state->mem_hits & (BSET_0|BSET_1|BSET_2|BSET_3))
		|			mp_mem_hit &= ~1;
		|		if (state->mem_hits & (BSET_4|BSET_5|BSET_6|BSET_7))
		|			mp_mem_hit &= ~8;
		|		if (state->mem_hits) {
		|			unsigned tadr = state->mem_hash << 3;
		|			     if (state->mem_hits & BSET_0)	state->mem_hit_lru = state->mem_rame[tadr | 0];
		|			else if (state->mem_hits & BSET_1)	state->mem_hit_lru = state->mem_rame[tadr | 1];
		|			else if (state->mem_hits & BSET_2)	state->mem_hit_lru = state->mem_rame[tadr | 2];
		|			else if (state->mem_hits & BSET_3)	state->mem_hit_lru = state->mem_rame[tadr | 3];
		|			else if (state->mem_hits & BSET_4)	state->mem_hit_lru = state->mem_rame[tadr | 4];
		|			else if (state->mem_hits & BSET_5)	state->mem_hit_lru = state->mem_rame[tadr | 5];
		|			else if (state->mem_hits & BSET_6)	state->mem_hit_lru = state->mem_rame[tadr | 6];
		|			else if (state->mem_hits & BSET_7)	state->mem_hit_lru = state->mem_rame[tadr | 7];
		|			state->mem_hit_lru >>= 2;
		|			state->mem_hit_lru &= 0xf;
		|		} else {
		|			state->mem_hit_lru = 0xf;
		|		}
		|	}
		|	if (!state->mem_cyt) {
		|		if (CMDS(CMD_PTR)) {
		|			unsigned padr = (state->mem_hash << 3) | (state->mem_mar_set & 0x7);
		|			state->mem_qreg = state->mem_ram[padr] & ~(0x7fULL << 6);
		|			state->mem_qreg |= (state->mem_rame[padr] & 0x7f) << 6;
		|		}
		|	}
		|
		|	if (!state->mem_cyt) {
		|		if (CMDS(CMD_LMR|CMD_PMR) && !labort) {
		|			unsigned set = find_set(state->mem_cmd);
		|			uint32_t radr =	(set << 18) | (state->mem_cl << 6) | state->mem_wd;
		|			assert(radr < (1 << 21));
		|			state->mem_tqreg = state->mem_bitt[radr+radr];
		|			state->mem_vqreg = state->mem_bitt[radr+radr+1];
		|		}
		|	}
		|	
		|	if (!state->mem_cyt) {
		|		bool ihit = mp_mem_hit == 0xf;
		|		if (CMDS(CMD_LMW|CMD_PMW) && !ihit && !state->mem_labort) {
		|			unsigned set = find_set(state->mem_cmd);
		|			uint32_t radr = (set << 18) | (state->mem_cl << 6) | state->mem_wd;
		|			assert(radr < (1 << 21));
		|			state->mem_bitt[radr+radr] = state->mem_tdreg;
		|			state->mem_bitt[radr+radr+1] = state->mem_vdreg;
		|		}
		|
		|		if (CMDS(CMD_PTW)) {
		|			bool my_board = false;
		|			bool which_board = state->mem_mar_set >> 3;
		|			if (which_board == my_board) {
		|				unsigned padr = (state->mem_hash << 3) | (state->mem_mar_set & 0x7);
		|				state->mem_ram[padr] = state->mem_vdreg & ~(0x7fULL << 6);
		|				state->mem_rame[padr] = (state->mem_vdreg >> 6) & 0x7f;
		|			}
		|		} else if (!state->mem_labort && CMDS(CMD_LRQ|CMD_LMW|CMD_LMR)) {
		|			unsigned padr = state->mem_hash << 3;
		|			for (unsigned u = 0; u < 8; u++)
		|				state->mem_rame[padr + u] = dolru(state->mem_hit_lru, state->mem_rame[padr + u], state->mem_cmd);
		|		}
		|	}
		|
		|	bool not_me = mp_mem_hit == 0xf;
		|	
		|	if (!mp_memv_oe && mp_memtv_oe) {
		|		if (not_me) {
		|			mp_val_bus = ~0ULL;
		|		} else {
		|			mp_val_bus = state->mem_qreg;
		|		}
		|	} else if (!mp_memtv_oe) {
		|		if (not_me) {
		|			mp_typ_bus = ~0ULL;
		|			mp_val_bus = ~0ULL;
		|		} else {
		|			mp_typ_bus = state->mem_tqreg;
		|			mp_val_bus = state->mem_vqreg;
		|		}
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|mem_q4(void)
		|{
		|	bool labort = !(mp_mem_abort_l && mp_mem_abort_el);
		|
		|	state->mem_cl = state->mem_hash;
		|	state->mem_wd = state->mem_word;
		|
		|	state->mem_cstop = mp_sync_freeze == 0;
		|
		|	if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
		|		state->mem_tdreg = mp_typ_bus;
		|		state->mem_vdreg = mp_val_bus;
		|	}
		|	bool loadmar = !((mp_mar_cntl >= 4) && mp_clock_stop_7);
		|	if (!loadmar && state->mem_cstop) {
		|		load_mar();
		|	}
		|
		|	if (!state->mem_cyo) {
		|		state->mem_hits = 0;
		|		unsigned badr = state->mem_hash << 3;
		|		if (is_hit(badr | 0, badr | 0, 0)) state->mem_hits |= BSET_0;
		|		if (is_hit(badr | 1, badr | 1, 1)) state->mem_hits |= BSET_1;
		|		if (is_hit(badr | 2, badr | 2, 2)) state->mem_hits |= BSET_2;
		|		if (is_hit(badr | 3, badr | 3, 3)) state->mem_hits |= BSET_3;
		|		if (is_hit(badr | 4, badr | 4, 4)) state->mem_hits |= BSET_4;
		|		if (is_hit(badr | 5, badr | 5, 5)) state->mem_hits |= BSET_5;
		|		if (is_hit(badr | 6, badr | 6, 6)) state->mem_hits |= BSET_6;
		|		if (is_hit(badr | 7, badr | 7, 7)) state->mem_hits |= BSET_7;
		|	}
		|	state->mem_q4cmd = mp_mem_ctl;
		|	state->mem_q4cont = mp_mem_continue;
		|	state->mem_labort = labort;
		|	state->mem_eabort = !(mp_mem_abort_e && mp_mem_abort_el);
		|}
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "PIN_H2.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_H2.negedge()) {
		|		mem_h1();
		|	} else if (PIN_Q4.posedge()) {
		|		mem_q4();
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("MEM", PartModelDQ("MEM", MEM))
