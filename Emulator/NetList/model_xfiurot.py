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
   FIU Rotators
   ============

'''

from part import PartModelDQ, PartFactory

class XFIUROT(PartFactory):
    ''' FIU Rotators '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t treg;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool tpos = PIN_TCLK.posedge();
		|
		|	uint64_t vmsk = 0, tmsk = 0;
		|	if (PIN_ZLEN=>) {
		|		unsigned sbit, ebit;
		|		BUS_SBIT_READ(sbit);
		|		BUS_EBIT_READ(ebit);
		|
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
		|	if (tpos) {
		|		uint64_t tii = 0;
		|		BUS_DT_READ(tii);
		|
		|		uint64_t rdata;
		|		BUS_RD_READ(rdata);
		|
		|		uint64_t out = 0;
		|		out = (rdata & tmsk);
		|		out |= (tii & (tmsk ^ BUS_DT_MASK));
		|		state->treg = out;
		|	}
		|
		|	output.z_qt = PIN_QTOE=>;
		|	bool ft = PIN_FT=>;
		|
		|	if (!output.z_qt && !ft) {
		|		BUS_DF_READ(output.qt);
		|		output.qt ^= BUS_DF_MASK;
		|	} else if (!output.z_qt) {
		|		output.qt = state->treg;
		|	}
		|	if (PIN_DBGI=>) {
		|		output.dbg = 0xaaaaaaaaaaaaaaaaULL;
		|	} else if (!ft) {
		|		BUS_DF_READ(output.dbg);
		|		output.dbg ^= BUS_DF_MASK;
		|	} else {
		|		output.dbg = state->treg;
		|	}
		|''')


class XFIUROV(PartFactory):
    ''' FIU Rotators '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t vreg;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool vpos = PIN_VCLK.posedge();
		|
		|	uint64_t vmsk = 0, tmsk = 0;
		|	if (PIN_ZLEN=>) {
		|		unsigned sbit, ebit;
		|		BUS_SBIT_READ(sbit);
		|		BUS_EBIT_READ(ebit);
		|
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
		|	uint64_t tii = 0;
		|	unsigned sel;
		|	bool sign;
		|
		|	BUS_SEL_READ(sel);
		|
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		sign = PIN_SIGN=>;
		|		if (sign)
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
		|	uint64_t rdata;
		|	BUS_RD_READ(rdata);
		|
		|	uint64_t out = 0;
		|	out = (rdata & vmsk);
		|	out |= (tii & (vmsk ^ BUS_DV_MASK));
		|
		|	if (vpos) {
		|		state->vreg = out;
		|	}
		|
		|	output.z_qv = PIN_QVOE=>;
		|	bool fv = PIN_FV=>;
		|
		|	if (!output.z_qv and !fv) {
		|		BUS_DF_READ(output.qv);
		|		output.qv ^= BUS_DF_MASK;
		|	} else if (!output.z_qv) {
		|		output.qv = state->vreg;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = out ^ BUS_QF_MASK;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUROT", PartModelDQ("XFIUROT", XFIUROT))
    part_lib.add_part("XFIUROV", PartModelDQ("XFIUROV", XFIUROV))
