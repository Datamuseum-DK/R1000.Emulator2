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

    autopin = True

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

        file.fmt('''
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
		|	unsigned bbit = 0;
		|	unsigned loop = 0;
		|	unsigned aluz = 0;
		|	unsigned which = sel & 7;
		|
		|#define BBIT0() ((bbit >> 6) & 1)
		|#define SIGNS_EQ() (PIN_ABIT0=> ^ BBIT0())
		|#define OVR_SIGN() (!((SIGNS_EQ() && PIN_ISBIN=>) || (!PIN_ISBIN=> && !PIN_ABIT0=>)))
		|
		|	bool cond;
		|	switch (group) {
		|	case 0:
		|		switch (which) {
		|		case 0:
		|		case 6:
		|			BUS_ALUZ_READ(aluz);
		|			cond = aluz != BUS_ALUZ_MASK;
		|			idle_next = &aluz_event;
		|			break;
		|		case 1:
		|			BUS_ALUZ_READ(aluz);
		|			cond = aluz == BUS_ALUZ_MASK;
		|			idle_next = &aluz_event;
		|			break;
		|		case 2:
		|			BUS_BBIT_READ(bbit);
		|			cond = !(
		|				(SIGNS_EQ() && PIN_ABIT0=>) ||
		|				(PIN_C1A=> && (OVR_SIGN() ^ PIN_SELA=>))
		|			);
		|			idle_next = &c0c_event;
		|			break;
		|		case 4:
		|			BUS_LOOP_READ(loop);
		|			cond = loop != BUS_LOOP_MASK;
		|			idle_next = &loop_event;
		|			break;
		|		case 7:
		|			cond = PIN_C0H=>;
		|			idle_next = &c0h_event;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		if (!cond)
		|			output.vcond |= 0x10;
		|		else
		|			output.vcond &= ~0x10;
		|		break;
		|	case 1:
		|		switch (which) {
		|		case 0:
		|			cond = !PIN_C1A=>;
		|			idle_next = &c1a_event;
		|			break;
		|		case 1:
		|			BUS_BBIT_READ(bbit);
		|			cond = PIN_OVREN=> || (
		|				PIN_C1A=> ^ PIN_C1C=> ^ PIN_SELA=> ^ OVR_SIGN()
		|			);
		|			idle_next = &c1b_event;
		|			break;
		|		case 2:
		|			cond = PIN_C1C=>;
		|			idle_next = &c1c_event;
		|			break;
		|		case 3:
		|			BUS_ALUZ_READ(aluz);
		|			cond = !(PIN_C1C=> && (aluz != BUS_ALUZ_MASK));
		|			idle_next = &c1d_event;
		|			break;
		|		case 4:
		|			BUS_BBIT_READ(bbit);
		|			cond = SIGNS_EQ();
		|			idle_next = &c1e_event;
		|			break;
		|		case 5:
		|			cond = true;
		|			break;
		|		case 6:
		|			cond = false;
		|			break;
		|		case 7:
		|			cond = output.lvcnd;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		if (!cond)
		|			output.vcond |= 0x08;
		|		else
		|			output.vcond &= ~0x08;
		|		break;
		|	case 2:
		|		switch (which) {
		|		case 0:
		|			cond = PIN_C2A=>;
		|			idle_next = &c2a_event;
		|			break;
		|		case 1:
		|			cond = PIN_C2B=>;
		|			idle_next = &c2b_event;
		|			break;
		|		case 2:
		|			cond = PIN_C2C=>;
		|			idle_next = &c2c_event;
		|			break;
		|		case 3:
		|			cond = PIN_C2D=>;
		|			idle_next = &c2d_event;
		|			break;
		|		case 4:
		|			cond = PIN_C2E=>;
		|			idle_next = &c2e_event;
		|			break;
		|		case 5:
		|			cond = PIN_C2F=>;
		|			idle_next = &c2f_event;
		|			break;
		|		case 6:
		|			cond = PIN_C2G=>;
		|			idle_next = &c2g_event;
		|			break;
		|		case 7:
		|			cond = PIN_C3C=> && PIN_C3A;
		|			idle_next = &c3d_event;	// 2h and 3d use same
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		if (!cond)
		|			output.vcond |= 0x04;
		|		else
		|			output.vcond &= ~0x04;
		|		break;
		|	case 3:
		|		switch (which) {
		|		case 0:
		|			cond = PIN_C3A=>;
		|			idle_next = &c3a_event;
		|			break;
		|		case 1:
		|			cond = PIN_C3B=>;
		|			idle_next = &c3b_event;
		|			break;
		|		case 2:
		|			cond = PIN_C3C=>;
		|			idle_next = &c3c_event;
		|			break;
		|		case 3:
		|			cond = !(PIN_C3A=> || PIN_C3C=>);
		|			idle_next = &c3d_event;
		|			break;
		|		case 4:
		|			cond = PIN_C3E=>;
		|			idle_next = &c3e_event;
		|			break;
		|		case 5:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 4) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		case 6:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 3) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		case 7:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 2) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		if (!cond)
		|			output.vcond |= 0x02;
		|		else
		|			output.vcond &= ~0x02;
		|		break;
		|	case 4:
		|		switch (which) {
		|		case 0:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 1) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		case 1:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 0) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		case 2:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit & 0x0d) != 0x0d;
		|			idle_next = &bbit_event;
		|			break;
		|		case 7:
		|			BUS_BBIT_READ(bbit);
		|			cond = (bbit >> 5) & 1;
		|			idle_next = &bbit_event;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		if (!cond)
		|			output.vcond |= 0x01;
		|		else
		|			output.vcond &= ~0x01;
		|		break;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTCOND", PartModel("XTCOND", XTCOND))
