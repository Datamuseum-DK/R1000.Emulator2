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
   FIU Memory Monitor
   ==================

'''

from part import PartModel, PartFactory

class XMEMMON(PartFactory):
    ''' FIU Memory Monitor '''

    autopin = True

    def sensitive(self):
        yield "BUS_MSTRT_SENSITIVE()"
        yield "PIN_LABR"
        yield "PIN_LEABR"
        yield "PIN_EABR"
        yield "BUS_MCTL_SENSITIVE()"
        yield "PIN_Q4.pos()"
        yield "PIN_H2.pos()"
        yield "BUS_CNDSL_SENSITIVE()"
        yield "BUS_BDHIT_SENSITIVE()"
        yield "PIN_PGMOD"

    def state(self, file):
        file.fmt('''
		|	uint64_t mstat[32];
		|	bool state0, state1, labort, e_abort_dly;
		|	uint8_t pa025[512];
		|	uint8_t pa026[512];
		|	uint8_t pa027[512];
		|	uint8_t pa028[512];
		|	uint8_t pcntl_d;
		|	uint8_t lcntl;
		|	uint8_t mcntl;
		|	bool scav_trap;
		|	bool cache_miss;
		|	bool csa_oor;
		|	bool page_xing;
		|	bool init_mru_d;
		|	bool drive_mru;
		|	bool rtv_next;
		|	bool memcnd;
		|	bool cndtru;
		|	bool rtv_next_d;
		|	bool incmplt_mcyc;
		|	bool mar_modified;
		|	bool write_last;
		|	bool phys_ref;
		|	bool phys_last;
		|	bool log_query;
		|	bool mctl_is_read;
		|	bool logrw;
		|	bool logrw_d;
		|	bool omf20;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pa025, sizeof state->pa025, "PA025-03");
		|	load_programmable(this->name(),
		|	    state->pa026, sizeof state->pa026, "PA026-02");
		|	load_programmable(this->name(),
		|	    state->pa027, sizeof state->pa027, "PA027-01");
		|	load_programmable(this->name(),
		|	    state->pa028, sizeof state->pa028, "PA028-02");
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|/*
		| logrw   phys_ref
		| 0       1       0000  PHYSICAL_MEM_WRITE
		| 0       1       0001  PHYSICAL_MEM_READ
		| 1       0       0010  LOGICAL_MEM_WRITE
		| 1       0       0011  LOGICAL_MEM_READ
		| 1       0       0100  COPY 0 TO 1 *
		| 1       0       0101  MEMORY_TO_TAGSTORE *
		| 1       0       0110  COPY 1 to 0 *
		| 1       0       0111  SET HIT FLIP FLOPS *
		| 0       1       1000  PHYSICAL TAG WRITE
		| 0       1       1001  PHYSICAL TAG READ
		| 0       0       1010  INITIALIZE MRU
		| 0       0       1011  LOGICAL TAG READ
		| 0       0       1100  NAME QUERY
		| 0       0       1101  LRU QUERY
		| 0       0       1110  AVAILABLE QUERY
		| 0       0       1111  IDLE
		|*/
		|	bool pos = PIN_Q4.posedge();
		|
		|	unsigned mem_start;
		|	BUS_MSTRT_READ(mem_start);
		|	mem_start ^= 0x1e;
		|	if (pos)
		|		state->mstat[mem_start]++;
		|	output.ackrfs = mem_start != 0x6;
		|
		|	unsigned condsel;
		|	BUS_CNDSL_READ(condsel);
		|
		|	bool l_abort = PIN_LABR=>;
		|	bool le_abort = PIN_LEABR=>;
		|	bool e_abort = PIN_EABR=>;
		|	bool eabrt = !(e_abort && le_abort);
		|
		|	unsigned mar_cntl;
		|	BUS_MCTL_READ(mar_cntl);
		|	bool rmarp = (mar_cntl & 0xe) == 0x4;
		|
		|	unsigned pa025a = 0;
		|	pa025a |= mem_start;
		|	pa025a |= state->state0 << 8;
		|	pa025a |= state->state1 << 7;
		|	pa025a |= state->labort << 6;
		|	pa025a |= state->e_abort_dly << 5;
		|	unsigned pa025 = state->pa025[pa025a];
		|	bool memcyc1 = (pa025 >> 1) & 1;
		|	bool memstart = (pa025 >> 0) & 1;
		|
		|	unsigned pa026a = 0;
		|	pa026a |= mem_start;
		|	if (output.omq & 0x02)	// INIT_MRU_D
		|		pa026a |= 0x20;
		|	if (state->phys_last)
		|		pa026a |= 0x40;
		|	if (state->write_last)
		|		pa026a |= 0x80;
		|	if (state->rtv_next_d)
		|		pa026a |= 0x100;
		|	unsigned pa026 = state->pa026[pa026a];
		|	// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3
		|	bool start_if_incw = (pa026 >> 5) & 1;
		|
		|	unsigned board_hit, pa027a = 0;
		|	BUS_BDHIT_READ(board_hit);
		|	pa027a = 0;
		|	pa027a |= board_hit << 5;
		|	pa027a |= state->init_mru_d << 4;
		|	pa027a |= (output.omq & 0xc);
		|	pa027a |= 1 << 1;
		|	pa027a |= PIN_PGMOD=> << 0;
		|	unsigned pa027 = state->pa027[pa027a];
		|
		|
		|	bool sel = !(
		|		(PIN_UEVSTP=> && memcyc1) ||
		|		(PIN_SCLKE=> && !memcyc1)
		|	);
		|	if (pos) {
		|		bool idum;
		|		if (sel) {
		|			idum = (state->output.prmt >> 5) & 1;
		|			output.dnext = !((state->output.prmt >> 0) & 1);
		|		} else {
		|			idum = state->output.dumon;
		|			output.dnext = !state->output.dumon;
		|		}
		|		state->state0 = (pa025 >> 7) & 1;
		|		state->state1 = (pa025 >> 6) & 1;
		|		state->labort = !(l_abort && le_abort);
		|		state->e_abort_dly = eabrt;
		|		state->pcntl_d = pa026 & 0xf;
		|		output.dumon = idum;
		|		output.csaht = !PIN_ICSA=>;
		|	}
		|
		|	uint32_t ti = 0;
		|	if (rmarp)
		|		BUS_TI_READ(ti);
		|
		|	bool scav_trap_next = state->scav_trap;
		|	if (condsel == 0x69) {		// SCAVENGER_HIT
		|		scav_trap_next = false;
		|	} else if (rmarp) {
		|		scav_trap_next = (ti >> (63 - 32)) & 1;
		|	} else if (state->log_query) {
		|		scav_trap_next = false;
		|	}
		|
		|	bool cache_miss_next = state->cache_miss;
		|	if (condsel == 0x6b) {		// CACHE_MISS
		|		cache_miss_next = false;
		|	} else if (rmarp) {
		|		cache_miss_next = (ti >> (63 - 35)) & 1;
		|	} else if (state->log_query) {
		|		cache_miss_next = PIN_MISS=>;
		|	}
		|
		|	bool csa_oor_next = state->csa_oor;
		|	if (condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|		csa_oor_next = false;
		|	} else if (rmarp) {
		|		csa_oor_next = (ti >> (63 - 33)) & 1;
		|	} else if (state->log_query) {
		|		csa_oor_next = PIN_CSAOOR=>;
		|	}
		|
		|	if (pos && !PIN_SFSTP=>) {
		|		state->scav_trap = scav_trap_next;
		|		state->cache_miss = cache_miss_next;
		|		state->csa_oor = csa_oor_next;
		|		state->rtv_next_d = state->rtv_next;
		|
		|		if (rmarp) {
		|			state->mar_modified = (ti >> (63 - 39)) & 1;
		|		} else if (condsel == 0x6d) {
		|			state->mar_modified = 1;
		|		} else if (state->omf20) {
		|			state->mar_modified = le_abort;
		|		} else if (!memstart && le_abort) {
		|			state->mar_modified = le_abort;
		|		}
		|		if (rmarp) {
		|			state->incmplt_mcyc = (ti >> (63 - 40)) & 1;
		|		} else if (start_if_incw) {
		|			state->incmplt_mcyc = true;
		|		} else if (memcyc1) {
		|			state->incmplt_mcyc = le_abort;
		|		}
		|		if (rmarp) {
		|			state->phys_last = (ti >> (63 - 37)) & 1;
		|			state->write_last = (ti >> (63 - 38)) & 1;
		|		} else if (memcyc1) {
		|			state->phys_last = state->phys_ref;
		|			state->write_last = output.mcntl3;
		|		}
		|
		|		state->log_query = !(state->labort || output.logrwn);
		|		
		|		state->omf20 = (
		|			memcyc1 &&
		|			((output.prmt >> 3) & 1) &&
		|			!PIN_SCLKE=>
		|		);
		|		
		|		if (memcyc1)
		|			state->mctl_is_read = !(state->lcntl & 1);
		|		else
		|			state->mctl_is_read = !(pa026 & 1);
		|
		|		state->logrw_d = state->logrw;
		|	}
		|
		|	if (state->log_query) {
		|		// PIN_MISS instead of cache_miss_next looks suspicious
		|		// but confirmed on both /200 and /400 FIU boards.
		|		// 20230910/phk
		|		output.memexp = !(
		|			!PIN_MISS=> &&
		|			!csa_oor_next &&
		|			!scav_trap_next
		|		);
		|	} else {
		|		output.memexp = !(
		|			!state->cache_miss &&
		|			!state->csa_oor &&
		|			!state->scav_trap
		|		);
		|	}
		|
		|	if (pos && !PIN_SCLKE=> && !PIN_Q4DIS=>) {
		|		output.omq = 0;
		|		output.omq |= (pa027 & 3) << 2;
		|		output.omq |= ((pa027 >> 5) & 1) << 1;
		|		if (rmarp)
		|			state->page_xing = (ti >> (63 - 34)) & 1;
		|		else
		|			state->page_xing = PIN_PXNXT=>;
		|		state->init_mru_d = (pa026 >> 7) & 1;
		|	}
		|	if (PIN_H2.posedge()) {
		|		state->lcntl = state->mcntl;
		|		state->drive_mru = state->init_mru_d;
		|		// output.tmp = state->drive_mru;
		|		state->rtv_next = (pa026 >> 4) & 1; // START_TAG_RD
		|		state->memcnd = (pa025 >> 4) & 1;	// CM_CTL0
		|		state->cndtru = (pa025 >> 3) & 1;	// CM_CTL1
		|	}
		|
		|	if (memstart) {
		|		state->mcntl = state->lcntl;
		|	} else {
		|		state->mcntl = state->pcntl_d;
		|	}
		|
		|	state->phys_ref = !(state->mcntl & 0x6);
		|	output.mcntl3 = state->mcntl & 1;
		|	output.logrwn = !(state->logrw && memcyc1);
		|	state->logrw = !(state->phys_ref || ((state->mcntl >> 3) & 1));
		|
		|	if (memcyc1) {
		|		output.memct = state->lcntl;
		|	} else {
		|		output.memct = pa026 & 0xf;
		|	}
		|
		|	pa025a = 0;
		|	pa025a |= mem_start;
		|	pa025a |= state->state0 << 8;
		|	pa025a |= state->state1 << 7;
		|	pa025a |= state->labort << 6;
		|	pa025a |= state->e_abort_dly << 5;
		|	pa025 = state->pa025[pa025a];
		|	// output.mcyc1 = (pa025 >> 1) & 1;
		|	bool contin = (pa025 >> 5) & 1;
		|	output.contin = !(contin);
		|
		|	pa026a = 0;
		|	pa026a |= mem_start;
		|	if (output.omq & 0x02)	// INIT_MRU_D
		|		pa026a |= 0x20;
		|	if (state->phys_last)
		|		pa026a |= 0x40;
		|	if (state->write_last)
		|		pa026a |= 0x80;
		|	if (state->rtv_next_d)
		|		pa026a |= 0x100;
		|	pa026 = state->pa026[pa026a];
		|
		|	output.cond6a = condsel != 0x6a;
		|	output.cond6e = condsel != 0x6e;
		|
		|	output.cond = 0;
		|	output.cond |= state->scav_trap << 7;
		|	output.cond |= state->csa_oor << 6;
		|	output.cond |= state->page_xing << 5;
		|	output.cond |= state->cache_miss << 4;
		|	output.cond |= state->phys_last << 3;
		|	output.cond |= state->write_last << 2;
		|	output.cond |= state->mar_modified << 1;
		|	output.cond |= state->incmplt_mcyc << 0;
		|
		|	pa027a = 0;
		|	pa027a |= board_hit << 5;
		|	pa027a |= state->init_mru_d << 4;
		|	pa027a |= (output.omq & 0xc);
		|	pa027a |= 1 << 1;
		|	pa027a |= PIN_PGMOD=> << 0;
		|	pa027 = state->pa027[pa027a];
		|	output.setq = (pa027 >> 3) & 3;
		|
		|	output.pgstq = 0;
		|	if (!state->drive_mru || !(pa027 & 0x40))
		|		output.pgstq |= 1;
		|	if (!state->drive_mru || !(pa027 & 0x80))
		|		output.pgstq |= 2;
		|	output.rtvnxt = !(state->rtv_next);
		|	output.memcnd = !(state->memcnd);
		|	output.cndtru = !(state->cndtru);
		|	output.nohit = board_hit != 0xf;
		|
		|	unsigned pa028a = mar_cntl << 5;
		|	pa028a |= (output.cond & 1) << 4;
		|	pa028a |= state->e_abort_dly << 3;
		|	pa028a |= state->state1 << 2;
		|	pa028a |= state->mctl_is_read << 1;
		|	pa028a |= output.dumon;
		|	output.prmt = state->pa028[pa028a];
		|	output.prmt ^= 0x02;
		|	output.prmt &= 0x7b;
		|
		|	output.scvhit = false;
		|	output.logrwd = state->logrw_d;
		|
		|	if (sel) {
		|		output.dnext = !((state->output.prmt >> 0) & 1);
		|	} else {
		|		output.dnext = !state->output.dumon;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMEMMON", PartModel("XMEMMON", XMEMMON))
