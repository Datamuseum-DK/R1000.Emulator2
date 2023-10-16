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
   TYP conditions 
   ==============

'''

from part import PartModel, PartFactory

class XTCOND(PartFactory):
    ''' TYP conditions '''

    def state(self, file):
        file.fmt('''
		|	bool cond0, cond1, cond2, cond3, cond4;
		|	bool last_cond;
		|''')

    def private(self):
        ''' private variables '''
        for i in (
                                                             "c0h",
            "c1a",        "c1c",
            "c2a", "c2b", "c2c", "c2d", "c2e", "c2f", "c2g",
            "c3a", "c3b", "c3c",        "c3e",
        ):
            yield from self.event_or(
                i + "_event",
                "BUS_SEL",
                "PIN_SCLK.posedge_event()",
                "PIN_%s" % i.upper(),
            )
        yield from self.event_or(
            "c3d_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_C3A",
            "PIN_C3C",
        )
        yield from self.event_or(
            "c0c_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_C1A",
            "PIN_SELA",
            "PIN_ISBIN",
            "PIN_ABIT0",
            "BUS_BBIT",
        )
        yield from self.event_or(
            "c1b_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_C1A",
            "PIN_OVREN",
            "PIN_C1C",
            "PIN_SELA",
            "PIN_ISBIN",
            "PIN_ABIT0",
            "BUS_BBIT",
        )
        yield from self.event_or(
            "c1d_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_C1C",
            "BUS_ALUZ",
        )
        yield from self.event_or(
            "c1e_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "PIN_ABIT0",
            "BUS_BBIT",
        )
        yield from self.event_or(
            "aluz_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "BUS_ALUZ",
        )
        yield from self.event_or(
            "loop_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "BUS_LOOP",
        )
        yield from self.event_or(
            "bbit_event",
            "BUS_SEL",
            "PIN_SCLK.posedge_event()",
            "BUS_BBIT",
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
		|		PIN_VCOND3<=(!state->cond3);
		|		PIN_VCOND4<=(!state->cond4);
		|	}
		|
		|	bool sclk = PIN_SCLK.posedge();
		|
		|	unsigned sel;
		|	BUS_SEL_READ(sel);
		|
		|	unsigned group = 99;
		|	switch (sel >> 3) {
		|	case 0x3: group = 0; break;
		|	case 0x4: group = 1; break;
		|	case 0x5: group = 2; break;
		|	case 0x6: group = 3; break;
		|	case 0x7: group = 4; break;
		|	case 0xb: group = 0; break;
		|	default: break;
		|	}
		|
		|	bool cond0 = state->cond0;
		|	bool cond1 = state->cond1;
		|	bool cond2 = state->cond2;
		|	bool cond3 = state->cond3;
		|	bool cond4 = state->cond4;
		|	bool last_cond = state->last_cond;
		|
		|	unsigned bbit = 0;
		|	unsigned loop = 0;
		|	unsigned aluz = 0;
		|	unsigned which = sel & 7;
		|
		|#define BBIT0() ((bbit >> 6) & 1)
		|#define SIGNS_EQ() (PIN_ABIT0=> ^ BBIT0())
		|#define OVR_SIGN() (!((SIGNS_EQ() && PIN_ISBIN=>) || (!PIN_ISBIN=> && !PIN_ABIT0=>)))
		|
		|	switch (group) {
		|	case 0:
		|		switch (which) {
		|		case 0:
		|		case 6:
		|			BUS_ALUZ_READ(aluz);
		|			cond0 = aluz != BUS_ALUZ_MASK;
		|			next_trigger(aluz_event);
		|			break;
		|		case 1:
		|			BUS_ALUZ_READ(aluz);
		|			cond0 = aluz == BUS_ALUZ_MASK;
		|			next_trigger(aluz_event);
		|			break;
		|		case 2:
		|			BUS_BBIT_READ(bbit);
		|			cond0 = !(
		|				(SIGNS_EQ() && PIN_ABIT0=>) ||
		|				(PIN_C1A=> && (OVR_SIGN() ^ PIN_SELA=>))
		|			);
		|			next_trigger(c0c_event);
		|			break;
		|		case 4:
		|			BUS_LOOP_READ(loop);
		|			cond0 = loop != BUS_LOOP_MASK;
		|			next_trigger(loop_event);
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
		|			BUS_BBIT_READ(bbit);
		|			cond1 = PIN_OVREN=> || (
		|				PIN_C1A=> ^ PIN_C1C=> ^ PIN_SELA=> ^ OVR_SIGN()
		|			);
		|			next_trigger(c1b_event);
		|			break;
		|		case 2: cond1 = PIN_C1C=>; next_trigger(c1c_event); break;
		|		case 3:
		|			BUS_ALUZ_READ(aluz);
		|			cond1 = !(PIN_C1C=> && (aluz != BUS_ALUZ_MASK));
		|			next_trigger(c1d_event);
		|			break;
		|		case 4:
		|			BUS_BBIT_READ(bbit);
		|			cond1 = SIGNS_EQ();
		|			next_trigger(c1e_event);
		|			break;
		|		case 5: cond1 = true; break;
		|		case 6: cond1 = false; break;
		|		case 7: cond1 = state->last_cond; break;
		|		default: cond1 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond1;
		|		break;
		|	case 2:
		|		switch (which) {
		|		case 0: cond2 = PIN_C2A=>; next_trigger(c2a_event); break;
		|		case 1: cond2 = PIN_C2B=>; next_trigger(c2b_event); break;
		|		case 2: cond2 = PIN_C2C=>; next_trigger(c2c_event); break;
		|		case 3: cond2 = PIN_C2D=>; next_trigger(c2d_event); break;
		|		case 4: cond2 = PIN_C2E=>; next_trigger(c2e_event); break;
		|		case 5: cond2 = PIN_C2F=>; next_trigger(c2f_event); break;
		|		case 6: cond2 = PIN_C2G=>; next_trigger(c2g_event); break;
		|		case 7:
		|			cond2 = PIN_C3C=> && PIN_C3A;
		|			next_trigger(c3d_event);	// 2h and 3d use same
		|			break;
		|		default: cond2 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond2;
		|		break;
		|	case 3:
		|		switch (which) {
		|		case 0: cond3 = PIN_C3A=>; next_trigger(c3a_event); break;
		|		case 1: cond3 = PIN_C3B=>; next_trigger(c3b_event); break;
		|		case 2: cond3 = PIN_C3C=>; next_trigger(c3c_event); break;
		|		case 3:
		|			cond3 = !(PIN_C3A=> || PIN_C3C=>);
		|			next_trigger(c3d_event);
		|			break;
		|		case 4: cond3 = PIN_C3E=>; next_trigger(c3e_event); break;
		|		case 5:
		|			BUS_BBIT_READ(bbit);
		|			cond3 = (bbit >> 4) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		case 6:
		|			BUS_BBIT_READ(bbit);
		|			cond3 = (bbit >> 3) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		case 7:
		|			BUS_BBIT_READ(bbit);
		|			cond3 = (bbit >> 2) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		default: cond3 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond3;
		|		break;
		|	case 4:
		|		switch (which) {
		|		case 0:
		|			BUS_BBIT_READ(bbit);
		|			cond4 = (bbit >> 1) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		case 1:
		|			BUS_BBIT_READ(bbit);
		|			cond4 = (bbit >> 0) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		case 2:
		|			BUS_BBIT_READ(bbit);
		|			cond4 = (bbit & 0x0d) != 0x0d;
		|			next_trigger(bbit_event);
		|			break;
		|		case 7:
		|			BUS_BBIT_READ(bbit);
		|			cond4 = (bbit >> 5) & 1;
		|			next_trigger(bbit_event);
		|			break;
		|		default: cond4 = true; break;
		|		}
		|		if (sclk)
		|			last_cond = cond4;
		|		break;
		|	}
		|	if (last_cond != state->last_cond ||
		|	    cond0 != state->cond0 ||
		|	    cond1 != state->cond1 ||
		|	    cond2 != state->cond2 ||
		|	    cond3 != state->cond3 ||
		|	    cond4 != state->cond4
		|	) {
		|		state->last_cond = last_cond;
		|		state->cond0 = cond0;
		|		state->cond1 = cond1;
		|		state->cond2 = cond2;
		|		state->cond3 = cond3;
		|		state->cond4 = cond4;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCOND", PartModel("XTCOND", XTCOND))
