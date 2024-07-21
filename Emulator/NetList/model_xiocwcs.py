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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<14];
		|	uint16_t tram[1<<11];
		|	unsigned ctr;
		|	unsigned uir;
		|	unsigned sr0, sr1;
		|	unsigned tracnt;
		|	bool csa_hit;
		|	bool dummy_en;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "PIN_DGADR"
        yield "BUS_UADR_SENSITIVE()"
        yield "PIN_TRRDD"
        yield "PIN_TRRDA"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned uadr;
		|
		|	if (PIN_DGADR=>) {
		|		BUS_UADR_READ(uadr);
		|	} else {
		|		uadr = state->ctr & BUS_UADR_MASK;
		|	}
		|
		|	bool uir_clk = false;
		|
		|	if (PIN_Q4.posedge()) {
		|		state->dummy_en = !(PIN_DGDUEN=> && PIN_DUMNXT=>);
		|		output.dumen = state->dummy_en;
		|		state->csa_hit = !(PIN_DGCSAH=> && PIN_ICSAH=>);
		|		output.csahit = state->csa_hit;
		|		if (PIN_TRAWR=>) {
		|			unsigned tmp = 0;
		|			if (PIN_CLKSTP=>)
		|				tmp |= 0x8000;
		|			if (state->csa_hit)
		|				tmp |= 0x4000;
		|			tmp |= uadr & 0x3fff;
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
		|		} else {
		|			// Count Down
		|			state->ctr += 0xffff;
		|		}
		|		state->ctr &= 0xffff;
		|
		|	}
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
		|			state->sr0 = state->ram[uadr] >> 8;
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
		|			state->sr1 = state->ram[uadr] & 0xff;
		|			break;
		|		}
		|		state->sr1 &= 0xff;
		|
		|		unsigned uir = (state->sr0 << 8) | state->sr1;
		|		assert(uir <= 0xffff);
		|
		|		state->uir = uir;
		|		output.uir = state->uir;
		|		output.odg = state->uir & 0x0001;
		|		output.odg |= (state->uir >>7) & 0x0002;
		|
		|		unsigned aen = (uir >> 6) & 3;
		|		output.aen = (1 << aen) ^ 0xf;
		|
		|		unsigned fen = (uir >> 4) & 3;
		|		output.fen = (1 << fen) ^ 0xf;
		|	}
		|
		|	if (!PIN_TRRDD=>) {
		|		output.z_dgo = false;
		|		output.dgo = state->tram[state->tracnt];
		|	} else if (!PIN_TRRDA=>) {
		|		output.z_dgo = false;
		|		output.dgo = state->tracnt | 0xb800;
		|	} else {
		|		output.z_dgo = true;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOCWCS", PartModel("XIOCWCS", XIOCWCS))
