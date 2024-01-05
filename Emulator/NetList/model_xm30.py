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
   MEM32 page 30
   =============

'''

from part import PartModel, PartFactory

class XM30(PartFactory):
    ''' MEM32 page 30 '''

    def state(self, file):
        file.fmt('''
		|	bool awe, nameq, row_adr_oe, col_adr_oe, tag_write, ras, cas_a, cas_b;
		|	bool vpdr;
		|	bool vbdr;
		|	bool vadr;
		|	bool trdr;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (state->ctx.job & 1) {
		|		state->ctx.job &= ~1;
		|		PIN_AWE<=(state->awe);
		|		PIN_NMEQ<=(state->nameq);
		|		PIN_RAOE<=(state->row_adr_oe);
		|		PIN_CAOE<=(state->col_adr_oe);
		|		PIN_TAGW<=(state->tag_write);
		|		PIN_TRCE<=(state->trdr);
		|		PIN_VACE<=(state->vadr);
		|		PIN_VBCE<=(state->vbdr);
		|		PIN_VPCE<=(state->vpdr);
		|		if (state->ctx.job & 2)
		|			next_trigger(30, sc_core::SC_NS);
		|		return;
		|	}
		|	if (state->ctx.job & 2) {
		|		state->ctx.job &= ~2;
		|		PIN_RAS<=(state->ras);
		|		PIN_CASA<=(state->cas_a);
		|		PIN_CASB<=(state->cas_b);
		|		return;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		unsigned cmd;
		|		BUS_CMD_READ(cmd);
		|		bool h1 = PIN_H1=>;
		|		bool mcyc2 = PIN_MC=>;
		|		bool mcyc2_next = PIN_MCN=>;
		|		bool ahit = PIN_AHIT=>;
		|		bool bhit = PIN_BHIT=>;
		|		bool late_abort = PIN_LAB=>;
		|		bool d_dis_adr = PIN_DDA=>;
		|		bool set_b = PIN_SETB=>;
		|
		|		bool ras = !(
		|		    ((cmd == 0x9 || cmd == 0xb) && !mcyc2_next) ||
		|		    ((cmd == 0x9 || cmd == 0xb) && h1 && !mcyc2) ||
		|		    (cmd >= 0xc && !mcyc2_next) ||
		|		    (cmd >= 0xc && h1 && !mcyc2)
		|		);
		|		bool cas_a = !(
		|		    ((cmd == 0xc || cmd == 0xe) && !h1 && !mcyc2_next) ||
		|		    ((cmd == 0xd || cmd == 0xf) && h1 && !mcyc2 && !ahit && !late_abort)
		|		);
		|		bool cas_b = !(
		|		    ((cmd == 0xc || cmd == 0xe) && !h1 && !mcyc2_next) ||
		|		    ((cmd == 0xd || cmd == 0xf) && h1 && !mcyc2 && !bhit && !late_abort)
		|		);
		|		bool awe = !(((cmd & 0xd) == 0xd) && h1 && !mcyc2);
		|		bool nameq = !(cmd == 0x3);
		|		bool tag_write = (
		|		    ((cmd == 0xc || cmd == 0xd) && !h1 && !mcyc2_next && mcyc2) ||
		|		    (cmd == 0x7 && !h1 && !mcyc2_next && mcyc2) ||
		|		    (cmd == 0x2 && !h1 && !mcyc2_next && mcyc2) ||
		|		    (h1 && state->tag_write)
		|		);
		|		bool row_adr_oe = !(!h1 && mcyc2_next && !d_dis_adr);
		|		bool col_adr_oe = !(
		|		    (h1 && !d_dis_adr) ||
		|		    (!mcyc2_next && !d_dis_adr)
		|		);
		|
		|		if (
		|		    ras != state->ras ||
		|		    cas_a != state->cas_a ||
		|		    cas_b != state->cas_b
		|		) {
		|			state->ctx.job |= 2;
		|			state->ras = ras;
		|			state->cas_a = cas_a;
		|			state->cas_b = cas_b;
		|		}
		|
		|		bool trdr =
		|		    !(
		|		        (cmd == 0xc && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0xe && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x5 && !h1 )
		|		    );
		|		bool vadr =
		|		    !(
		|		        (cmd == 0xe && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x6 && !h1  && (!mcyc2_next) &&   set_b ) ||
		|		        (cmd == 0xc && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x5 && !h1 )
		|		    );
		|		bool vbdr =
		|		    !(
		|		        (cmd == 0xe && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x6 && !h1  && (!mcyc2_next) && (!set_b)) ||
		|		        (cmd == 0xc && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x5 && !h1 )
		|		    );
		|		bool vpdr =
		|		    !(
		|		        (cmd == 0x6 && !h1  && (!mcyc2_next)) ||
		|		        (cmd == 0x5 && !h1 )
		|		    );
		|
		|		if (
		|		    awe != state->awe ||
		|		    nameq != state->nameq ||
		|		    row_adr_oe != state->row_adr_oe ||
		|		    col_adr_oe != state->col_adr_oe ||
		|		    tag_write != state->tag_write ||
		|		    trdr != state->trdr ||
		|		    vadr != state->vadr ||
		|		    vbdr != state->vbdr ||
		|		    vpdr != state->vpdr
		|		) {
		|			state->ctx.job |= 1;
		|			state->awe = awe;
		|			state->nameq = nameq;
		|			state->row_adr_oe = row_adr_oe;
		|			state->col_adr_oe = col_adr_oe;
		|			state->tag_write = tag_write;
		|			state->trdr = trdr;
		|			state->vadr = vadr;
		|			state->vbdr = vbdr;
		|			state->vpdr = vpdr;
		|		}
		|		if (state->ctx.job & 1)
		|			next_trigger(5, sc_core::SC_NS);
		|		else if (state->ctx.job & 2)
		|			next_trigger(35, sc_core::SC_NS);
		|
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM30", PartModel("XM30", XM30))
