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
		|	uint16_t tram[1<<11];	// Z023
		|	unsigned tracnt;	// Z023
		|	uint64_t *ram;
		|	unsigned sr0, sr1;
		|	unsigned aen;
		|''')

    def init(self, file):
        file.fmt('''
		|	state->ram = (uint64_t*)CTX_GetRaw("IOC_WCS", sizeof(uint64_t) << 14);
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q4_pos = PIN_Q4.posedge();
		|
		|	if (q4_pos) {
		|		unsigned uadr;
		|		BUS_UADR_READ(uadr);
		|		output.dumen = !PIN_DUMNXT=>;
		|		bool csa_hit = !PIN_ICSAH=>;
		|
		|		unsigned tmp = 0;
		|		if (PIN_CLKSTP=>)
		|			tmp |= 0x8000;
		|		if (csa_hit)
		|			tmp |= 0x4000;
		|		tmp |= uadr & 0x3fff;
		|		state->tram[state->tracnt] = tmp;
		|
		|		if (PIN_TRAEN=>) {
		|			state->tracnt += 1;
		|			state->tracnt &= 0x7ff;
		|		}
		|
		|		if (!PIN_SFSTOP=>) {
		|			state->sr0 = state->ram[uadr] >> 8;
		|			state->sr0 &= 0xff;
		|			state->sr1 = state->ram[uadr] & 0xff;
		|			state->sr1 &= 0xff;
		|
		|			unsigned uir = (state->sr0 << 8) | state->sr1;
		|			assert(uir <= 0xffff);
		|
		|			output.uir = uir;
		|
		|			state->aen = (uir >> 6) & 3;
		|
		|			unsigned fen = (uir >> 4) & 3;
		|			output.fen = (1 << fen) ^ 0xf;
		|			output.aen = (1 << state->aen) ^ 0xf;
		|
		|			unsigned tvbs = uir & 0xf;
		|
		|			output.seqtv = true;
		|			output.fiuv = true;
		|			output.fiut = true;
		|			output.memv = true;
		|			output.memtv = true;
		|			output.ioctv = true;
		|			output.valv = true;
		|			output.typt = true;
		|			switch (tvbs) {
		|			case 0x0: output.valv = false; output.typt = false; break;
		|			case 0x1: output.fiuv = false; output.typt = false; break;
		|			case 0x2: output.valv = false; output.fiut = false; break;
		|			case 0x3: output.fiuv = false; output.fiut = false; break;
		|			case 0x4: output.ioctv = false; break;
		|			case 0x5: output.seqtv = false; break;
		|			case 0x8:
		|			case 0x9:
		|				output.memv = false; output.typt = false; break;
		|			case 0xa:
		|			case 0xb:
		|				output.memv = false; output.fiut = false; break;
		|			case 0xc:
		|			case 0xd:
		|			case 0xe:
		|			case 0xf:
		|				if (output.dumen) {
		|					output.ioctv = false;
		|				} else if (csa_hit) {
		|					output.typt = false;
		|					output.valv = false;
		|				} else {
		|					output.memtv = false;
		|					output.memv = false;
		|				}
		|				break;
		|			default:
		|				break;
		|			}
		|		}
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOCWCS", PartModel("XIOCWCS", XIOCWCS))
