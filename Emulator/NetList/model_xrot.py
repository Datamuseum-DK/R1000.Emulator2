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

    def state(self, file):
        file.fmt('''
		|       unsigned oreg;
		|       uint64_t mdreg;
		|	uint64_t treg;
		|	uint64_t vreg;
		|	uint64_t rdq;
		|''')

    def xsensitive(self):
        yield "PIN_Q4.pos()"            # Q4
        yield "PIN_FSRC"                # ucode
        yield "PIN_LSRC"                # ucode
        yield "PIN_ORSR"                # ucode
        yield "PIN_OSRC"                # ucode
        yield "BUS_LFRC_SENSITIVE()"    # ucode
        yield "BUS_OP_SENSITIVE()"      # ucode
        yield "BUS_LFL_SENSITIVE()"     # ucode 
        yield "BUS_OL_SENSITIVE()"      # ucode
        yield "BUS_DT_SENSITIVE()"
        yield "BUS_DV_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4pos = PIN_Q4.posedge();
		|	uint64_t ft, tir, vir, m;
		|	unsigned msk, s, fs, u, sgn;
		|	bool sgnbit;
		|
		|	uint64_t ti, vi;
		|	if (!PIN_FT=>) {
		|		BUS_DF_READ(ti);
		|		ti ^= BUS_DF_MASK;
		|	} else {
		|		BUS_DT_READ(ti);
		|	}
		|	if (!PIN_FV=>) {
		|		BUS_DF_READ(vi);
		|		vi ^= BUS_DF_MASK;
		|	} else {
		|		BUS_DV_READ(vi);
		|	}
		|
		|	unsigned lfl;
		|	BUS_LFL_READ(lfl);	// UCODE
		|
		|	bool fill_mode = false;
		|	if (PIN_FSRC=>) {	// UCODE
		|		fill_mode = lfl >> 6;
		|	} else {
		|		fill_mode = (output.lfrg >> 6) & 1;
		|	}
		|
		|	unsigned lenone;
		|	if (PIN_LSRC=>) {	// UCODE
		|		lenone = lfl & 0x3f;
		|	} else {
		|		lenone = output.lfrg & 0x3f;
		|	}
		|
		|	bool zero_length = !(fill_mode & (lenone == 0x3f));
		|
		|	unsigned off_lit;
		|	BUS_OL_READ(off_lit);	// UCODE
		|
		|
		|	// OSMX
		|	unsigned offset;
		|	if (PIN_OSRC=>) {	// UCODE
		|		offset = off_lit;
		|	} else {
		|		offset = state->oreg;
		|	}
		|
		|	// XWALU
		|	unsigned xword;
		|	xword = state->oreg + (output.lfrg & 0x3f) + (output.lfrg & 0x80);
		|	output.xwrd = xword > 255;
		|
		|	// SBTMX
		|
		|	unsigned op, sbit, ebit;
		|	BUS_OP_READ(op);	// UCODE
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
		|	if (PIN_RDSRC=>) {
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
		|	BUS_SEL_READ(sel);
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
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt and !PIN_FT=>) {
		|		BUS_DF_READ(output.qt);
		|		output.qt ^= BUS_DF_MASK;
		|	} else if (!output.z_qt) {
		|		output.qt = state->treg;
		|	}
		|
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv && !PIN_FV=>) {
		|		BUS_DF_READ(output.qv);
		|		output.qv ^= BUS_DF_MASK;
		|	} else if (!output.z_qv) {
		|		output.qv = state->vreg;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = vout ^ BUS_QF_MASK;
		|	}
		|
		|	if (q4pos && PIN_LDMDR=> && PIN_SCLKE) {
		|		uint64_t yl = 0, yh = 0, q;
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		q = yh | yl;
		|		state->mdreg = q;
		|	}
		|
		|	if (PIN_TCLK.posedge()) {
		|		uint64_t out = 0;
		|		out = (state->rdq & tmsk);
		|		out |= (ti & (tmsk ^ BUS_DT_MASK));
		|		state->treg = out;
		|	}
		|
		|	if (PIN_VCLK.posedge()) {
		|		state->vreg = vout;
		|	}
		|
		|	if (PIN_OCLK.posedge()) {	// Q4~^
		|		if (PIN_ORSR=>) {	// UCODE
		|			state->oreg = off_lit;
		|		} else {
		|			BUS_AO_READ(state->oreg);
		|		}
		|		output.oreg = state->oreg;
		|	}
		|
		|	if (PIN_LCLK.posedge()) {
		|		unsigned lfrc;
		|		BUS_LFRC_READ(lfrc);	// UCODE
		|
		|		unsigned lfrg = 0;
		|		switch(lfrc) {
		|		case 0:
		|			lfrg = (((vi >> BUS_DV_LSB(31)) & 0x3f) + 1) & 0x3f;
		|			if ((ti >> BUS_DT_LSB(36)) & 1)
		|				lfrg |= (1 << 6);
		|			else if (!((vi >> BUS_DV_LSB(25)) & 1))
		|				lfrg |= (1 << 6);
		|			lfrg = lfrg ^ 0x7f;
		|			break;
		|		case 1:
		|			lfrg = lfl;
		|			break;
		|		case 2:
		|			lfrg = (ti >> BUS_DT_LSB(48)) & 0x3f;
		|			if ((ti >> BUS_DT_LSB(36)) & 1)
		|				lfrg |= (1 << 6);
		|			lfrg = lfrg ^ 0x7f;
		|			break;
		|		case 3:	// No load
		|			lfrg = output.lfrg;
		|			break;
		|		}
		|
		|		if (lfrg != 0x7f)
		|			lfrg |= 1<<7;
		|
		|		output.lfrg = lfrg;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XROTF", PartModelDQ("XROTF", XROTF))
