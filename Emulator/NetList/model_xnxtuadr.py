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
   Select next micro address
   =========================

'''

from part import PartModel, PartFactory

class XNXTUADR(PartFactory):
    ''' Select next micro address '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned fiu;
		|	unsigned other;
		|	unsigned late_u;
		|	unsigned prev;
		|''')

    def sensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned data = 0, sel;
		|	bool macro_hic = true;
		|	bool u_event = true;
		|
		|	if (PIN_FIU_CLK.posedge()) {
		|		BUS_FIU_READ(state->fiu);
		|		state->fiu &= 0x3fff;
		|	}	
		|
		|	if (PIN_LOCAL_CLK.posedge()) {
		|		BUS_LATE_READ(state->late_u);
		|		sel = 0;
		|		if (!PIN_U_MUX_SEL) sel |= 4;
		|		if (PIN_G_SEL0) sel |= 2;
		|		if (PIN_G_SEL1) sel |= 1;
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 2:
		|			BUS_TOP_READ(data);
		|			break;
		|		case 3:
		|		case 4:
		|			BUS_CUR_READ(data);
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|		state->other = data;
		|	}
		|
		|	if (!PIN_DV_U) {
		|		BUS_DIAG_READ(data);
		|	} else if (PIN_BAD_HINT) {
		|		data = state->other;
		|	} else if (PIN_LATE_MACRO) {
		|		// Not tested by expmon_test_seq ?
		|		data = state->late_u << 3;
		|		data ^= (7 << 3);
		|		data |= 0x0140;
		|		macro_hic = false;
		|	} else if (PIN_U_PEND) {
		|		BUS_UEV_READ(data);
		|		data <<= 3;
		|		data |= 0x0180;
		|		u_event = false;
		|	} else {
		|		sel = 0;
		|		if (PIN_U_MUX_SEL) sel |= 4;
		|		if (PIN_G_SEL0) sel |= 2;
		|		if (PIN_G_SEL1) sel |= 1;
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			BUS_DEC_READ(data);
		|			data <<= 1;
		|			break;
		|		case 2:
		|			BUS_TOP_READ(data);
		|			break;
		|		case 3:
		|		case 4:
		|			BUS_CUR_READ(data);
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|	}
		|	if (PIN_Q1not.posedge()) {
		|
		|		uint8_t utrc[2];
		|		utrc[0] = UT_UADR;
		|		utrc[0] |= (data >> 8) & 0x3f;
		|		utrc[1] = data & 0xff;
		|		microtrace(utrc, sizeof utrc);
		|
		|		output.nu = data;
		|	}
		|
		|	output.macro_hic = macro_hic;
		|	output.u_event = !u_event;
		|	output.u_eventnot = u_event;
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XNXTUADR", PartModel("XNXTUADR", XNXTUADR))
