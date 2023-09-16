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
        yield "PIN_DMHLD"
        yield "PIN_LABR"
        yield "PIN_LEABR"
        yield "PIN_EABR"
        yield "BUS_MCTL_SENSITIVE()"
        yield "PIN_Q4.pos()"
        yield "PIN_H2.pos()"
        yield "BUS_CNDSL_SENSITIVE()"
        yield "BUS_BDHIT_SENSITIVE()"
        yield "PIN_DGHWE"
        yield "PIN_PGMOD"

    def state(self, file):
        file.fmt('''
		|	unsigned qms;
		|	bool state0, state1, labort, e_abort_dly;
		|	uint8_t promz[512];
		|	uint8_t promo[512];
		|	uint8_t promd[512];
		|	uint8_t promt[512];
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
		|	bool sparerr;
		|	bool log_query;
		|	bool mctl_is_read;
		|	bool logrw;
		|	bool logrw_d;
		|	bool scav_hit;
		|	bool omf20;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->promz, sizeof state->promz,
		|	    "PA025-03");
		|	load_programmable(this->name(),
		|	    state->promo, sizeof state->promo,
		|	    "PA026-02");
		|	load_programmable(this->name(),
		|	    state->promd, sizeof state->promd,
		|	    "PA027-01");
		|	load_programmable(this->name(),
		|	    state->promt, sizeof state->promt,
		|	    "PA028-02");
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool diag_mctl = PIN_DMCTL=>;
		|	unsigned mstart;
		|	BUS_MSTRT_READ(mstart);
		|	if (PIN_DMHLD=>) {
		|		state->qms = mstart ^ 0x1e;
		|	} else {
		|		state->qms = (mstart & 1) | 0x1e;
		|	}
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
		|	output.rmarp = (mar_cntl & 0xe) == 0x4;
		|
		|	unsigned promza = 0;
		|	promza |= state->qms;
		|	promza |= state->state0 << 8;
		|	promza |= state->state1 << 7;
		|	promza |= state->labort << 6;
		|	promza |= state->e_abort_dly << 5;
		|	unsigned prmz = state->promz[promza];
		|
		|	unsigned promoa = 0;
		|	promoa |= state->qms;
		|	if (output.omq & 0x02)	// INIT_MRU_D
		|		promoa |= 0x20;
		|	if (state->phys_last)
		|		promoa |= 0x40;
		|	if (state->write_last)
		|		promoa |= 0x80;
		|	if (state->rtv_next_d)
		|		promoa |= 0x100;
		|	unsigned prmo = state->promo[promoa];
		|	// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3
		|
		|	unsigned board_hit, prmda = 0;
		|	BUS_BDHIT_READ(board_hit);
		|	prmda = 0;
		|	prmda |= board_hit << 5;
		|	prmda |= state->init_mru_d << 4;
		|	prmda |= (output.omq & 0xc);
		|	prmda |= PIN_DGHWE=> << 1;
		|	prmda |= PIN_PGMOD=> << 0;
		|	unsigned prmd = state->promd[prmda];
		|
		|	unsigned prmta = (output.cond & 1) << 4;
		|	prmta |= output.eabd << 3;
		|	prmta |= output.st1 << 2;
		|	prmta |= state->mctl_is_read << 1;
		|	prmta |= (output.oqf >> 3) & 1;
		|	// unsigned prmt = state->promt[prmta];
		|
		|	bool memcyc1 = (prmz >> 1) & 1;
		|	bool memstart = (prmz >> 0) & 1;
		|	bool start_if_incw = (prmo >> 5) & 1;
		|
		|	bool pos = PIN_Q4.posedge();
		|	if (pos) {
		|		state->state0 = (prmz >> 7) & 1;
		|		state->state1 = (prmz >> 6) & 1;
		|		output.st1 = state->state1;
		|		state->labort = !(l_abort && le_abort);
		|		state->e_abort_dly = eabrt;
		|		output.eabd = state->e_abort_dly;
		|		state->pcntl_d = prmo & 0xf;
		|		BUS_IQF_READ(output.oqf);
		|		output.oqf &= 0x0f;
		|		output.oqf ^= 0x3;
		|	}
		|
		|	uint32_t ti = 0;
		|	if (output.rmarp)
		|		BUS_TI_READ(ti);
		|
		|	bool scav_trap_next = state->scav_trap;
		|	if (condsel == 0x69) {		// SCAVENGER_HIT
		|		scav_trap_next = false;
		|	} else if (output.rmarp) {
		|		scav_trap_next = (ti >> (63 - 32)) & 1;
		|	} else if (state->log_query) {
		|		scav_trap_next = state->scav_hit;
		|	}
		|
		|	bool cache_miss_next = state->cache_miss;
		|	if (condsel == 0x6b) {		// CACHE_MISS
		|		cache_miss_next = false;
		|	} else if (output.rmarp) {
		|		cache_miss_next = (ti >> (63 - 35)) & 1;
		|	} else if (state->log_query) {
		|		cache_miss_next = PIN_MISS=>;
		|	}
		|
		|	bool csa_oor_next = state->csa_oor;
		|	if (condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|		csa_oor_next = false;
		|	} else if (output.rmarp) {
		|		csa_oor_next = (ti >> (63 - 33)) & 1;
		|	} else if (state->log_query) {
		|		csa_oor_next = PIN_CSAOOR=>;
		|	}
		|
		|	if (pos && !PIN_SFSTP=> && PIN_DMHLD=>) {
		|		state->scav_trap = scav_trap_next;
		|		state->cache_miss = cache_miss_next;
		|		state->csa_oor = csa_oor_next;
		|		state->rtv_next_d = state->rtv_next;
		|
		|		if (output.rmarp) {
		|			state->mar_modified = (ti >> (63 - 39)) & 1;
		|		} else if (condsel == 0x6d) {
		|			state->mar_modified = 1;
		|		} else if (state->omf20) {
		|			state->mar_modified = PIN_EVENT=>;
		|		} else if (!memstart && PIN_EVENT=>) {
		|			state->mar_modified = PIN_EVENT=>;
		|		}
		|		if (output.rmarp) {
		|			state->incmplt_mcyc = (ti >> (63 - 40)) & 1;
		|		} else if (start_if_incw) {
		|			state->incmplt_mcyc = true;
		|		} else if (memcyc1) {
		|			state->incmplt_mcyc = PIN_EVENT=>;
		|		}
		|		if (output.rmarp) {
		|			state->phys_last = (ti >> (63 - 37)) & 1;
		|			state->write_last = (ti >> (63 - 38)) & 1;
		|		} else if (memcyc1) {
		|			state->phys_last = state->phys_ref;
		|			state->write_last = output.mcntl3;
		|		}
		|
		|		state->log_query = !(state->labort || output.logrwn);
		|		
		|		state->sparerr = PIN_SCAPEV=>;
		|		state->scav_hit = PIN_SCADAT=>;
		|
		|		state->omf20 = (
		|			memcyc1 &&
		|			((output.prmt >> 3) & 1) &&
		|			PIN_SCKE=>
		|		);
		|		
		|		if (memcyc1)
		|			state->mctl_is_read = !(state->lcntl & 1);
		|		else
		|			state->mctl_is_read = !(prmo & 1);
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
		|	if (pos && PIN_SCKE=> && !PIN_Q4DIS=>) {
		|		output.omq = 0;
		|		output.omq |= (prmd & 3) << 2;
		|		output.omq |= ((prmd >> 5) & 1) << 1;
		|		if (output.rmarp)
		|			state->page_xing = (ti >> (63 - 34)) & 1;
		|		else
		|			state->page_xing = PIN_PXNXT=>;
		|		state->init_mru_d = (prmo >> 7) & 1;
		|	}
		|	if (PIN_H2.posedge()) {
		|		state->lcntl = state->mcntl;
		|		state->drive_mru = state->init_mru_d;
		|		// output.tmp = state->drive_mru;
		|		state->rtv_next = (prmo >> 4) & 1; // START_TAG_RD
		|		state->memcnd = (prmz >> 4) & 1;	// CM_CTL0
		|		state->cndtru = (prmz >> 3) & 1;	// CM_CTL1
		|	}
		|
		|	if (memstart) {
		|		state->mcntl = state->lcntl;
		|	} else {
		|		state->mcntl = state->pcntl_d;
		|	}
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
		|
		|	state->phys_ref = !(state->mcntl & 0x6);
		|	output.mcntl3 = state->mcntl & 1;
		|	state->logrw = !(state->phys_ref || ((state->mcntl >> 3) & 1));
		|	output.logrw = state->logrw;
		|	output.logrwn = !(output.logrw && memcyc1);
		|
		|	if (diag_mctl) {
		|		output.memct = 0xf;
		|	} else if (memcyc1) {
		|		output.memct = state->lcntl;
		|	} else {
		|		output.memct = prmo & 0xf;
		|	}
		|
		|	promza = 0;
		|	promza |= state->qms;
		|	promza |= state->state0 << 8;
		|	promza |= state->state1 << 7;
		|	promza |= state->labort << 6;
		|	promza |= state->e_abort_dly << 5;
		|	prmz = state->promz[promza];
		|	output.prmz = prmz;
		|	bool contin = (prmz >> 5) & 1;
		|	output.contin = !(!diag_mctl && contin);
		|	output.wrscav = (prmz >> 2) & 1;
		|	output.sparer = !(state->log_query && state->sparerr);
		|
		|	promoa = 0;
		|	promoa |= state->qms;
		|	if (output.omq & 0x02)	// INIT_MRU_D
		|		promoa |= 0x20;
		|	if (state->phys_last)
		|		promoa |= 0x40;
		|	if (state->write_last)
		|		promoa |= 0x80;
		|	if (state->rtv_next_d)
		|		promoa |= 0x100;
		|	prmo = state->promo[promoa];
		|	output.ackrfs = (prmo >> 6) & 1;
		|	// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3
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
		|	prmda = 0;
		|	prmda |= board_hit << 5;
		|	prmda |= state->init_mru_d << 4;
		|	prmda |= (output.omq & 0xc);
		|	prmda |= PIN_DGHWE=> << 1;
		|	prmda |= PIN_PGMOD=> << 0;
		|	prmd = state->promd[prmda];
		|	output.setq = (prmd >> 3) & 3;
		|
		|	output.pgstq = 0;
		|	if (!state->drive_mru || !(prmd & 0x40))
		|		output.pgstq |= 1;
		|	if (!state->drive_mru || !(prmd & 0x80))
		|		output.pgstq |= 2;
		|	output.rtvnxt = !(!diag_mctl && state->rtv_next);
		|	output.memcnd = !(!diag_mctl && state->memcnd);
		|	output.cndtru = !(!diag_mctl && state->cndtru);
		|	output.nohit = board_hit != 0xf;
		|
		|	prmta = mar_cntl << 5;
		|	prmta |= (output.cond & 1) << 4;
		|	prmta |= output.eabd << 3;
		|	prmta |= output.st1 << 2;
		|	prmta |= state->mctl_is_read << 1;
		|	prmta |= (output.oqf >> 3) & 1;
		|	output.prmt = state->promt[prmta];
		|
		|	output.scvhit = state->scav_hit;
		|	output.mcisrd = state->mctl_is_read;
		|	output.logrwd = state->logrw_d;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMEMMON", PartModel("XMEMMON", XMEMMON))
