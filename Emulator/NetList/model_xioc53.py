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
   TYP A-side mux+latch
   ====================

'''

from part import PartModel, PartFactory

class XIOC53(PartFactory):
    ''' IOC pg 53 '''

    def state(self, file):
        file.fmt('''
		|	unsigned adrbs;
		|	unsigned fiubs;
		|	unsigned tvbs;
		|	unsigned fiu;
		|	bool dummy_en;
		|	bool csa_hit;
		|	bool diag_on;
		|	bool diag_off;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "BUS_UIR_SENSITIVE()"
        yield "PIN_DUMEN"
        yield "PIN_CSAHIT"
        yield "PIN_DIAGON"
        yield "PIN_DIAGOFF"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|
		|		unsigned adr = 1 << state->adrbs;
		|		adr ^= 0xf;
		|		BUS_ADR_WRITE(adr);
		|
		|		unsigned fiu = 1 << state->fiubs;
		|		fiu ^= 0xf;
		|		BUS_FIU_WRITE(fiu);
		|
		|		PIN_SEQTV<=(state->tvbs != 0x5);
		|		PIN_FIUV<=((state->tvbs & 0xd) != 0x1);
		|		PIN_FIUT<=((state->tvbs & 0x6) != 0x2);
		|		PIN_RDDUM<=!(state->dummy_en && (state->tvbs & 0xc) == 0xc);
		|		PIN_MEMTV<=!(
		|			((state->tvbs & 0xc) == 0xc) &&
		|			!state->dummy_en &&
		|			!state->csa_hit
		|		);
		|		PIN_MEMV<=((state->tvbs & 0xc) != 0x8);
		|
		|		PIN_IOCTV<=!(
		|			state->diag_on ||
		|			(
		|			    ((state->tvbs & 0xc) == 0xc) &&
		|			    state->dummy_en &&
		|			    !state->diag_off
		|			) ||
		|			(
		|			    (state->tvbs == 0x4) &&
		|			    !state->diag_off
		|			)
		|		);
		|
		|		PIN_VALV<=!(
		|			((state->tvbs & 0xd) == 0x0) ||
		|			(
		|			    ((state->tvbs & 0xc) == 0xc) &&
		|			    !state->dummy_en &&
		|			    state->csa_hit
		|			)
		|		);
		|
		|		PIN_TYPT<=!(
		|			((state->tvbs & 0x6) == 0x0) ||
		|			(
		|			    ((state->tvbs & 0xc) == 0xc) &&
		|			    !state->dummy_en &&
		|			    state->csa_hit
		|			)
		|		);
		|		return;
		|	}
		|	unsigned uir;
		|	BUS_UIR_READ(uir);
		|	unsigned adrbs = (uir >> 6) & 3;
		|	unsigned fiubs = (uir >> 4) & 3;
		|	unsigned tvbs = uir & 0xf;
		|	bool dummy_en = PIN_DUMEN=>;
		|	bool csa_hit = PIN_CSAHIT=>;
		|	bool diag_on = PIN_DIAGON=>;
		|	bool diag_off = PIN_DIAGOFF=>;
		|
		|	if (PIN_Q2.posedge() && adrbs != state->adrbs) {
		|		state->adrbs = adrbs;
		|		state->ctx.job = 1;
		|		next_trigger(15, sc_core::SC_NS);
		|	}
		|	if (fiubs != state->fiubs ||
		|	    tvbs != state->tvbs ||
		|	    dummy_en != state->dummy_en ||
		|	    csa_hit != state->csa_hit ||
		|	    diag_on != state->diag_on ||
		|	    diag_off != state->diag_off
		|	) {
		|		state->fiubs = fiubs;
		|		state->tvbs = tvbs;
		|		state->dummy_en = dummy_en;
		|		state->csa_hit = csa_hit;
		|		state->diag_on = diag_on;
		|		state->diag_off = diag_off;
		|		state->ctx.job = 1;
		|		next_trigger(20, sc_core::SC_NS);
		|	}
		|	
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOC53", PartModel("XIOC53", XIOC53))
