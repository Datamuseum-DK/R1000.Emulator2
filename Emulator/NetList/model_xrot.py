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

'''

from part import PartModelDQ, PartFactory

class XROTF(PartFactory):

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
		|	uint64_t rdq;
		|	uint64_t refresh_reg;
		|	uint64_t marh;
		|	uint64_t tibus, vibus;
		|	unsigned tivi, lfreg;
		|	sc_core::sc_event_or_list *idle_this;
		|
		|	uint32_t srn, sro, par, ctopn, ctopo;
		|	unsigned nve, pdreg;
		|	unsigned moff;
		|	bool pdt;
		|
		|''')

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

    def sensitive(self):
        yield "PIN_H1.pos()"
        yield "PIN_Q4.pos()"

        yield "BUS_DF"
        yield "BUS_DT"
        yield "BUS_DV"
        yield "BUS_MCND"

        yield "PIN_CLK2X.pos()"
        # yield "BUS_IREG"
        # yield "PIN_QVIOE"
        yield "PIN_QSPCOE"
        yield "PIN_QADROE"
        # yield "PIN_Q4.pos()"

        # yield "PIN_FSRC"		# UCODE, H1
        # yield "PIN_FT"		# UCODE, H1
        # yield "PIN_FV"		# UCODE, H1
        # yield "PIN_LCLK.pos()"	# Q4
        # yield "PIN_LDMDR"		# Q4
        # yield "BUS_LFL"		# UCODE, H1
        # yield "BUS_LFRC"		# LCLK
        # yield "PIN_LSRC"		# UCODE, H1
        # yield "PIN_OCLK.pos()"	# Q4
        # yield "BUS_OL"		# UCODE, H1
        # yield "BUS_OP"		# UCODE, H1
        # yield "PIN_ORSR"		# OCLK
        # yield "PIN_OSRC"		# UCODE, H1
        # yield "PIN_RDSRC"		# UCODE, H1
        # yield "PIN_SCLKE"		# Q4
        # yield "BUS_SEL"		# UCODE, H1
        # yield "PIN_TCLK.pos()"	# Q4
        # yield "PIN_VCLK.pos()"	# Q4

        yield "BUS_MSTRT"
        yield "PIN_LABR"
        yield "PIN_LEABR"
        yield "PIN_EABR"
        yield "BUS_MCTL"
        yield "PIN_H2.pos()"
        yield "BUS_CNDSL"
        yield "BUS_BDHIT"

        yield "BUS_TIVI"
        yield "BUS_DFA"

    def priv_decl(self, file):
        file.fmt('''
		|	void do_tivi(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|do_tivi(void)
		|{
		|	unsigned mcnd;
		|	BUS_MCND_READ(mcnd);
		|
		|	BUS_TIVI_READ(state->tivi);
		|
		|	uint64_t vi;
		|	switch (state->tivi) {
		|	case 0x00:
		|	case 0x04:
		|	case 0x08:
		|		vi = state->vreg;
		|		break;
		|	case 0x01:
		|	case 0x05:
		|	case 0x09:
		|		BUS_DV_READ(vi);
		|		vi ^= BUS_DV_MASK;
		|		break;
		|	case 0x02:
		|	case 0x06:
		|	case 0x0a:
		|		BUS_DF_READ(vi);
		|		vi ^= BUS_DF_MASK;
		|		break;
		|	case 0x03:
		|	case 0x07:
		|	case 0x0b:
		|		BUS_DFA_READ(vi);
		|		vi ^= BUS_DFA_MASK;
		|		break;
		|	default:
		|		vi = (uint64_t)state->srn << 32;
		|		vi |= state->sro & 0xffffff80;
		|		vi |= state->oreg;
		|		vi ^= BUS_QV_MASK;
		|		break;
		|	}
		|	uint64_t ti;
		|	switch (state->tivi) {
		|	case 0x00:
		|	case 0x01:
		|	case 0x02:
		|	case 0x03:
		|		ti = state->treg;
		|		break;
		|	case 0x04:
		|	case 0x05:
		|	case 0x06:
		|	case 0x07:
		|		BUS_DF_READ(ti);
		|		ti ^= BUS_DF_MASK;
		|		break;
		|	case 0x08:
		|	case 0x09:
		|	case 0x0a:
		|	case 0x0b:
		|		BUS_DT_READ(ti);
		|		ti ^= BUS_DT_MASK;
		|		break;
		|	default:
		|		uint64_t tmp;
		|		tmp = (state->sro >> 4) & 0x7;
		|		state->marh &= ~0x07;
		|		state->marh |= tmp;
		|		tmp = mcnd ^ BUS_MCND_MASK; 
		|		state->marh &= ~(0x1efULL << 23ULL);
		|		state->marh |= tmp << 23ULL;
		|		ti = ~state->marh;
		|		break;
		|	}
		|	state->tibus = ti;
		|	state->vibus = vi;
		|}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4pos = PIN_Q4.posedge();
		|	bool sclk = q4pos && !PIN_SCLKE=>;
		|
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|
		|	unsigned mcnd;
		|	BUS_MCND_READ(mcnd);
		|
		|	do_tivi();
		|	uint64_t ti, vi;
		|{
		|	uint64_t ft, tir, vir, m;
		|	unsigned msk, s, fs, u, sgn;
		|	bool sgnbit;
		|
		|	ti = state->tibus;
		|	vi = state->vibus;
		|
		|	unsigned lfl;
		|	BUS_LFL_READ(lfl);				// UCODE
		|
		|	bool fill_mode = false;
		|	if (PIN_FSRC=>) {				// UCODE
		|		fill_mode = lfl >> 6;
		|	} else {
		|		fill_mode = (state->lfreg >> 6) & 1;
		|	}
		|
		|	unsigned lenone;
		|	if (PIN_LSRC=>) {				// UCODE
		|		lenone = lfl & 0x3f;
		|	} else {
		|		lenone = state->lfreg & 0x3f;
		|	}
		|
		|	bool zero_length = !(fill_mode & (lenone == 0x3f));
		|
		|	unsigned off_lit;
		|	BUS_OL_READ(off_lit);				// UCODE
		|
		|	unsigned offset;
		|	if (PIN_OSRC=>) {				// UCODE
		|		offset = off_lit;
		|	} else {
		|		offset = state->oreg;
		|	}
		|
		|	unsigned xword;
		|	xword = state->oreg + (state->lfreg & 0x3f) + (state->lfreg & 0x80);
		|	output.xwrd = xword > 255;
		|
		|	unsigned op, sbit, ebit;
		|	BUS_OP_READ(op);				// UCODE
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
		|	if (op != 0) {
		|		msk = 0x7fff;
		|		switch (offset & 3) {
		|		case 0:
		|			if ((lenone & 3) == 3)
		|				msk |= 0x8000;
		|			break;
		|		case 1:
		|			if ((lenone & 3) == 2)
		|				msk |= 0x8000;
		|			break;
		|		case 2:
		|			if ((lenone & 3) == 1)
		|				msk |= 0x8000;
		|			break;
		|		case 3:
		|			if ((lenone & 3) == 0)
		|				msk |= 0x8000;
		|			break;
		|		}
		|	} else {
		|		msk = 0xffff0000 >> ((offset + (lenone & 3)) >> 2);
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
		|	tir = ti >> fs;
		|	vir = vi >> fs;
		|	switch (fs) {
		|	case 1:
		|		tir |= (vi & 1) << 63;
		|		vir |= (ti & 1) << 63;
		|		break;
		|	case 2:
		|		tir |= (vi & 3) << 62;
		|		vir |= (ti & 3) << 62;
		|		break;
		|	case 3:
		|		tir |= (vi & 7) << 61;
		|		vir |= (ti & 7) << 61;
		|		break;
		|	default:
		|		break;
		|	}
		|	m = 0xf;
		|	ft = 0x0;
		|	for (u = 1; u < (1<<16); u += u) {
		|		if (msk & u)
		|			ft |= vir & m;
		|		else
		|			ft |= tir & m;
		|		m <<= 4;
		|	}
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
		|	if (PIN_RDSRC=>) {				// UCODE
		|		state->rdq = state->mdreg;
		|	} else {
		|		uint64_t yl = 0, yh = 0, q;
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		q = yh | yl;
		|		state->rdq = q;
		|	}
		|
		|	uint64_t vmsk = 0, tmsk = 0;
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
		|	unsigned sel;
		|	BUS_SEL_READ(sel);				// UCODE
		|
		|	uint64_t tii = 0;
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		if (sgnbit)
		|			tii = BUS_DV_MASK;
		|		break;
		|	case 2:
		|		BUS_DV_READ(tii);
		|		tii = state->vibus;
		|		break;
		|	case 3:
		|		BUS_DF_READ(tii);
		|		tii ^= BUS_DF_MASK;
		|		break;
		|	}
		|
		|	uint64_t vout = 0;
		|	vout = (state->rdq & vmsk);
		|	vout |= (tii & (vmsk ^ BUS_DV_MASK));
		|
		|	output.z_qf = PIN_QFOE=>;			// (UCODE)
		|	if (!output.z_qf) {
		|		output.qf = vout ^ BUS_QF_MASK;
		|	}
		|
		|	if (sclk && !PIN_RFCK=>) {
		|		state->refresh_reg = state->tibus;
		|		state->marh &= 0xffffffffULL;
		|		state->marh |= (state->refresh_reg & 0xffffffff00000000ULL);
		|		state->marh ^= 0xffffffff00000000ULL;
		|	}
		|
		|	if (sclk && PIN_LDMDR=>) {	// (UCODE)
		|		uint64_t yl = 0, yh = 0, q;
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		q = yh | yl;
		|		state->mdreg = q;
		|	}
		|
		|	if (sclk && !PIN_TCLK=>) {			// Q4~^
		|		uint64_t out = 0;
		|		out = (state->rdq & tmsk);
		|		out |= (ti & (tmsk ^ BUS_DT_MASK));
		|		state->treg = out;
		|	}
		|
		|	if (sclk && !PIN_VCLK=>) {			// Q4~^
		|		state->vreg = vout;
		|	}
		|
		|	if (sclk && !PIN_OCLK=>) {			// Q4~^
		|		if (PIN_ORSR=>) {			// UCODE
		|			state->oreg = off_lit;
		|		} else {
		|			BUS_DADR_READ(state->oreg);
		|			state->oreg &= 0x7f;
		|		}
		|		output.oreg0 = state->oreg >> 6;
		|	}
		|
		|	if (sclk) {
		|		unsigned lfrc;
		|		BUS_LFRC_READ(lfrc);			// UCODE
		|
		|		switch(lfrc) {
		|		case 0:
		|			state->lfreg = (((vi >> BUS_DV_LSB(31)) & 0x3f) + 1) & 0x3f;
		|			if ((ti >> BUS_DT_LSB(36)) & 1)
		|				state->lfreg |= (1 << 6);
		|			else if (!((vi >> BUS_DV_LSB(25)) & 1))
		|				state->lfreg |= (1 << 6);
		|			state->lfreg ^= 0x7f;
		|			break;
		|		case 1:
		|			state->lfreg = lfl;
		|			break;
		|		case 2:
		|			state->lfreg = (ti >> BUS_DT_LSB(48)) & 0x3f;
		|			if ((ti >> BUS_DT_LSB(36)) & 1)
		|				state->lfreg |= (1 << 6);
		|			state->lfreg = state->lfreg ^ 0x7f;
		|			break;
		|		case 3:	// No load
		|			break;
		|		}
		|
		|		state->marh &= ~(0x3fULL << 15);
		|		state->marh |= (state->lfreg & 0x3f) << 15;
		|		state->marh &= ~(1ULL << 27);
		|		state->marh |= ((state->lfreg >> 6) & 1) << 27;
		|		if (state->lfreg != 0x7f)
		|			state->lfreg |= 1<<7;
		|
		|	}
		|}
		|''')

        file.fmt('''
		|{
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
		|	if (sclk && !(csa >> 2)) {
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
		|	name_match = 
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
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
		|		// output.mspc = (state->sro >> 4) & BUS_MSPC_MASK;
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
		|	bool page_xing = (mcnd >> 6) & 1;
		|	bool sel_pg_xing = PIN_SELPG=>;
		|	bool sel_incyc_px = PIN_SELIN=>;
		|
		|	unsigned marbot = mar_offset & 0x1f;
		|	unsigned inco = marbot;
		|	if (inc_mar && inco != 0x1f)
		|		inco += 1;
		|	inco |= mar_offset & 0x20;
		|
		|	output.z_qadr = PIN_QADROE=>;
		|	if (!output.z_qadr) {
		|		output.qadr = (uint64_t)state->srn << 32;
		|		output.qadr |= state->sro & 0xfffff000;
		|		output.qadr |= (inco & 0x1f) << 7;
		|		output.qadr |= state->oreg;
		|	}
		|
		|	output.pxnx = (
		|		(page_xing && sel_pg_xing && sel_incyc_px) ||
		|		(!page_xing && sel_pg_xing && sel_incyc_px && inc_mar && marbot == 0x1f)
		|	);
		|
		|	if (sclk && (csa == 0)) {
		|		state->ctopn = adr >> 32;
		|		output.nmatch =
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
		|	}
		|
		|	output.z_qspc = PIN_QSPCOE=>;
		|	if (!output.z_qspc) {
		|		output.qspc = (state->sro >> 4) & 7;
		|	}
		|
		|	if (sclk && !(csa >> 2)) {
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
		|	output.line ^= cache_line_tbl_s[(state->sro >> 4) & 0x7];
		|}
		|
		|	if (q4pos) {
		|		unsigned mem_start;
		|		BUS_MSTRT_READ(mem_start);
		|		if (mem_start == 0x18) {
		|			uint64_t tmp = state->tibus;
		|			//BUS_DT_READ(tmp);
		|			state->refresh_count = tmp >> 48;
		|		} else if (state->refresh_count != 0xffff) {
		|			state->refresh_count++;
		|		}
		|		output.rfsh = state->refresh_count != 0xffff;
		|	}
		|''')

        file.fmt('''
		|{
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
		|	bool pgmod = (output.omq >> 1) & 1;
		|	unsigned board_hit, pa027a = 0;
		|	BUS_BDHIT_READ(board_hit);
		|	pa027a = 0;
		|	pa027a |= board_hit << 5;
		|	pa027a |= state->init_mru_d << 4;
		|	pa027a |= (output.omq & 0xc);
		|	pa027a |= 1 << 1;
		|	pa027a |= pgmod << 0;
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
		|	ti = 0;
		|	if (rmarp) {
		|		ti = state->tibus;
		|	}
		|
		|	bool scav_trap_next = state->scav_trap;
		|	if (condsel == 0x69) {		// SCAVENGER_HIT
		|		scav_trap_next = false;
		|	} else if (rmarp) {
		|		scav_trap_next = (ti >> BUS_DT_LSB(32)) & 1;
		|	} else if (state->log_query) {
		|		scav_trap_next = false;
		|	}
		|
		|	bool cache_miss_next = state->cache_miss;
		|	if (condsel == 0x6b) {		// CACHE_MISS
		|		cache_miss_next = false;
		|	} else if (rmarp) {
		|		cache_miss_next = (ti >> BUS_DT_LSB(35)) & 1;
		|	} else if (state->log_query) {
		|		cache_miss_next = PIN_MISS=>;
		|	}
		|
		|	bool csa_oor_next = state->csa_oor;
		|	if (condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|		csa_oor_next = false;
		|	} else if (rmarp) {
		|		csa_oor_next = (ti >> BUS_DT_LSB(33)) & 1;
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
		|			state->mar_modified = (ti >> BUS_DT_LSB(39)) & 1;
		|		} else if (condsel == 0x6d) {
		|			state->mar_modified = 1;
		|		} else if (state->omf20) {
		|			state->mar_modified = le_abort;
		|		} else if (!memstart && le_abort) {
		|			state->mar_modified = le_abort;
		|		}
		|		if (rmarp) {
		|			state->incmplt_mcyc = (ti >> BUS_DT_LSB(40)) & 1;
		|		} else if (start_if_incw) {
		|			state->incmplt_mcyc = true;
		|		} else if (memcyc1) {
		|			state->incmplt_mcyc = le_abort;
		|		}
		|		if (rmarp) {
		|			state->phys_last = (ti >> BUS_DT_LSB(37)) & 1;
		|			state->write_last = (ti >> BUS_DT_LSB(38)) & 1;
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
		|			state->page_xing = (ti >> BUS_DT_LSB(34)) & 1;
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
		|	pa027a |= pgmod << 0;
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
		|
		|	output.csawr = !(
		|		PIN_LABR=> &&
		|		PIN_LEABR=> &&
		|		!(
		|			output.logrwn ||
		|			output.mcntl3
		|		)
		|	);
		|}
		|
		|	output.z_qt = PIN_QTOE=>;
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qt || !output.z_qv) {
		|		do_tivi();
		|		if (!output.z_qt)
		|			output.qt = state->tibus ^ BUS_QT_MASK;
		|		if (!output.z_qv)
		|			output.qv = state->vibus ^ BUS_QT_MASK;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XROTF", PartModelDQ("XROTF", XROTF))
