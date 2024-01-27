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

    autopin = True

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

        file.fmt('''
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
		|	bool cond;
		|
		|	if (sclk) {
		|		output.mbit = PIN_C1C=>;
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
		|			cond = (zero != 0xff);
		|			idle_next = &zero_event;
		|			break;
		|		case 1:
		|		case 6:
		|			BUS_AZ_READ(zero);
		|			cond = (zero == 0xff);
		|			idle_next = &zero_event;
		|			break;
		|		case 2:
		|			DO_OVRSGN();
		|			cond = !(
		|				(PIN_BBD0=> && (PIN_BAD0=> ^ PIN_BBD0=>)) ||
		|				(!PIN_C1A=> && (ovrsgn ^ PIN_SELA=>))
		|			);
		|			idle_next = &c0c_event;
		|			break;
		|		case 4:
		|			unsigned loop;
		|			BUS_LCN_READ(loop);
		|			cond = loop != BUS_LCN_MASK;
		|			idle_next = &c0e_event;
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
		|		output.vcond = !cond ? 4 : 0;
		|		break;
		|	case 1:
		|		switch (which) {
		|		case 0:
		|			cond = !PIN_C1A=>;
		|			idle_next = &c1a_event;
		|			break;
		|		case 1:
		|			DO_OVRSGN();
		|			cond = PIN_OVRE=> || !(ovrsgn ^ PIN_SELA=> ^ (!PIN_C1A=>) ^ PIN_C1C=>);
		|			idle_next = &c1b_event;
		|			break;
		|		case 2:
		|			cond = PIN_C1C=>;
		|			idle_next = &c1c_event;
		|			break;
		|		case 3:
		|			BUS_AZ_READ(zero);
		|			cond = !PIN_C1C=> || (zero == 0xff);
		|			idle_next = &c1d_event;
		|			break;
		|		case 4:
		|			cond = (PIN_BAD0=> ^ PIN_BBD0);
		|			idle_next = &c1e_event;
		|			break;
		|		case 7:
		|			cond = PIN_C1H=>;
		|			idle_next = &c1h_event;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		output.vcond = !cond ? 2 : 0;
		|		break;
		|	case 2:
		|		switch (which) {
		|		case 0:
		|			BUS_AZ_READ(zero);
		|			cond = ((zero & 0xf0) != 0xf0);
		|			idle_next = &zero_event;
		|			break;
		|		case 1:
		|			BUS_AZ_READ(zero);
		|			cond = ((zero & 0xfc) != 0xfc);
		|			idle_next = &zero_event;
		|			break;
		|		case 2:
		|			BUS_AZ_READ(zero);
		|			cond = ((zero & 0x0c) != 0x0c);
		|			idle_next = &zero_event;
		|			break;
		|		case 3:
		|			cond = PIN_C2D=>;
		|			idle_next = &c2d_event;
		|			break;
		|		case 5:
		|			cond = output.mbit;
		|			break;
		|		case 6:
		|			cond = false;
		|			break;
		|		default:
		|			cond = true;
		|			break;
		|		}
		|		if (sclk)
		|			output.lvcnd = cond;
		|		output.vcond = !cond ? 1 : 0;
		|		break;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCOND", PartModel("XVCOND", XVCOND))
