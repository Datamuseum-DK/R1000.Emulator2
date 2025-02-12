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
   64x4 rotator
   ============
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

'''

from part import PartModelDQ, PartFactory

class FIU(PartFactory):

    ''' FIU first stage rotator '''

    autopin = True

    def extra(self, file):
        file.include("Infra/cache_line.h")

    def state(self, file):
        file.fmt('''
		|	uint16_t refresh_count;			// Z025
		|       unsigned oreg;
		|       uint64_t mdreg;
		|	uint64_t treg;
		|	uint64_t vreg;
		|	uint64_t refresh_reg;
		|	uint64_t marh;
		|	uint64_t ti_bus, vi_bus;
		|	unsigned lfreg;
		|
		|	uint32_t srn, sro, par, ctopn, ctopo;
		|	unsigned nve, pdreg;
		|	unsigned moff;
		|	bool pdt;
		|
		|	bool state0, state1, labort, e_abort_dly;
		|	uint8_t pa025[512];
		|	uint8_t pa026[512];
		|	uint8_t pa027[512];
		|	uint8_t pa028[512];
		|	uint8_t pa060[512];
		|	uint8_t pcntl_d;
		|	uint8_t lcntl;
		|	uint8_t mcntl;
		|	bool scav_trap;
		|	bool cache_miss;
		|	bool csa_oor;
		|	bool page_xing;
		|	bool init_mru_d;
		|	bool drive_mru;
		|	bool memcnd;
		|	bool cndtru;
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
		|	bool nmatch;
		|	bool in_range;
		|	unsigned setq;
		|	unsigned omq;
		|	unsigned prmt;
		|	bool dumon;
		|	bool memex;
		|	bool logrwn;
		|	bool page_crossing_next;
		|	bool miss;
		|	bool csaht;
		|	bool csa_oor_next;
		|	uint64_t *wcsram;
		|	uint64_t *typwcsram;
		|	uint64_t uir;
		|	uint64_t typuir;
		|
		|#define UIR_OL		((state->uir >> 40) & 0x7f)
		|#define UIR_LFL	((state->uir >> 32) & 0x7f)
		|#define UIR_LFRC	((state->uir >> 30) & 0x3)
		|#define UIR_OP		((state->uir >> 28) & 0x3)
		|#define UIR_SEL	((state->uir >> 26) & 0x3)
		|#define UIR_FSRC	((state->uir >> 25) & 1)
		|#define UIR_ORSR	((state->uir >> 24) & 1)
		|#define UIR_TIVI	((state->uir >> 20) & 0xf)
		|#define UIR_OCLK	((state->uir >> 19) & 1)
		|#define UIR_VCLK	((state->uir >> 18) & 1)
		|#define UIR_TCLK	((state->uir >> 17) & 1)
		|#define UIR_LDMDR	((state->uir >> 16) & 1)
		|#define UIR_MSTRT	((state->uir >> 10) & 0x1f)
		|#define UIR_RDSRC	((state->uir >> 9) & 1)
		|#define UIR_LSRC	((state->uir >> 1) & 1)
		|#define UIR_OSRC	((state->uir >> 0) & 1)
		|''')


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->pa025, sizeof state->pa025, "PA025-03");
		|	load_programmable(this->name(), state->pa026, sizeof state->pa026, "PA026-02");
		|	load_programmable(this->name(), state->pa027, sizeof state->pa027, "PA027-01");
		|	load_programmable(this->name(), state->pa028, sizeof state->pa028, "PA028-02");
		|	load_programmable(this->name(), state->pa060, sizeof state->pa060, "PA060");
		|	state->wcsram = (uint64_t*)CTX_GetRaw("FIU_WCS", sizeof(uint64_t) << 14);
		|	state->typwcsram = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);
		|''')

    def sensitive(self):
        yield "PIN_H1.pos()"
        yield "PIN_Q2"
        yield "PIN_Q4.pos()"

        yield "BUS_DF"

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned pa025, pa026, pa027;
		|	unsigned tivi;
		|	bool csa_oor_next;
		|	bool scav_trap_next;
		|	bool memcyc1;
		|	bool memstart;
		|	bool mp_seq_uev10_page_x;
		|	bool mp_seq_uev0_memex;
		|	unsigned countdown;
		|
		|	void do_tivi(void);
		|	void rotator(bool sclk);
		|	void fiu_conditions(unsigned condsel);
		|	uint64_t frame(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|
		|void
		|SCM_«mmm» ::
		|fiu_conditions(unsigned condsel)
		|{
		|
		|	switch(condsel) {
		|	case 0x60: output.conda = !state->memex; 		break;
		|	case 0x61: output.conda = !state->phys_last; 		break;
		|	case 0x62: output.conda = !state->write_last; 		break;
		|	case 0x63: output.conda = !output.chit; 		break;
		|	case 0x64: output.conda = !((state->oreg >> 6) & 1); 	break;
		|	case 0x65: // Cross word shift
		|		output.conda = (state->oreg + (state->lfreg & 0x3f) + (state->lfreg & 0x80)) <= 255;
		|		break;
		|	case 0x66: output.conda = (state->moff & 0x3f) > 0x30; 	break;
		|	case 0x67: output.conda = !output.rfsh; 		break;
		|	case 0x68: output.condb = !state->csa_oor_next;		break;
		|	case 0x69: output.condb = !false; 			break; // SCAV_HIT
		|	case 0x6a: output.condb = !state->page_xing; 		break;
		|	case 0x6b: output.condb = !state->miss; 		break;
		|	case 0x6c: output.condb = !state->incmplt_mcyc; 	break;
		|	case 0x6d: output.condb = !state->mar_modified; 	break;
		|	case 0x6e: output.condb = !state->incmplt_mcyc; 	break;
		|	case 0x6f: output.condb = (state->moff & 0x3f) != 0; 	break;
		|	};
		|}
		|
		|uint64_t
		|SCM_«mmm» ::
		|frame(void)
		|{
		|	uint64_t u = 0;
		|
		|	uint64_t line = 0;
		|	line ^= cache_line_tbl_h[(state->srn >> 10) & 0x3ff];
		|	line ^= cache_line_tbl_l[(state->moff >> (13 - 7)) & 0xfff];
		|	line ^= cache_line_tbl_s[(state->sro >> 4) & 0x7];
		|
		|	uint64_t st;
		|	BUS_ST_READ(st);
		|
		|	u |= (uint64_t)output.cndtru << BUS64_LSB(9);
		|	u |= (uint64_t)output.memcnd << BUS64_LSB(10);
		|	u |= line << BUS64_LSB(23);
		|	u |= (uint64_t)state->setq << BUS64_LSB(25);
		|	u |= st << BUS64_LSB(27);
		|	u |= (uint64_t)((state->omq >> 2) & 0x3) << BUS64_LSB(29);
		|	u |= 0x3ULL << BUS64_LSB(31);
		|	u |= (uint64_t)(mp_seq_uev10_page_x) << BUS64_LSB(32);
		|	u |= (uint64_t)((state->prmt >> 1) & 1) << BUS64_LSB(33);
		|	u |= (uint64_t)output.rfsh << BUS64_LSB(34);
		|	u |= (uint64_t)(mp_seq_uev0_memex) << BUS64_LSB(35);
		|	u |= ((line >> 0) & 1) << BUS64_LSB(48);
		|	u |= ((line >> 1) & 1) << BUS64_LSB(50);
		|	u |= (uint64_t)state->nmatch << BUS64_LSB(56);
		|	u |= (uint64_t)state->in_range << BUS64_LSB(57);
		|	u |= (uint64_t)state->csa_oor_next << BUS64_LSB(58);
		|	u |= (uint64_t)output.chit << BUS64_LSB(59);
		|	u |= (uint64_t)output.hofs;
		|	return (u);
		|}
		|
		|void
		|SCM_«mmm» ::
		|do_tivi(void)
		|{
		|
		|	tivi = UIR_TIVI;
		|
		|	uint64_t vi;
		|	switch (tivi) {
		|	case 0x00: case 0x04: case 0x08:
		|		vi = state->vreg;
		|		break;
		|	case 0x01: case 0x05: case 0x09:
		|		vi = ~mp_val_bus;
		|		break;
		|	case 0x02: case 0x06: case 0x0a:
		|		BUS_DF_READ(vi);
		|		vi ^= BUS_DF_MASK;
		|		break;
		|	case 0x03: case 0x07: case 0x0b:
		|		vi = frame() ^ BUS_DF_MASK;
		|		break;
		|	default:
		|		vi = (uint64_t)state->srn << 32;
		|		vi |= state->sro & 0xffffff80;
		|		vi |= state->oreg;
		|		vi ^= BUS_DF_MASK;
		|		break;
		|	}
		|	uint64_t ti;
		|	switch (tivi) {
		|	case 0x00: case 0x01: case 0x02: case 0x03:
		|		ti = state->treg;
		|		break;
		|	case 0x04: case 0x05: case 0x06: case 0x07:
		|		BUS_DF_READ(ti);
		|		ti ^= BUS_DF_MASK;
		|		break;
		|	case 0x08: case 0x09: case 0x0a: case 0x0b:
		|		ti = ~mp_typ_bus;
		|		break;
		|	default:
		|		uint64_t tmp;
		|		tmp = (state->sro >> 4) & 0x7;
		|		state->marh &= ~0x07;
		|		state->marh |= tmp;
		|		state->marh &= ~(0x1efULL << 23ULL);
		|		state->marh |= (uint64_t)(!state->incmplt_mcyc) << 23;
		|		state->marh |= (uint64_t)(!state->mar_modified) << 24;
		|		state->marh |= (uint64_t)(!state->write_last) << 25;
		|		state->marh |= (uint64_t)(!state->phys_last) << 26;
		|		state->marh |= (uint64_t)(!state->cache_miss) << 28;
		|		state->marh |= (uint64_t)(!state->page_xing) << 29;
		|		state->marh |= (uint64_t)(!state->csa_oor) << 30;
		|		state->marh |= (uint64_t)(!state->scav_trap) << 31;
		|		ti = ~state->marh;
		|		break;
		|	}
		|	state->ti_bus = ti;
		|	state->vi_bus = vi;
		|}
		|
		|void
		|SCM_«mmm» ::
		|rotator(bool sclk)
		|{
		|	uint64_t rot = 0;
		|	uint64_t vmsk = 0, tmsk = 0;
		|	bool sgnbit = 0;
		|	uint64_t ft, tir, vir;
		|	unsigned s, fs, sgn;
		|	bool zero_length;
		|
		|	unsigned lfl = UIR_LFL;
		|
		|	bool fill_mode = false;
		|	if (UIR_FSRC) {				// UCODE
		|		fill_mode = lfl >> 6;
		|	} else {
		|		fill_mode = (state->lfreg >> 6) & 1;
		|	}
		|
		|	unsigned lenone;
		|	if (UIR_LSRC) {				// UCODE
		|		lenone = lfl & 0x3f;
		|	} else {
		|		lenone = state->lfreg & 0x3f;
		|	}
		|
		|	zero_length = !(fill_mode & (lenone == 0x3f));
		|
		|	unsigned offset;
		|	if (UIR_OSRC) {				// UCODE
		|		offset = UIR_OL;
		|	} else {
		|		offset = state->oreg;
		|	}
		|
		|
		|	unsigned op, sbit, ebit;
		|	op = UIR_OP;				// UCODE
		|	switch (op) {
		|	case 0:
		|		sbit = (lenone ^ 0x3f) | (1<<6);
		|		ebit = 0x7f;
		|		break;
		|	case 1:
		|		sbit = 0;
		|		ebit = (lenone & 0x3f) + (offset & 0x7f);
		|		break;
		|	case 2:
		|		sbit = offset;
		|		ebit = 0x7f;
		|		break;
		|	case 3:
		|		sbit = offset;
		|		ebit = (lenone & 0x3f) + (offset & 0x7f);
		|		break;
		|	}
		|	sbit &= 0x7f;
		|	ebit &= 0x7f;
		|
		|	uint64_t msk6;
		|	if (op != 0) {
		|		msk6 = ~0ULL;
		|		if (((offset + lenone) & 3) != 3) {
		|			msk6 >>= 4;
		|		}
		|	} else {
		|		unsigned sx = (offset + (lenone & 3)) & ~0x3;
		|		if (sx == 0 || sx == 0x80) {
		|			msk6 = 0;
		|		} else if (sx < 0x40) {
		|			msk6 = ~0ULL << (64 - sx);
		|		} else {
		|			msk6 = ~0ULL >> (sx - 64);
		|		}
		|	}
		|
		|	// The actual rotation
		|	if (op == 0) {
		|		s = (lenone ^ 0x3f) + 0xc0 - offset;
		|	} else {
		|		s = lenone + offset + 1;
		|	}		
		|	s &= 0x3f;
		|
		|	fs = s & 3;
		|	if (fs == 0) {
		|		tir = state->ti_bus;
		|		vir = state->vi_bus;
		|	} else {
		|		tir = state->ti_bus >> fs;
		|		tir |= state->vi_bus << (64 - fs);
		|		vir = state->vi_bus >> fs;
		|		vir |= state->ti_bus << (64 - fs);
		|	}
		|
		|	ft = msk6 & vir;
		|	ft |= (~msk6) & tir;
		|
		|	if (fill_mode) {
		|		sgnbit = true;
		|	} else {
		|		sgn = offset & 0x3c;
		|		if ((offset & 3) + (lenone & 3) > 3)
		|			sgn += 4;
		|		sgn |= (lenone & 3) ^ 3;
		|
		|		sgnbit = (ft >> (63 - sgn)) & 1;
		|	}
		|
		|	{
		|		uint64_t yl = 0, yh = 0;
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		rot = yh | yl;
		|	}
		|
		|	if (zero_length) {
		|		if (ebit == sbit) {
		|			if (ebit < 64) {
		|				tmsk = 1ULL << (63 - ebit);
		|				vmsk = 0;
		|			} else {
		|				tmsk = 0;
		|				vmsk = 1ULL << (127 - ebit);
		|			} 
		|		} else {
		|			uint64_t inv = 0;
		|			unsigned sb = sbit, eb = ebit;
		|			if (eb < sb) {
		|				sb = ebit + 1;
		|				eb = sbit - 1;
		|				inv = ~(uint64_t)0;
		|			}
		|			if (sb < 64)
		|				tmsk = (~(uint64_t)0) >> sb;
		|			if (eb < 63)
		|				tmsk ^= (~(uint64_t)0) >> (eb + 1);
		|			if (eb > 63)
		|				vmsk = (~(uint64_t)0) << (127 - eb);
		|			if (sb > 64)
		|				vmsk ^= (~(uint64_t)0) << (128 - sb);
		|			tmsk ^= inv;
		|			vmsk ^= inv;
		|		}
		|	}
		|
		|	unsigned sel = UIR_SEL;
		|
		|	uint64_t tii = 0;
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		if (sgnbit)
		|			tii = BUS_DF_MASK;
		|		break;
		|	case 2:
		|		//BUS_DF_READ(tii);
		|		tii = mp_val_bus;
		|		tii = state->vi_bus;
		|		break;
		|	case 3:
		|		BUS_DF_READ(tii);
		|		tii ^= BUS_DF_MASK;
		|		break;
		|	}
		|
		|	uint64_t rdq;
		|	if (UIR_RDSRC) {				// UCODE
		|		rdq = state->mdreg;
		|	} else {
		|		rdq = rot;
		|	}
		|
		|	uint64_t vout = 0;
		|	vout = (rdq & vmsk);
		|	vout |= (tii & (vmsk ^ BUS_DF_MASK));
		|
		|	output.z_qf = PIN_QFOE=>;			// (UCODE)
		|	if (!output.z_qf && PIN_H1=>) { 
		|		output.qf = vout ^ BUS_QF_MASK;
		|		mp_fiu_bus = output.qf;
		|	}
		|
		|	if (sclk && UIR_LDMDR) {			// (UCODE)
		|		state->mdreg = rot;
		|	}
		|
		|	if (sclk && !UIR_TCLK) {			// Q4~^
		|		state->treg = (rdq & tmsk);
		|		state->treg |= (state->ti_bus & (tmsk ^ BUS_DF_MASK));
		|	}
		|
		|	if (sclk && !UIR_VCLK) {			// Q4~^
		|		state->vreg = vout;
		|	}
		|
		|
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	bool h1pos = PIN_H1.posedge();
		|	bool sclk = q4pos && !PIN_SCLKE=>;
		|
		|	bool carry, name_match;
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|
		|	unsigned condsel;
		|	BUS_CNDSL_READ(condsel);
		|
		|	unsigned mar_cntl;
		|	BUS_MCTL_READ(mar_cntl);
		|	bool rmarp = (mar_cntl & 0xe) == 0x4;
		|
		|	unsigned pa028a = mar_cntl << 5;
		|	pa028a |= state->incmplt_mcyc << 4;
		|	pa028a |= state->e_abort_dly << 3;
		|	pa028a |= state->state1 << 2;
		|	pa028a |= state->mctl_is_read << 1;
		|	pa028a |= state->dumon;
		|	state->prmt = state->pa028[pa028a];
		|	state->prmt ^= 0x02;
		|	state->prmt &= 0x7b;
		|
		|	unsigned mem_start = UIR_MSTRT;
		|	mem_start ^= 0x1e;
		|
		|//	ALWAYS						H1				Q1				Q2				Q4
		|	do_tivi();
		|											if (q1pos) {
		|												if (!PIN_QFOE=>) {
		|													rotator(sclk);
		|												}
		|												unsigned dif;
		|											
		|												if (state->pdt) {
		|													carry = state->ctopo <= state->pdreg;
		|													dif = ~0xfffff + state->pdreg - state->ctopo;
		|												} else {
		|													carry = state->moff <= state->ctopo;
		|													dif = ~0xfffff + state->ctopo - state->moff;
		|												}
		|												dif &= 0xfffff;
		|											
		|												name_match = 
		|													    (state->ctopn != state->srn) ||
		|													    ((state->sro & 0xf8000070 ) != 0x10);
		|											
		|												state->in_range = (!state->pdt && name_match) || (dif & 0xffff0);
		|											
		|												output.hofs = (0xf + state->nve - (dif & 0xf)) & 0xf;
		|											
		|												output.chit = !(carry && !(state->in_range || ((dif & 0xf) >= state->nve)));
		|
		|												unsigned pa025a = 0;
		|												pa025a |= mem_start;
		|												pa025a |= state->state0 << 8;
		|												pa025a |= state->state1 << 7;
		|												pa025a |= state->labort << 6;
		|												pa025a |= state->e_abort_dly << 5;
		|												pa025 = state->pa025[pa025a];
		|												memcyc1 = (pa025 >> 1) & 1;
		|												memstart = (pa025 >> 0) & 1;
		|											
		|												if (memstart) {
		|													state->mcntl = state->lcntl;
		|												} else {
		|													state->mcntl = state->pcntl_d;
		|												}
		|												state->phys_ref = !(state->mcntl & 0x6);
		|												state->logrwn = !(state->logrw && memcyc1);
		|												state->logrw = !(state->phys_ref || ((state->mcntl >> 3) & 1));
		|											
		|												scav_trap_next = state->scav_trap;
		|												if (condsel == 0x69) {		// SCAVENGER_HIT
		|													scav_trap_next = false;
		|												} else if (rmarp) {
		|													scav_trap_next = (state->ti_bus >> BUS64_LSB(32)) & 1;
		|												} else if (state->log_query) {
		|													scav_trap_next = false;
		|												}
		|											
		|											
		|												csa_oor_next = state->csa_oor;
		|												if (condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|													csa_oor_next = false;
		|												} else if (rmarp) {
		|													csa_oor_next = (state->ti_bus >> BUS64_LSB(33)) & 1;
		|												} else if (state->log_query) {
		|													csa_oor_next = state->csa_oor_next;
		|												}
		|
		|												bool pgmod = (state->omq >> 1) & 1;
		|												unsigned board_hit;
		|												BUS_BDHIT_READ(board_hit);
		|												unsigned pa027a = 0;
		|												pa027a |= board_hit << 5;
		|												pa027a |= state->init_mru_d << 4;
		|												pa027a |= (state->omq & 0xc);
		|												pa027a |= 1 << 1;
		|												pa027a |= pgmod << 0;
		|												pa027 = state->pa027[pa027a];
		|												state->setq = (pa027 >> 3) & 3;
		|
		|												bool mnor0b = state->drive_mru || ((pa027 & 3) == 0);
		|												bool mnan2a = !(mnor0b && state->logrw_d);
		|												state->miss = !(
		|													((board_hit != 0xf) && mnan2a) ||
		|													(state->logrw_d && state->csaht)
		|												);
		|											}
		|//	ALWAYS						H1				Q1				Q2				Q4
		|															if (q2pos) {
		|																unsigned pa025a = 0;
		|																pa025a |= mem_start;
		|																pa025a |= state->state0 << 8;
		|																pa025a |= state->state1 << 7;
		|																pa025a |= state->labort << 6;
		|																pa025a |= state->e_abort_dly << 5;
		|																pa025 = state->pa025[pa025a];
		|																memcyc1 = (pa025 >> 1) & 1;
		|																memstart = (pa025 >> 0) & 1;
		|															
		|																if (memstart) {
		|																	state->mcntl = state->lcntl;
		|																} else {
		|																	state->mcntl = state->pcntl_d;
		|																}
		|																state->phys_ref = !(state->mcntl & 0x6);
		|																state->logrwn = !(state->logrw && memcyc1);
		|																state->logrw = !(state->phys_ref || ((state->mcntl >> 3) & 1));
		|															
		|																scav_trap_next = state->scav_trap;
		|																if (condsel == 0x69) {		// SCAVENGER_HIT
		|																	scav_trap_next = false;
		|																} else if (rmarp) {
		|																	scav_trap_next = (state->ti_bus >> BUS64_LSB(32)) & 1;
		|																} else if (state->log_query) {
		|																	scav_trap_next = false;
		|																}
		|															
		|															
		|																csa_oor_next = state->csa_oor;
		|																if (condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|																	csa_oor_next = false;
		|																} else if (rmarp) {
		|																	csa_oor_next = (state->ti_bus >> BUS64_LSB(33)) & 1;
		|																} else if (state->log_query) {
		|																	csa_oor_next = state->csa_oor_next;
		|																}
		|
		|																unsigned pa026a = mem_start;
		|																if (state->omq & 0x02)	// INIT_MRU_D
		|																	pa026a |= 0x20;
		|																if (state->phys_last)
		|																	pa026a |= 0x40;
		|																if (state->write_last)
		|																	pa026a |= 0x80;
		|																pa026 = state->pa026[pa026a];
		|																// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3
		|
		|																if (state->log_query) {
		|																	// PIN_MISS instead of cache_miss_next looks suspicious
		|																	// but confirmed on both /200 and /400 FIU boards.
		|																	// 20230910/phk
		|																	state->memex = !(!state->miss && !csa_oor_next && !scav_trap_next);
		|																} else {
		|																	state->memex = !(!state->cache_miss && !state->csa_oor && !state->scav_trap);
		|																}
		|																output.frdr = (state->prmt >> 1) & 1;
		|																bool sel = !((PIN_UEVSTP=> && memcyc1) || (PIN_SCLKE=> && !memcyc1));
		|																if (sel) {
		|																	output.dnext = !((state->prmt >> 0) & 1);
		|																} else {
		|																	output.dnext = !state->dumon;
		|																}
		|														
		|																output.csawr = !(PIN_LABR=> && PIN_LEABR=> && !(state->logrwn || (state->mcntl & 1)));
		|																if (!PIN_QADROE=>) {
		|																	bool inc_mar = (state->prmt >> 3) & 1;
		|																	unsigned inco = state->moff & 0x1f;
		|																	if (inc_mar && inco != 0x1f)
		|																		inco += 1;
		|															
		|																	mp_adr_bus = (uint64_t)state->srn << 32;
		|																	mp_adr_bus |= state->sro & 0xfffff000;
		|																	mp_adr_bus |= (inco & 0x1f) << 7;
		|																	mp_adr_bus |= state->oreg;
		|																	mp_spc_bus = (state->sro >> 4) & 7;
		|																}
		|
		|																state->lcntl = state->mcntl;
		|																state->drive_mru = state->init_mru_d;
		|																state->memcnd = (pa025 >> 4) & 1;	// CM_CTL0
		|																state->cndtru = (pa025 >> 3) & 1;	// CM_CTL1
		|																output.memcnd = !(state->memcnd);
		|																output.cndtru = !(state->cndtru);
		|														
		|																if (memcyc1) {
		|																	output.memct = state->lcntl;
		|																} else {
		|																	output.memct = pa026 & 0xf;
		|																}
		|																bool inc_mar = (state->prmt >> 3) & 1;
		|																state->page_crossing_next = (
		|																	condsel != 0x6a) && (// sel_pg_xing
		|																	condsel != 0x6e) && (// sel_incyc_px
		|																	(
		|																		(state->page_xing) ||
		|																		(!state->page_xing && inc_mar && (state->moff & 0x1f) == 0x1f)
		|																	)
		|																);
		|																output.contin = !((pa025 >> 5) & 1);
		|																mp_seq_uev10_page_x = !(PIN_MICEN=> && state->page_xing);
		|																if (PIN_MICEN=> && state->page_xing) {
		|																	mp_seq_uev |= UEV_PAGE_X;
		|																} else {
		|																	mp_seq_uev &= ~UEV_PAGE_X;
		|																}
		|																mp_seq_uev0_memex = !(PIN_MICEN=> && state->memex);
		|																if (PIN_MICEN=> && state->memex) {
		|																	mp_seq_uev |= UEV_MEMEX;
		|																} else {
		|																	mp_seq_uev &= ~UEV_MEMEX;
		|																}
		|																output.stop0 = mp_seq_uev10_page_x && mp_seq_uev0_memex;
		|															}
		|//	ALWAYS						H1				Q1				Q2				Q4
		|																			if (q4pos) {
		|																				if (sclk) {
		|																					if (UIR_LDMDR || !UIR_TCLK || !UIR_VCLK) {
		|																						rotator(sclk);
		|																					}
		|																			
		|																					if (!UIR_OCLK) {			// Q4~^
		|																						if (UIR_ORSR) {			// UCODE
		|																							state->oreg = UIR_OL;
		|																						} else {
		|																							state->oreg = mp_adr_bus;
		|																							state->oreg &= 0x7f;
		|																						}
		|																					}
		|
		|																					//if (!(state->prmt & 0x40)) {
		|																					if (mar_cntl == 5) {
		|																						state->refresh_reg = state->ti_bus;
		|																						state->marh &= 0xffffffffULL;
		|																						state->marh |= (state->refresh_reg & 0xffffffff00000000ULL);
		|																						state->marh ^= 0xffffffff00000000ULL;
		|																					}
		|																			
		|																					unsigned lfrc;
		|																					lfrc = UIR_LFRC;
		|																			
		|																					switch(lfrc) {
		|																					case 0:
		|																						state->lfreg = (((state->vi_bus >> BUS64_LSB(31)) & 0x3f) + 1) & 0x3f;
		|																						if ((state->ti_bus >> BUS64_LSB(36)) & 1)
		|																							state->lfreg |= (1 << 6);
		|																						else if (!((state->vi_bus >> BUS64_LSB(25)) & 1))
		|																							state->lfreg |= (1 << 6);
		|																						state->lfreg ^= 0x7f;
		|																						break;
		|																					case 1:
		|																						state->lfreg = UIR_LFL;
		|																						break;
		|																					case 2:
		|																						state->lfreg = (state->ti_bus >> BUS64_LSB(48)) & 0x3f;
		|																						if ((state->ti_bus >> BUS64_LSB(36)) & 1)
		|																							state->lfreg |= (1 << 6);
		|																						state->lfreg = state->lfreg ^ 0x7f;
		|																						break;
		|																					case 3:	// No load
		|																						break;
		|																					}
		|																			
		|																					state->marh &= ~(0x3fULL << 15);
		|																					state->marh |= (state->lfreg & 0x3f) << 15;
		|																					state->marh &= ~(1ULL << 27);
		|																					state->marh |= ((state->lfreg >> 6) & 1) << 27;
		|																					if (state->lfreg != 0x7f)
		|																						state->lfreg |= 1<<7;
		|																			
		|{
		|																					unsigned csacntl0 = (state->typwcsram[mp_nua_bus] >> 1) & 7;
		|																					unsigned csacntl1 = (state->typuir >> 1) & 6;
		|																					state->pdt = (csacntl0 == 7) && (csacntl1 == 0);
		|}
		|																					state->nve = mp_csa_nve;
		|																					if (!(csa >> 2)) {
		|																						state->pdreg = state->ctopo;
		|																					}
		|																				}
		|
		|																				unsigned dif;
		|																			
		|																				if (state->pdt) {
		|																					carry = state->ctopo <= state->pdreg;
		|																					dif = ~0xfffff + state->pdreg - state->ctopo;
		|																				} else {
		|																					carry = state->moff <= state->ctopo;
		|																					dif = ~0xfffff + state->ctopo - state->moff;
		|																				}
		|																				dif &= 0xfffff;
		|																			
		|																				name_match = 
		|																					    (state->ctopn != state->srn) ||
		|																					    ((state->sro & 0xf8000070 ) != 0x10);
		|																			
		|																				state->in_range = (!state->pdt && name_match) || (dif & 0xffff0);
		|																			
		|																				output.hofs = (0xf + state->nve - (dif & 0xf)) & 0xf;
		|
		|																				uint64_t adr = 0;
		|																				adr = mp_adr_bus;
		|																				bool load_mar = (state->prmt >> 4) & 1;
		|																		
		|																				if (sclk && load_mar) {
		|																					state->srn = adr >> 32;
		|																					state->sro = adr & 0xffffff80;
		|																					state->sro |= mp_spc_bus << 4;
		|																					state->sro |= 0xf;
		|																				}
		|																				state->moff = (state->sro >> 7) & 0xffffff;
		|																		
		|																				state->nmatch =
		|																				    (state->ctopn != state->srn) ||
		|																				    ((state->sro & 0xf8000070 ) != 0x10);
		|																		
		|																				if (sclk && (csa == 0)) {
		|																					state->ctopn = adr >> 32;
		|																					state->nmatch =
		|																					    (state->ctopn != state->srn) ||
		|																					    ((state->sro & 0xf8000070 ) != 0x10);
		|																				}
		|																		
		|																				if (sclk && !(csa >> 2)) {
		|																					if (csa <= 1) {
		|																						state->ctopo = adr >> 7;
		|																					} else if (!(csa & 1)) {
		|																						state->ctopo += 1;
		|																					} else {
		|																						state->ctopo += 0xfffff;
		|																					}
		|																					state->ctopo &= 0xfffff;
		|																		
		|																				}
		|																		
		|																				if (mem_start == 0x06) {
		|																					state->refresh_count = state->ti_bus >> 48;
		|																				} else if (state->refresh_count != 0xffff) {
		|																					state->refresh_count++;
		|																				}
		|																				output.rfsh = state->refresh_count != 0xffff;
		|
		|																				bool le_abort = PIN_LEABR=>;
		|																				bool e_abort = PIN_EABR=>;
		|																				bool eabrt = !(e_abort && le_abort);
		|																				bool l_abort = PIN_LABR=>;
		|																				bool idum;
		|																				bool sel = !((PIN_UEVSTP=> && memcyc1) || (PIN_SCLKE=> && !memcyc1));
		|																				if (sel) {
		|																					idum = (state->prmt >> 5) & 1;
		|																					output.dnext = !((state->prmt >> 0) & 1);
		|																				} else {
		|																					idum = state->dumon;
		|																					output.dnext = !state->dumon;
		|																				}
		|																				state->state0 = (pa025 >> 7) & 1;
		|																				state->state1 = (pa025 >> 6) & 1;
		|																				state->labort = !(l_abort && le_abort);
		|																				state->e_abort_dly = eabrt;
		|																				state->pcntl_d = pa026 & 0xf;
		|																				state->dumon = idum;
		|																				state->csaht = !output.chit;
		|
		|																				if (!PIN_SFSTP=>) {
		|																					bool cache_miss_next = state->cache_miss;
		|																					if (condsel == 0x6b) {		// CACHE_MISS
		|																						cache_miss_next = false;
		|																					} else if (rmarp) {
		|																						cache_miss_next = (state->ti_bus >> BUS64_LSB(35)) & 1;
		|																					} else if (state->log_query) {
		|																						cache_miss_next = state->miss;
		|																					}
		|																					state->scav_trap = scav_trap_next;
		|																					state->cache_miss = cache_miss_next;
		|																					state->csa_oor = csa_oor_next;
		|																											
		|																					if (rmarp) {
		|																						state->mar_modified = (state->ti_bus >> BUS64_LSB(39)) & 1;
		|																					} else if (condsel == 0x6d) {
		|																						state->mar_modified = 1;
		|																					} else if (state->omf20) {
		|																						state->mar_modified = le_abort;
		|																					} else if (!memstart && le_abort) {
		|																						state->mar_modified = le_abort;
		|																					}
		|																					if (rmarp) {
		|																						state->incmplt_mcyc = (state->ti_bus >> BUS64_LSB(40)) & 1;
		|																					} else if (mem_start == 0x12) {
		|																						state->incmplt_mcyc = true;
		|																					} else if (memcyc1) {
		|																						state->incmplt_mcyc = le_abort;
		|																					}
		|																					if (rmarp) {
		|																						state->phys_last = (state->ti_bus >> BUS64_LSB(37)) & 1;
		|																						state->write_last = (state->ti_bus >> BUS64_LSB(38)) & 1;
		|																					} else if (memcyc1) {
		|																						state->phys_last = state->phys_ref;
		|																						state->write_last = (state->mcntl & 1);
		|																					}
		|																											
		|																					state->log_query = !(state->labort || state->logrwn);
		|																													
		|																					state->omf20 = (memcyc1 && ((state->prmt >> 3) & 1) && !PIN_SCLKE=>);
		|																					
		|																					if (memcyc1)
		|																						state->mctl_is_read = !(state->lcntl & 1);
		|																					else
		|																						state->mctl_is_read = !(pa026 & 1);
		|																											
		|																					state->logrw_d = state->logrw;
		|																				}
		|
		|																				if (!PIN_SCLKE=>) {
		|																					state->omq = 0;
		|																					state->omq |= (pa027 & 3) << 2;
		|																					state->omq |= ((pa027 >> 5) & 1) << 1;
		|																					if (rmarp) {
		|																						state->page_xing = (state->ti_bus >> BUS64_LSB(34)) & 1;
		|																					} else {
		|																						state->page_xing = (state->page_crossing_next);
		|																					}
		|																					state->init_mru_d = (pa026 >> 7) & 1;
		|																				}
		|																				state->csa_oor_next = !(carry || name_match);
		|
		|																				if (!PIN_SFSTP=>) {
		|																					state->uir = state->wcsram[mp_nua_bus];
		|																					state->typuir = state->typwcsram[mp_nua_bus];
		|																				}
		|																			}
		|
		|//	ALWAYS						H1				Q1				Q2				Q4
		|																			if (q4pos) {
		|																				if (mp_fiu_freeze && !output.freze) {
		|																					output.freze = 1;
		|																				} else if (!mp_fiu_freeze && output.freze && !output.sync) {
		|																					output.sync = 1;
		|																				} else if (!mp_fiu_freeze && output.freze && output.sync) {
		|																					output.freze = 0;
		|																					countdown = 5;
		|																				} else if (!mp_fiu_freeze && !output.freze && output.sync) {
		|																					if (--countdown == 0)
		|																						output.sync = 0;
		|																				}
		|																			}
		|//	ALWAYS						H1				Q1				Q2				Q4
		|
		|	if ((!PIN_QTOE=> || !PIN_QVOE=>) && !q4pos) {
		|		do_tivi();
		|		if (!PIN_QTOE=>) {
		|			mp_typ_bus = ~state->ti_bus;
		|		}
		|		if (!PIN_QVOE=>) {
		|			mp_val_bus = ~state->vi_bus;
		|		}
		|	}
		|
		|	if (condsel == 0x6b) {
		|		if (q2pos) {
		|			fiu_conditions(condsel);
		|		}
		|	} else if ((h1pos||q1pos||q2pos) && (60 <= condsel && condsel <= 0x6f)) {
		|		fiu_conditions(condsel);
		|#if 0
		|		if (output.conda != state->output.conda || output.condb != state->output.condb) {
		|			ALWAYS_TRACE(<< " FIUCOND " << std::hex << condsel);
		|		}
		|#endif
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("FIU", PartModelDQ("FIU", FIU))
