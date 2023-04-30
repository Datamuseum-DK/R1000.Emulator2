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

from part import PartModel, PartFactory

class XROTF(PartFactory):

    ''' FIU first stage rotator '''

    def state(self, file):
        file.fmt('''
		|       unsigned lreg;
		|       unsigned oreg;
		|''')

    def sensitive(self):
        yield "PIN_LCLK.pos()"          # Q4
        yield "PIN_OCLK.pos()"          # Q4
        yield "PIN_OE"                  # ucode
        yield "PIN_FSRC"                # ucode
        yield "PIN_LSRC"                # ucode
        yield "PIN_ORSR"                # ucode
        yield "PIN_OSRC"                # ucode
        yield "BUS_LFRC_SENSITIVE()"    # ucode
        yield "BUS_OP_SENSITIVE()"      # ucode
        yield "BUS_LFL_SENSITIVE()"     # ucode 
        yield "BUS_OL_SENSITIVE()"      # ucode
        yield "PIN_OCE"
        yield "BUS_TI_SENSITIVE()"
        yield "BUS_VI_SENSITIVE()"

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "oe_event",
            "PIN_LCLK.posedge_event()",
            "PIN_OCLK.posedge_event()",
            "PIN_OE.negedge_event()",
            "PIN_FSRC",
            "PIN_LSRC",
            "PIN_ORSR",
            "PIN_OSRC",
            "BUS_LFRC",
            "BUS_OP",
            "BUS_LFL",
            "BUS_OL",
            "PIN_OCE",
            #"PIN_TI",
            #"PIN_VI",
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t ti, vi, ft, tir, vir, m;
		|	unsigned msk, s, fs, u, sgn;
		|	bool sgnbit;
		|	unsigned op;
		|
		|	BUS_OP_READ(op);	// UCODE
		|	BUS_TI_READ(ti);
		|	BUS_VI_READ(vi);
		|
		|	unsigned lfrg = 0;
		|	unsigned lfl;
		|	BUS_LFL_READ(lfl);	// UCODE
		|	if (PIN_LCLK.posedge()) {
		|		unsigned lfrc;
		|		BUS_LFRC_READ(lfrc);	// UCODE
		|
		|		if (lfrc & 1) {
		|			lfrg = lfl;
		|		} else {
		|			if (lfrc & 2) {
		|				lfrg = (ti >> 15) & 0x3f;
		|				if ((ti >> (63-36)) & 1)
		|					lfrg |= (1 << 6);
		|			} else {
		|				// LDALU
		|				lfrg = (((vi >> 32) & 0x3f) + 1) & 0x3f;
		|				if ((ti >> (63-36)) & 1)
		|					lfrg |= (1 << 6);
		|				else if (!((vi >> (63-25)) & 1))
		|					lfrg |= (1 << 6);
		|			}
		|			lfrg = lfrg ^ 0x7f;
		|		}
		|
		|		// LFNAN0
		|		if (lfrg != 0x7f)
		|			lfrg |= 1<<7;
		|
		|		BUS_LFRG_WRITE(lfrg);
		|		state->lreg = lfrg;
		|	}
		|
		|	// LAOIA
		|	bool fill_mode = false;
		|	if (PIN_FSRC=>) {	// UCODE
		|		fill_mode = lfl >> 6;
		|	} else {
		|		fill_mode = (state->lreg >> 6) & 1;
		|	}
		|
		|	// LSMX
		|	unsigned lenone;
		|
		|	if (PIN_LSRC=>) {	// UCODE
		|		lenone = lfl & 0x3f;
		|	} else {
		|		lenone = state->lreg & 0x3f;
		|	}
		|
		|	// ZLNAN
		|	bool zlen = !(fill_mode & (lenone == 0x3f));
		|	PIN_ZL<=(zlen);
		|
		|	// OFSMX
		|	bool ckpn;
		|	unsigned oregin;
		|	unsigned off_lit;
		|	BUS_OL_READ(off_lit);	// UCODE
		|	if (PIN_ORSR=>) {	// UCODE
		|		oregin = off_lit;
		|		ckpn = false;
		|	} else {
		|		BUS_AO_READ(oregin);
		|		ckpn = PIN_OCE=>;
		|	}
		|	PIN_CKPN<=(ckpn);
		|
		|	if (PIN_OCLK.posedge()) {	// Q4~^
		|		state->oreg = oregin;
		|		BUS_OREG_WRITE(state->oreg);
		|	}
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
		|	xword = state->oreg + (state->lreg & 0x3f) + (state->lreg & 0x80);
		|	PIN_XWRD<=(xword > 255);
		|
		|	// SBTMX
		|	unsigned sbit;
		|
		|	switch (op) {
		|	case 0:
		|		sbit = (lenone ^ 0x3f) | (1<<6);
		|		break;
		|	case 1:
		|		sbit = 0;
		|		break;
		|	case 2:
		|		sbit = offset;
		|		break;
		|	case 3:
		|		sbit = offset;
		|		break;
		|	}
		|	BUS_SBIT_WRITE(sbit);
		|
		|	unsigned ebit;
		|	if (op & 1) {
		|		ebit = (lenone & 0xf) + (offset & 0xf);
		|		ebit += lenone & 0x30;
		|		ebit += offset & 0x70;
		|	} else {
		|		ebit = 0x7f;
		|	}
		|	BUS_EBIT_WRITE(ebit);
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
		|	PIN_SGNB<=(sgnbit);
		|
		|	if (PIN_OE=>) {
		|		BUS_Q_Z();
		|		next_trigger(oe_event);
		|	} else {
		|		uint64_t yl = 0, yh = 0, q;
		|
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		q = yh | yl;
		|		BUS_Q_WRITE(q);
		|	}
		|
		|	TRACE(
		|	    << " oe " << PIN_OE?
		|	    << " lclk^ " << PIN_LCLK.posedge()
		|	    << " oclk^ " << PIN_OCLK.posedge()
		|	    << " op " << BUS_OP_TRACE()
		|	    << " ti " << BUS_TI_TRACE()
		|	    << " vi " << BUS_VI_TRACE()
		|	    << " lfl " << BUS_LFL_TRACE()
		|	    << " lfrc " << BUS_LFRC_TRACE()
		|	    << " ao " << BUS_AO_TRACE()
		|	    << " ol " << BUS_OL_TRACE()
		|	    << " lsrc " << PIN_LSRC?
		|	    << " orsr " << PIN_ORSR?
		|	    << " oce " << PIN_OCE?
		|	    << " osrc " << PIN_OSRC?
		|	    << " - ft " << std::hex << ft
		|	    << " sgnbit " << sgnbit
		|	    << " lfrg " << std::hex << lfrg
		|	    << " sbit " << std::hex << sbit
		|	    << " ebit " << std::hex << ebit
		|	    << " zlen " << zlen
		|	);
		|''')


class XROT16(PartFactory):

    ''' 16x4x2 rotator '''


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a, b, s, ab, y = 0;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_S_READ(s);
		|	BUS_AB_READ(ab);
		|	a >>= s;
		|	b >>= s;
		|	y |= (ab & 0x1) ? (b & 0x000f) : (a & 0x000f);
		|	y |= (ab & 0x2) ? (b & 0x00f0) : (a & 0x00f0);
		|	y |= (ab & 0x4) ? (b & 0x0f00) : (a & 0x0f00);
		|	y |= (ab & 0x8) ? (b & 0xf000) : (a & 0xf000);
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " s " << BUS_S_TRACE()
		|	    << " ab " << BUS_AB_TRACE()
		|	    << " y " << std::hex << y
		|	);
		|	BUS_Y_WRITE(y);
		|''')


class XROT64(PartFactory):

    ''' 64x4 rotator '''


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t s, i, yl = 0, yh = 0, y;
		|
		|	if (PIN_OE=>) {
		|		TRACE(<<"Z");
		|		BUS_Y_Z();
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|
		|	BUS_S_READ(s);
		|	BUS_I_READ(i);
		|	s <<= 2;
		|	yl = i >> s;
		|	yh = i << (64 - s);
		|	y = yh | yl;
		|	BUS_Y_WRITE(y);
		|	TRACE(
		|	    << " oe " << PIN_OE?
		|	    << " s " << BUS_S_TRACE()
		|	    << " i " << BUS_I_TRACE()
		|	    << " " << std::hex << i
		|	    << " y " << std::hex << y
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XROT16", PartModel("XROT16", XROT16))
    part_lib.add_part("XROT64", PartModel("XROT64", XROT64))
    part_lib.add_part("XROTF", PartModel("XROTF", XROTF))
