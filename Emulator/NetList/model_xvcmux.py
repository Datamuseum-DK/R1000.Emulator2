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
   VAL C-bus mux
   =============

'''

from part import PartModel, PartFactory

class XVCMUX(PartFactory):
    ''' VAL C-bus mux '''

    def state(self, file):
 
        file.fmt('''
		|	uint64_t c;
		|	bool con;
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
		|
		|	if (state->ctx.job) {
		|		if (state->con)
		|			BUS_C_WRITE(state->c);
		|		else
		|			BUS_C_Z();
		|		state->ctx.job = 0;
		|	}
		|	uint64_t c = 0;
		|	uint64_t fiu = 0, alu = 0, wdr = 0;
		|	bool fiu_valid = false, alu_valid = false, wdr_valid = false;
		|	bool sel = PIN_SEL10=>;
		|	bool chi = false;
		|	bool clo = false;
		|
		|	if (PIN_OE=>) {
		|		BUS_C_Z();
		|		if (state->con) {
		|			state->con = false;
		|			next_trigger(5, SC_NS);
		|			return;
		|		}
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|
		|	if (!PIN_FOE0=>) {
		|		BUS_FIU_READ(fiu);
		|		fiu ^= BUS_FIU_MASK;
		|		fiu_valid = true;
		|		c |= fiu & 0xffffffff00000000ULL;
		|		chi = true;
		|	} else if (!PIN_OE00=>) {
		|		BUS_ALU_READ(alu);
		|		alu_valid = true;
		|		if (sel) {
		|			c |= (alu >> 16) & 0xffffffff00000000ULL;
		|			c |= 0xffff000000000000ULL;
		|		} else {
		|			c |= (alu << 1) & 0xffffffff00000000ULL;
		|		}
		|		chi = true;
		|	} else if (!PIN_OE01=>) {
		|		if (sel) {
		|			BUS_WDR_READ(wdr);
		|			wdr_valid = true;
		|			c |= wdr & 0xffffffff00000000ULL;
		|		} else {
		|			BUS_ALU_READ(alu);
		|			alu_valid = true;
		|			c |= alu & 0xffffffff00000000ULL;
		|		}
		|		chi = true;
		|	}
		|	if (!PIN_FOE1=>) {
		|		if (!fiu_valid) {
		|			BUS_FIU_READ(fiu);
		|			fiu ^= BUS_FIU_MASK;
		|		}
		|		c |= fiu & 0xfffffffeULL;
		|		unsigned csel;
		|		BUS_CSEL_READ(csel);
		|		if (csel == 7) {
		|			c |= fiu & 0x1ULL;
		|		} else {
		|			unsigned cond = PIN_COND=>;
		|			c |= cond & 1;
		|		}
		|		clo = true;
		|	} else if (!PIN_OE10=>) {
		|		if (!alu_valid)
		|			BUS_ALU_READ(alu);
		|		if (sel) {
		|			c |= (alu >> 16) & 0xffffffffULL;
		|		} else {
		|			c |= (alu << 1) & 0xffffffffULL;
		|			c |= 1;
		|		}
		|		clo = true;
		|	} else if (!PIN_OE11=>) {
		|		if (sel) {
		|			if (!wdr_valid)
		|				BUS_WDR_READ(wdr);
		|			c |= wdr & 0xffffffffULL;
		|		} else {
		|			if (!alu_valid)
		|				BUS_ALU_READ(alu);
		|			c |= alu & 0xffffffffULL;
		|		}
		|		clo = true;
		|	}
		|	if (chi && !clo)
		|		c |= 0xffffffff;
		|	if (!chi && clo)
		|		c |= 0xffffffffULL << 32;
		|	bool con = chi | clo;
		|	con = true;
		|#if 1
		|	if (con != state->con || c != state->c) {
		|		state->ctx.job = 1;
		|		state->con = con;
		|		state->c = c;
		|		next_trigger(5, SC_NS);
		|	}
		|#else
		|	if (con) {
		|		BUS_C_WRITE(c);
		|	} else {
		|		BUS_C_Z();
		|	}
		|#endif
		|	TRACE(
		|	    << " sel10 " << PIN_SEL10?
		|	    << " oe00 " << PIN_OE00?
		|	    << " oe01 " << PIN_OE01?
		|	    << " oe10 " << PIN_OE10?
		|	    << " oe11 " << PIN_OE11?
		|	    << " foe0 " << PIN_FOE0?
		|	    << " foe1 " << PIN_FOE1?
		|	    << " fiu " << BUS_FIU_TRACE()
		|	    << " wdr " << BUS_WDR_TRACE()
		|	    << " alu " << BUS_ALU_TRACE()
		|	    << " con " << con
		|	    << " c " << std::hex << c
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVCMUX", PartModel("XVCMUX", XVCMUX))
