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
   MEM32 Tracing
   =============

'''

from part import PartModel, PartFactory

class XMTRC(PartFactory):
    ''' MEM32 Tracing '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t traram[1 << 14];
		|	unsigned trareg;
		|	unsigned trace_q1;
		|	unsigned trace_q3;
		|	unsigned col;
		|	unsigned cnt1, cnt2, cnt8;
		|	unsigned co8;
		|	bool traddr12;
		|	bool traddr13;
		|''')

    def private(self):
        enables = (
            "PIN_CLKQ2",
            "PIN_CLKQ4",
            "PIN_IBE0",
            "PIN_ICE0",
            "PIN_ICE1",
            "PIN_IDE",
            "BUS_MODE",
            "PIN_RFSH",
            "PIN_DIR",
            "PIN_ADIR",
        )
        yield from self.event_or(
            "ia_event",
            "BUS_IA",
            *enables,
        )
        yield from self.event_or(
            "ib_event",
            "PIN_COLE",
            "PIN_ROWE",
            "BUS_ROW",
            *enables,
        )
        yield from self.event_or(
            "ic_event",
            "BUS_IC",
            *enables,
        )
        yield from self.event_or(
            "id_event",
            "BUS_ID",
            *enables,
        )
        yield from self.event_or(
            "ram_event",
            *enables,
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned mode;
		|	BUS_MODE_READ(mode);
		|	bool refresh = PIN_RFSH=>;
		|	bool trace_dir = PIN_DIR=>;
		|	bool tr_dram_dir = mode < 0xc;
		|
		|	bool tradr_oe = !(!refresh || mode == 0xa || mode == 0xb);
		|	bool trace_oe = !((!refresh) ||	(mode < 0x8) ||	(mode == 0xc) || (mode == 0xf));
		|	bool q2pos = PIN_CLKQ2.posedge();
		|	bool q2neg = PIN_CLKQ2.negedge();
		|	bool q4pos = PIN_CLKQ4.posedge();
		|	bool q4neg = PIN_CLKQ4.negedge();
		|
		|	unsigned diag;
		|	BUS_IA_READ(diag);
		|	unsigned dcnt;
		|	BUS_DCNT_READ(dcnt);
		|
		|	if (q4pos) {
		|		unsigned cnt1 = state->cnt1;
		|		unsigned cnt2 = state->cnt2;
		|		bool cen =
		|		    !(
		|			((!refresh) && (!(cnt2 & 1)) && ((cnt1) & 5) == 5) ||
		|			(  refresh  && ((dcnt & 0x1d) == 0x05)) ||
		|			(  refresh  && ((dcnt & 0x1e) == 0x04))
		|		    );
		|
		|		BUS_ID_READ(state->trareg);
		|		if (!PIN_C8LD=>) {
		|			BUS_IA_READ(state->cnt8);
		|		} else if (!cen) {
		|			state->cnt8 += 1;
		|		}
		|		state->cnt8 &= 0xff;
		|
		|		if (!refresh) {
		|			if (cnt2 & 1) {
		|			} else if (cnt1 == 0x0) {
		|				cnt1 = 0x3;
		|			} else if (cnt1 == 0x3) {
		|				cnt1 = 0xc;
		|			} else if (cnt1 == 0xc) {
		|				cnt1 = 0xf;
		|			} else {
		|				cnt1 = 0x0;
		|			}
		|			cnt2 ^= 0x1;
		|		} else {
		|			switch (dcnt) {
		|			case 0x04:
		|				if (!state->co8)
		|					cnt1 = state->cnt1 + 1;
		|				break;
		|			case 0x06:
		|				cnt2 = state->cnt2 + 1;
		|				break;
		|			case 0x07:
		|				if (!state->co8)
		|					cnt2 = state->cnt2 + 1;
		|				break;
		|			case 0x0c:
		|				cnt1 = state->cnt2;
		|				break;
		|			case 0x0d:
		|				cnt2 = state->cnt1;
		|				break;
		|			case 0x0e:
		|				cnt1 = diag >> 4;
		|				break;
		|			case 0x0f:
		|				cnt2 = diag >> 4;
		|				break;
		|			default:
		|				if (dcnt >= 0x10)
		|					cnt2 = dcnt & 0xf;
		|				break;
		|			}
		|		}
		|		state->cnt1 = cnt1;
		|		state->cnt2 = cnt2;
		|		state->co8 = (state->cnt8 != 0xff);
		|		output.tradr = cnt1;
		|		output.ta3 = cnt1 & 1;
		|	}
		|
		|	output.ovfo =
		|	    !(
		|		((dcnt == 0x05) && (!state->co8)) ||
		|		(((dcnt & 0x1d) == 0x05) && (!state->co8) && state->cnt2 == 0xf ) ||
		|		((dcnt == 0x06) &&  state->cnt2 == 0xf ) ||
		|		(((dcnt & 0x1e) == 0x04) && (!state->co8) && state->cnt1 == 0xf )
		|	    );
		|
		|	unsigned trace, adr;
		|	bool needadr = false;
		|
		|	if (!trace_oe && trace_dir) {
		|		BUS_IA_READ(trace);
		|		next_trigger(ia_event);
		|	} else if (!PIN_IBE0=> && !tr_dram_dir) {
		|		if (!PIN_ROWE=>) {
		|			BUS_ROW_READ(trace);
		|		} else if (!PIN_COLE=>) {
		|			trace = state->col;
		|		}
		|		next_trigger(ib_event);
		|	} else if (!PIN_ICE0=> && !PIN_ICE1=>) {
		|		BUS_IC_READ(trace);
		|		next_trigger(ic_event);
		|	} else if (!PIN_IDE=>) {
		|		trace = state->trareg;
		|		next_trigger(id_event);
		|	} else {
		|		needadr = true;
		|	}
		|
		|	bool dowrite = false;
		|	if (mode == 0xb && (q2pos || q4pos))
		|		dowrite = true;
		|	if ((mode & 0xc) == 0x4 && q4pos)
		|		dowrite = true;
		|
		|	if (needadr || dowrite) {
		|		adr = 0;
		|		if (state->traddr12) adr |= 2;
		|		if (state->traddr13) adr |= 1;
		|		unsigned ahi = state->cnt1;
		|		adr |= ahi << 10;
		|		if (!tradr_oe) {
		|			unsigned diag2;
		|			BUS_IA_READ(diag2);
		|			adr |= diag2 << 2;
		|		} else {
		|			adr |= state->cnt8 << 2;
		|		}
		|		if (needadr) {
		|			trace = state->traram[adr];
		|			next_trigger(ram_event);
		|		}
		|	}
		|	output.q = trace;
		|
		|	if (!trace_oe && !trace_dir) {
		|		output.z_qdiag = 0;
		|		output.qdiag = trace;
		|	} else if (!tradr_oe && !PIN_ADIR=>) {
		|		output.z_qdiag = 0;
		|		output.qdiag = state->cnt8;
		|	} else {
		|		output.z_qdiag = 1;
		|	}
		|
		|	if (q2neg) {
		|		state->trace_q1 = trace;
		|		if (!PIN_ROWE=>) {
		|			BUS_ROW_READ(output.dr);
		|		} else if (!PIN_COLE=>) {
		|			output.dr = state->col;
		|		} else {
		|			output.dr = trace;
		|		}
		|	}
		|	if (q2pos) {
		|		BUS_COL_READ(state->col);
		|		output.tqb = trace;
		|		if (dowrite)
		|			state->traram[adr] = trace;
		|	}
		|	if (q4neg) {
		|		state->trace_q3 = trace;
		|		if (!PIN_ROWE=>) {
		|			BUS_ROW_READ(output.dr);
		|		} else if (!PIN_COLE=>) {
		|			output.dr = state->col;
		|		} else {
		|			output.dr = trace;
		|		}
		|	}
		|	if (q4pos) {
		|		if (PIN_TSCEN=>) {
		|			output.tstr = state->trace_q1 << 8;
		|			output.tstr |= state->trace_q3;
		|		}
		|		if (dowrite)
		|			state->traram[adr] = trace;
		|	}
		|
		|	if (q2pos) {
		|		switch (mode) {
		|		case 0x2: state->traddr12 = true; break;
		|		case 0x3: state->traddr12 = true; break;
		|		case 0x6: state->traddr12 = true; break;
		|		case 0x7: state->traddr12 = true; break;
		|		case 0x8: state->traddr12 = true; break;
		|		case 0xd: state->traddr12 = true; break;
		|		default: state->traddr12 = false; break;
		|		};
		|	}
		|	if (q4pos) {
		|		switch (mode) {
		|		case 0x2: state->traddr12 = true; break;
		|		case 0x3: state->traddr12 = true; break;
		|		case 0x6: state->traddr12 = true; break;
		|		case 0x7: state->traddr12 = true; break;
		|		default: state->traddr12 = false; break;
		|		};
		|	}
		|	if (q2neg) {
		|		switch (mode) {
		|		case 0x2: state->traddr13 = true; break;
		|		case 0x6: state->traddr13 = true; break;
		|		case 0x1: state->traddr13 = true; break;
		|		case 0x5: state->traddr13 = true; break;
		|		case 0x8: state->traddr13 = true; break;
		|		default: state->traddr13 = false; break;
		|		};
		|	}
		|	if (q4neg) {
		|		switch (mode) {
		|		case 0x2: state->traddr13 = true; break;
		|		case 0x6: state->traddr13 = true; break;
		|		case 0x1: state->traddr13 = true; break;
		|		case 0x5: state->traddr13 = true; break;
		|		default: state->traddr13 = false; break;
		|		};
		|	}
		|
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMTRC", PartModel("XMTRC", XMTRC))
