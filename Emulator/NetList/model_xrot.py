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
		|	unsigned lfreg;
		|	sc_core::sc_event_or_list *idle_this;
		|
		|	uint32_t srn, sro, par, ctopn, ctopo;
		|	unsigned nve, pdreg;
		|	unsigned moff;
		|	bool pdt;
		|
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "q4_event",
            "PIN_H1.posedge_event()",
        )
        yield from self.event_or(
            "ftv_event", "PIN_Q4.posedge_event()", "BUS_DF", "BUS_DT", "BUS_DV",
        )
        yield from self.event_or(
            "tv_event", "PIN_Q4.posedge_event()", "BUS_DT", "BUS_DV",
        )
        yield from self.event_or(
            "f_event", "PIN_Q4.posedge_event()", "BUS_DF",
        )
        yield from self.event_or(
            "t_event", "PIN_Q4.posedge_event()", "BUS_DT",
        )
        yield from self.event_or(
            "v_event", "PIN_Q4.posedge_event()", "BUS_DV",
        )
        yield from self.event_or(
            "ft_event", "PIN_Q4.posedge_event()", "BUS_DF", "BUS_DT",
        )
        yield from self.event_or(
            "fv_event", "PIN_Q4.posedge_event()", "BUS_DF", "BUS_DV",
        )
        yield from self.event_or(
            "no_event", "PIN_Q4.posedge_event()",
        )

    def sensitive(self):
        yield "PIN_H1.pos()"
        yield "PIN_Q4.pos()"

        #yield "PIN_QFOE"
        #yield "PIN_QTOE"
        #yield "PIN_QVOE"

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
		|{
		|	uint64_t ft, tir, vir, m;
		|	unsigned msk, s, fs, u, sgn;
		|	bool sgnbit;
		|       bool need_fiu = false;
		|       bool need_ti = false;
		|       bool need_vi = false;
		|       bool need_msr = false;
		|
		|	uint64_t ti, vi;
		|	if (!PIN_FT=>) {				// UCODE
		|               need_fiu = true;
		|		BUS_DF_READ(ti);
		|		ti ^= BUS_DF_MASK;
		|	} else {
		|		need_ti = true;
		|		BUS_DT_READ(ti);
		|	}
		|	if (!PIN_FV=>) {				// UCODE
		|               need_fiu = true;
		|		BUS_DF_READ(vi);
		|		vi ^= BUS_DF_MASK;
		|	} else {
		|		need_vi = true;
		|		BUS_DV_READ(vi);
		|	}
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
		|		need_vi = true;
		|		BUS_DV_READ(tii);
		|		break;
		|	case 3:
		|               need_fiu = true;
		|		BUS_DF_READ(tii);
		|		tii ^= BUS_DF_MASK;
		|		break;
		|	}
		|
		|	uint64_t vout = 0;
		|	vout = (state->rdq & vmsk);
		|	vout |= (tii & (vmsk ^ BUS_DV_MASK));
		|
		|
		|	output.z_qt = PIN_QTOE=>;			// UCODE
		|	if (!output.z_qt and !PIN_MAROE=>) {		// UCODE
		|		uint64_t tmp;
		|		tmp = (state->sro >> 4) & 0x7;
		|		state->marh &= ~0x07;
		|		state->marh |= tmp;
		|		tmp = mcnd ^ BUS_MCND_MASK; 
		|		state->marh &= ~(0x1efULL << 23ULL);
		|		state->marh |= tmp << 23ULL;
		|		output.qt = ~state->marh;
		|		need_msr = true;
		|	} else if (!output.z_qt and !PIN_FT=>) {	// UCODE
		|               need_fiu = true;
		|		BUS_DF_READ(output.qt);
		|		output.qt ^= BUS_DF_MASK;
		|	} else if (!output.z_qt) {
		|		output.qt = state->treg;
		|	}
		|
		|	output.z_qv = PIN_QVOE=>;			// UCODE
		|	if (!output.z_qv && !PIN_FV=>) {		// UCODE
		|               need_fiu = true;
		|		BUS_DF_READ(output.qv);
		|		output.qv ^= BUS_DF_MASK;
		|	} else if (!output.z_qv) {
		|		output.qv = state->vreg;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;			// (UCODE)
		|	if (!output.z_qf) {
		|		output.qf = vout ^ BUS_QF_MASK;
		|	}
		|
		|	if (sclk && !PIN_RFCK=>) {
		|		BUS_DT_READ(state->refresh_reg);
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
		|	if (PIN_H1.posedge() && !need_msr) {
		|		if (need_fiu && need_ti && need_vi) {
		|			//state->idle_this = &ftv_event;
		|		} else if (need_fiu && need_ti) {
		|			state->idle_this = &ft_event;
		|		} else if (need_fiu && need_vi) {
		|			state->idle_this = &fv_event;
		|		} else if (need_fiu) {
		|			state->idle_this = &f_event;
		|		} else if (need_ti && need_vi) {
		|			state->idle_this = &tv_event;
		|		} else if (need_ti) {
		|			//state->idle_this = &t_event;
		|ALWAYS_TRACE(<<"WHAT " << need_fiu << need_ti << need_vi);
		|		} else if (need_vi) {
		|			//state->idle_this = &v_event;
		|ALWAYS_TRACE(<<"WHAT " << need_fiu << need_ti << need_vi);
		|		} else {
		|			state->idle_this = &no_event;
		|		}
		|	}
		|	if (need_msr) {
		|	} else if (q4pos) {
		|		idle_next = &q4_event;
		|		state->idle_this = NULL;
		|	} else {
		|		idle_next = state->idle_this;
		|	}
		|	idle_next = NULL;
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
		|	if (!output.z_qv && !PIN_MAROE=>) {
		|		output.qv = (uint64_t)state->srn << 32;
		|		output.qv |= state->sro & 0xffffff80;
		|		output.qv |= state->oreg;
		|		output.qv ^= BUS_QV_MASK;
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
		|		BUS_MSTA_READ(mem_start);
		|		if (mem_start == 0x18) {
		|			uint64_t tmp;
		|			BUS_DT_READ(tmp);
		|			state->refresh_count = tmp >> 48;
		|		} else if (state->refresh_count != 0xffff) {
		|			state->refresh_count++;
		|		}
		|		output.rfsh = state->refresh_count != 0xffff;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XROTF", PartModelDQ("XROTF", XROTF))
