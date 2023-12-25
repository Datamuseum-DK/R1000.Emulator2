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
   VAL conditions 
   ==============

'''

from part import PartModel, PartFactory

class XVCOND(PartFactory):
    ''' VAL conditions '''

    def state(self, file):
        file.fmt('''
		|	bool cond0, cond1, cond2;
		|	bool last_cond;
		|	bool m_bit;
		|''')

    def private(self):
        ''' private variables '''
        ovrsgn = (
            "PIN_ISBN",
            "PIN_BAD0",
            "PIN_BBD0",
        )
        for i in (
                                                             "c0h",
            "c1a",        "c1c",                             "c1h",
                                 "c2d",
        ):
            yield from self.event_or(
                i + "_event",
                "BUS_SEL",
                "PIN_SCLK.posedge_event()",
                "PIN_%s" % i.upper(),
            )
        yield from self.event_or(
            "zero_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "BUS_AZ",
        )
        yield from self.event_or(
            "c0c_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_BBD0",
            "PIN_SELA",
            "PIN_BAD0",
            "PIN_BBD0",
            "PIN_C1A",
            *ovrsgn,
        )
        yield from self.event_or(
            "c0e_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "BUS_LCN",
        )
        yield from self.event_or(
            "c1b_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_SELA",
            "PIN_OVRE",
            "PIN_C1A",
            "PIN_C1C",
	    *ovrsgn,
        )
        yield from self.event_or(
            "c1d_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_C1C",
            "BUS_AZ",
        )
        yield from self.event_or(
            "c1e_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_BAD0",
            "PIN_BBD0",
        )

    def sensitive(self):
        yield "PIN_SCLK.pos()"
        yield "BUS_SEL_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_LVCND<=(state->last_cond);
		|		PIN_VCOND0<=(!state->cond0);
		|		PIN_VCOND1<=(!state->cond1);
		|		PIN_VCOND2<=(!state->cond2);
		|		PIN_MBIT<=(state->m_bit);
		|	}
		|
		|	bool sclk = PIN_SCLK.posedge();
		|
		|	unsigned sel;
		|	BUS_SEL_READ(sel);
		|
		|	unsigned group = 99;
		|	switch (sel >> 3) {
		|	case 0x0: group = 0; break;
		|	case 0x1: group = 1; break;
		|	case 0x2: group = 2; break;
		|	case 0xb: group = 0; break;
		|	default: break;
		|	}
		|
		|	bool cond0 = state->cond0;
		|	bool cond1 = state->cond1;
		|	bool cond2 = state->cond2;
		|	bool last_cond = state->last_cond;
		|	bool m_bit = state->m_bit;
		|
		|	if (sclk) {
		|		m_bit = PIN_C1C=>;
		|	} else {
		|		m_bit = state->m_bit;
		|	}
		|
		|	bool ovrsgn = false;
		|#define DO_OVRSGN() \\
		|	do { \\
		|		bool a0 = PIN_BAD0=>; \\
		|		bool b0 = PIN_BBD0=>; \\
		|		bool se = PIN_ISBN=>; \\
		|		ovrsgn = !( \\
		|			(se && (a0 ^ b0)) || \\
		|			(!se && !a0) \\
		|		); \\
		|	} while (false)
		|	unsigned which = sel & 7;
		|	unsigned zero = 0;
		|	switch (group) {
		|	case 0:
		|		switch (which) {
		|		case 0:
		|			BUS_AZ_READ(zero);
		|			cond0 = (zero != 0xff);
		|			next_trigger(zero_event);
		|			break;
		|		case 1:
		|		case 6:
		|			BUS_AZ_READ(zero);
		|			cond0 = (zero == 0xff);
		|			next_trigger(zero_event);
		|			break;
		|		case 2:
		|			DO_OVRSGN();
		|			cond0 = !(
		|				(PIN_BBD0=> && (PIN_BAD0=> ^ PIN_BBD0=>)) ||
		|				(!PIN_C1A=> && (ovrsgn ^ PIN_SELA=>))
		|			);
		|			next_trigger(c0c_event);
		|			break;
		|		case 4:
		|			unsigned loop;
		|			BUS_LCN_READ(loop);
		|			cond0 = loop != BUS_LCN_MASK;
		|			next_trigger(c0e_event);
		|			break;
		|		case 7: cond0 = PIN_C0H=>; next_trigger(c0h_event); break;
		|		default: cond0 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond0;
		|		break;
		|	case 1:
		|		switch (which) {
		|		case 0: cond1 = !PIN_C1A=>; next_trigger(c1a_event); break;
		|		case 1:
		|			DO_OVRSGN();
		|			cond1 = PIN_OVRE=> || !(ovrsgn ^ PIN_SELA=> ^ (!PIN_C1A=>) ^ PIN_C1C=>);
		|			next_trigger(c1b_event);
		|			break;
		|		case 2: cond1 = PIN_C1C=>; next_trigger(c1c_event); break;
		|		case 3:
		|			BUS_AZ_READ(zero);
		|			cond1 = !PIN_C1C=> || (zero == 0xff);
		|			next_trigger(c1d_event);
		|			break;
		|		case 4:
		|			cond1 = (PIN_BAD0=> ^ PIN_BBD0);
		|			next_trigger(c1e_event);
		|			break;
		|		case 7: cond1 = PIN_C1H=>; next_trigger(c1h_event); break;
		|		default: cond1 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond1;
		|		break;
		|	case 2:
		|		switch (which) {
		|		case 0:
		|			BUS_AZ_READ(zero);
		|			cond2 = ((zero & 0xf0) != 0xf0);
		|			next_trigger(zero_event);
		|			break;
		|		case 1:
		|			BUS_AZ_READ(zero);
		|			cond2 = ((zero & 0xfc) != 0xfc);
		|			next_trigger(zero_event);
		|			break;
		|		case 2:
		|			BUS_AZ_READ(zero);
		|			cond2 = ((zero & 0x0c) != 0x0c);
		|			next_trigger(zero_event);
		|			break;
		|		case 3: cond2 = PIN_C2D=>; next_trigger(c2d_event); break;
		|		case 5: cond2 = m_bit; break;
		|		case 6: cond2 = false; break;
		|		default: cond2 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond2;
		|		break;
		|	}
		|	if (last_cond != state->last_cond ||
		|	    cond0 != state->cond0 ||
		|	    cond1 != state->cond1 ||
		|	    cond2 != state->cond2 ||
		|	    m_bit != state->m_bit
		|	) {
		|		state->last_cond = last_cond;
		|		state->cond0 = cond0;
		|		state->cond1 = cond1;
		|		state->cond2 = cond2;
		|		state->m_bit = m_bit;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCOND", PartModel("XVCOND", XVCOND))
