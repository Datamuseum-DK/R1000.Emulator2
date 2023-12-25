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
   VAL FIU conditions 
   ==================

'''

from part import PartModel, PartFactory

class XVFCND(PartFactory):
    ''' VAL FIU conditions '''

    def state(self, file):
        file.fmt('''
		|	unsigned fcsel;
		|	bool fcond;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_FCSEL_WRITE(state->fcsel);
		|		PIN_FCOND<=(state->fcond);
		|	}
		|
		|	if (PIN_SNK=>) {
		|		if (state->fcsel == 7) {
		|			next_trigger(PIN_SNK.negedge_event());
		|		} else {
		|			state->fcsel = 7;
		|			state->ctx.job = 1;
		|			next_trigger(5, sc_core::SC_NS);
		|		}
		|		return;
		|	}
		|	unsigned sel;
		|	BUS_SEL_READ(sel);
		|	bool fcond = false;
		|
		|	unsigned fcsel = 0;
		|
		|	if (!(sel & 0x02))
		|		fcsel |= 0x4;
		|
		|	if ((sel & 0x2) && (PIN_BAD0=> ^ PIN_BBD0=>))
		|		fcsel |= 0x2;
		|
		|	if ((sel & 3) == 1)
		|		fcsel |= 0x2;
		|
		|	if (sel & 0x10)
		|		fcsel |= 0x1;
		|
		|	if ((sel & 0x06) == 0x06)
		|		fcsel |= 0x1;
		|
		|	unsigned zero = 0;
		|	switch (state->fcsel) {
		|	case 0:
		|		fcond = !PIN_ACO=>;
		|		break;
		|	case 1:
		|	case 3:
		|		fcond = PIN_LVAL=>;
		|		break;
		|	case 2:
		|		fcond = PIN_BBD0=>;
		|		break;
		|	case 4:
		|		BUS_AZ_READ(zero);
		|		fcond = (zero == 0xff);
		|		break;
		|	case 6:
		|		BUS_AZ_READ(zero);
		|		fcond = (zero != 0xff);
		|		break;
		|
		|	default:
		|		fcond = true;
		|		break;
		|	}
		|	fcond = !fcond;
		|
		|	if (fcsel != state->fcsel ||
		|	    fcond != state->fcond) {
		|		state->fcsel = fcsel;
		|		state->fcond = fcond;
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	} else if (sel & 0x2) {
		|		//next_trigger(b5_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVFCND", PartModel("XVFCND", XVFCND))
