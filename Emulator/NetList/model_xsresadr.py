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
   SEQ Resolve address
   ====================

'''

from part import PartModel, PartFactory

class XSRESADR(PartFactory):
    ''' SEQ Resolve address '''

    def state(self, file):
        file.fmt('''
		|	unsigned curr_lex;
		|''')

    def xxsensitive(self):
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
		|	unsigned val, iclex;
		|
		|	BUS_VAL_READ(val);
		|	iclex = (val & 0xf) + 1;
		|
		|	if (PIN_CLCLK.posedge()) {
		|		state->curr_lex = val & 0xf;
		|		state->curr_lex ^= 0xf;
		|		BUS_CLEX_WRITE(state->curr_lex);
		|	}
		|	unsigned sel, res_addr = 0;
		|	BUS_RASEL_READ(sel);
		|	switch (sel) {
		|	case 0:
		|		if (PIN_LAUIR0=> && PIN_LAUIR1=>)
		|			res_addr = 0xe;
		|		else
		|			res_addr = 0xf;
		|		break;
		|	case 1:
		|		unsigned disp;
		|		BUS_DISP_READ(disp);
		|		res_addr = (disp >> 9) & 0xf;
		|		break;
		|	case 2:
		|		res_addr = iclex;
		|		break;
		|	case 3:
		|		res_addr = state->curr_lex ^ 0xf;
		|		break;
		|	default:
		|		assert(sel < 4);
		|	}
		|	BUS_RADR_WRITE(res_addr);
		|	if (PIN_LINC=>) {
		|		PIN_ICOND<=(true);
		|		PIN_SEXT<=(true);
		|	} else {
		|		PIN_ICOND<=(!(res_addr == 0xf));
		|		PIN_SEXT<=!((res_addr > 0xd));
		|	}		

		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSRESADR", PartModel("XSRESADR", XSRESADR))
