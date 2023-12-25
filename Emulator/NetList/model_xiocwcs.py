#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   IOC WCS
   =======
'''


from part import PartModel, PartFactory
from node import Node
from net import Net
from pin import Pin

class XIOCWCS(PartFactory):

    ''' IOC WCS '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|	uint16_t tram[1<<11];
		|	unsigned ctr;
		|	unsigned uir;
		|	unsigned sr0, sr1;
		|	unsigned uadr;
		|	unsigned tracnt;
		|	bool dgo;
		|	bool csa_hit;
		|	bool dummy_en;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "PIN_DGADR"
        yield "PIN_WE.pos()"
        yield "BUS_UADR_SENSITIVE()"
        yield "PIN_WE.pos()"
        yield "PIN_TRRDD"
        yield "PIN_TRRDA"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_UIR_WRITE(state->uir);
		|		PIN_ODG0<=(state->uir & 0x0100);
		|		PIN_ODG1<=(state->uir & 0x0001);
		|
		|		unsigned par_w = state->uir;
		|		par_w = (par_w ^ (par_w >> 8)) & 0xff;
		|		par_w = (par_w ^ (par_w >> 4)) & 0x0f;
		|		par_w = (par_w ^ (par_w >> 2)) & 0x03;
		|		par_w = (par_w ^ (par_w >> 1)) & 0x01;
		|
		|		PIN_UDPERR<=(par_w == 0);
		|		PIN_DUMEN<=(state->dummy_en);
		|		PIN_CSAHIT<=(state->csa_hit);
		|	}
		|
		|	unsigned uadr;
		|
		|	if (PIN_DGADR=>) {
		|		BUS_UADR_READ(uadr);
		|	} else {
		|		uadr = state->ctr;
		|	}
		|
		|	bool uir_clk = false;
		|
		|	if (PIN_Q4.posedge()) {
		|		state->dummy_en = !(PIN_DGDUEN=> && PIN_DUMNXT=>);
		|		state->csa_hit = !(PIN_DGCSAH=> && PIN_ICSAH=>);
		|		if (PIN_TRAWR=>) {
		|			unsigned tmp = 0;
		|			if (PIN_CLKSTP=>)
		|				tmp |= 0x8000;
		|			if (state->csa_hit)
		|				tmp |= 0x4000;
		|			tmp |= (uadr & 0x3fff);
		|			state->tram[state->tracnt] = tmp;
		|		}
		|		if (!PIN_TRALD=>) {
		|			BUS_IDG_READ(state->tracnt);
		|			state->tracnt &= 0x7ff;
		|		} else 	if (PIN_TRAEN=>) {
		|			state->tracnt += 1;
		|			state->tracnt &= 0x7ff;
		|		}
		|
		|		if (!PIN_SFSTOP=> && !PIN_DGUCEN=>)
		|			uir_clk = true;
		|		if (!PIN_CTRCLR=>) {
		|			// Sync reset
		|			state->ctr = 0;
		|		} else if (PIN_CTRCNT=>) {
		|			// Hold
		|		} else if (PIN_CTRUP=>) {
		|			// Count Up
		|			state->ctr += 1;
		|		} else {
		|			// Count Down
		|			state->ctr += 0xffff;
		|		}
		|		state->ctr &= 0xffff;
		|
		|		state->ctx.job = 1;
		|		next_trigger(5, sc_core::SC_NS);
		|	}
		|
		|	uint32_t par_a, par_b;
		|
		|	par_a = uadr & 0xbf00;
		|	par_a = (par_a ^ (par_a >> 8)) & 0xff;
		|	par_a = (par_a ^ (par_a >> 4)) & 0x0f;
		|	par_a = (par_a ^ (par_a >> 2)) & 0x03;
		|	par_a = (par_a ^ (par_a >> 1)) & 0x01;
		|	par_b = uadr & 0x40ff;
		|	par_b = (par_b ^ (par_b >> 8)) & 0xff;
		|	par_b = (par_b ^ (par_b >> 4)) & 0x0f;
		|	par_b = (par_b ^ (par_b >> 2)) & 0x03;
		|	par_b = (par_b ^ (par_b >> 1)) & 0x01;
		|
		|	PIN_UAPERR<=(!par_a && !par_b);
		|
		|	TRACE(<< BUS_IDG_TRACE() << std::hex << " u " << state->uir);
		|
		|	if (uir_clk) {
		|		unsigned uirs, diag;
		|		BUS_UIRS_READ(uirs);
		|		BUS_IDG_READ(diag);
		|		switch (uirs & 0xc) {
		|		case 0x0:
		|			break;
		|		case 0x4:
		|			state->sr0 <<= 1;
		|			state->sr0 |= 1;
		|			break;
		|		case 0x8:
		|			state->sr0 >>= 1;
		|			if (diag & 0x8000)
		|				state->sr0 |= 0x80;
		|			else
		|				state->sr0 &= 0x7f;
		|			break;
		|		case 0xc:
		|			state->sr0 = state->ram[uadr & 0x3fff] >> 8;
		|			break;
		|		}
		|		state->sr0 &= 0xff;
		|
		|		switch (uirs & 0x3) {
		|		case 0x0:
		|			break;
		|		case 0x1:
		|			state->sr1 <<= 1;
		|			state->sr1 |= 1;
		|			break;
		|		case 0x2:
		|			state->sr1 >>= 1;
		|			if (diag & 0x4000)
		|				state->sr1 |= 0x80;
		|			else
		|				state->sr1 &= 0x7f;
		|			break;
		|		case 0x3:
		|			state->sr1 = state->ram[uadr & 0x3fff] & 0xff;
		|			break;
		|		}
		|		state->sr1 &= 0xff;
		|
		|		unsigned uir = (state->sr0 << 8) | state->sr1;
		|		assert(uir <= 0xffff);
		|
		|		state->uir = uir;
		|		state->uadr = uadr;
		|
		|		TRACE(
		|		    << BUS_IDG_TRACE()
		|		    << std::hex
		|		    << " u " << uirs
		|		    << " d " << diag
		|		    << " sr0 " << state->sr0
		|		    << " sr1 " << state->sr1
		|		);
		|	}
		|
		|	if (PIN_WE.posedge()) {
		|		state->ram[uadr & 0x3fff] = state->uir;
		|	}
		|	if (!PIN_TRRDD=>) {
		|		state->dgo = true;
		|		BUS_DGO_WRITE(state->tram[state->tracnt]);
		|	} else if (!PIN_TRRDA=>) {
		|		state->dgo = true;
		|		BUS_DGO_WRITE(state->tracnt | 0xb800);
		|	} else if (state->dgo) {
		|		state->dgo = false;
		|		BUS_DGO_Z();
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOCWCS", PartModel("XIOCWCS", XIOCWCS))
