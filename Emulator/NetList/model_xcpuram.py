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
   R1000 access to IOP RAM
   =======================

'''

from part import PartModel, PartFactory

class XCPURAM(PartFactory):
    ''' TYP A-side mux+latch '''

    def extra(self, file):
        file.include("Infra/vend.h")
        super().extra(file)

    def state(self, file):
        file.fmt('''
		|	uint8_t *ram;
		|	unsigned acnt;
		|	unsigned areg;
		|	unsigned rdata;
		|''')

    def sensitive(self):
        yield "PIN_SCLK.pos()"
        yield "PIN_OE"

    def init(self, file):

        super().init(file)

        file.fmt('''
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ram = (uint8_t*)(c1 + 1);
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		// BUS_A_WRITE(state->areg | state->acnt);
		|		PIN_OFLO<=(state->acnt == 0xfff);
		|	}
		|	if (!PIN_OE=>) {
		|		BUS_OTYP_WRITE(state->rdata);
		|	} else {
		|		BUS_OTYP_Z();
		|	}
		|	if (PIN_SCLK.posedge()) {
		|		if (!PIN_RD=>) {
		|			state->rdata =
		|			    vbe32dec(state->ram + ((state->areg | state->acnt) << 2));
		|			if (state->ctx.do_trace & 4) {
		|				sc_tracef(this->name(), "RD 0x%08x 0x%08x",
		|				    ((state->areg | state->acnt) << 2), state->rdata);
		|			}
		|		}
		|		if (PIN_WR=>) {
		|			// XXX: Missing check on DIAG.RAM_EN which is high only 15...115ns
		|			//bool dgena = PIN_DGENA=>;
		|			uint64_t typ;
		|			BUS_ITYP_READ(typ);
		|			uint32_t data = typ >> 32;
		|			if (state->ctx.do_trace & 2) {
		|				sc_tracef(this->name(), "WR 0x%08x 0x%08x",
		|				    ((state->areg | state->acnt) << 2), data);
		|			}
		|			vbe32enc(state->ram + ((state->areg | state->acnt) << 2), data);
		|		}
		|		if (!PIN_LDA=>) {
		|			uint64_t typ;
		|			BUS_ITYP_READ(typ);
		|			state->acnt = (typ >> 2) & 0x00fff;
		|			state->areg = (typ >> 2) & 0x1f000;
		|		} else if (PIN_INCA=>) {
		|			state->acnt += 1;
		|			state->acnt &= 0xfff;
		|		}
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|	TRACE(
		|	    << " clk^ " << PIN_SCLK.posedge()
		|	    << " oe " << PIN_OE?
		|	    << " inca " << PIN_INCA?
		|	    << " lda " << PIN_LDA?
		|	    << " oflo " << PIN_OFLO?
		|	    << " wr " << PIN_WR?
		|	    << " rd " << PIN_RD?
		|	    << std::hex
		|	    << " areg " << state->areg
		|	    << " acnt " << state->acnt
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCPURAM", PartModel("XCPURAM", XCPURAM))
