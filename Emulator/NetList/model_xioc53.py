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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t pb010[32];
		|	uint8_t pb011[32];
		|	uint8_t pb012[32];
		|	uint8_t pb013[32];
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pb010, sizeof state->pb010,
		|	    "PB010");
		|	load_programmable(this->name(),
		|	    state->pb011, sizeof state->pb011,
		|	    "PB011");
		|	load_programmable(this->name(),
		|	    state->pb012, sizeof state->pb012,
		|	    "PB012");
		|	load_programmable(this->name(),
		|	    state->pb013, sizeof state->pb013,
		|	    "PB013");
		|''')
        super().init(file)

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned tvbs;
		|	BUS_TVBS_READ(tvbs);
		|
		|	output.seqtv = true;
		|	output.fiuv = true;
		|	output.fiut = true;
		|	bool rddum = true;
		|	output.memv = true;
		|	output.memtv = true;
		|	output.ioctv = true;
		|	output.valv = true;
		|	output.typt = true;
		|	switch (tvbs) {
		|	case 0x0: output.valv = false; output.typt = false; break;
		|	case 0x1: output.fiuv = false; output.typt = false; break;
		|	case 0x2: output.valv = false; output.fiut = false; break;
		|	case 0x3: output.fiuv = false; output.fiut = false; break;
		|	case 0x4: output.ioctv = false; break;
		|	case 0x5: output.seqtv = false; break;
		|	case 0x8:
		|	case 0x9:
		|		output.memv = false; output.typt = false; break;
		|	case 0xa:
		|	case 0xb:
		|		output.memv = false; output.fiut = false; break;
		|	case 0xc:
		|	case 0xd:
		|	case 0xe:
		|	case 0xf:
		|		if (PIN_DUMEN=>) {
		|			rddum = false;
		|			output.ioctv = false;
		|		} else if (PIN_CSAHIT=>) {
		|			output.typt = false;
		|			output.valv = false;
		|		} else {
		|			output.memtv = false;
		|		}
		|		break;
		|	default:
		|		break;
		|	}
		|	if (PIN_DIAGON=>)
		|		output.ioctv = false;
		|	else if (PIN_DIAGOFF=>)
		|		output.ioctv = true;
		|	
		|	unsigned rand;
		|	BUS_RAND_READ(rand);
		|	bool load_wdr = rand >> 5;
		|	rand &= 0x1f;
		|	output.r = 0;
		|	output.r |= state->pb010[rand] << 20;
		|	output.r |= state->pb011[rand] << 12;
		|	output.r |= state->pb012[rand] << 4;
		|	output.r |= state->pb013[rand] >> 4;
		|
		|	bool uir_load_wdr = !(load_wdr || PIN_DIAGLW=>);
		|
		|	output.ldwdr = !(uir_load_wdr && PIN_SCLKST=>);
		|
		|	bool rstrdr = PIN_RSTRDR=>;
		|	bool ldrst = !(uir_load_wdr || !rstrdr);
		|
		|	output.lddum = !(rddum && !rstrdr);
		|
		|	bool disable_ecc = (output.r >> (27-15)) & 1;
		|	output.decc = !(disable_ecc || output.memtv);
		|
		|	bool drive_other_cb = (output.r >> (27-10)) & 1;
		|	output.ncben = !(uir_load_wdr && drive_other_cb && output.memtv);
		|
		|	output.ipard = output.memtv && output.ioctv;
		|
		|	bool norcv = !(PIN_DIAGDR=> || !rddum);
		|
		|	bool rcv_type = (output.r >> (27-20)) & 1;
		|	output.typpc = !(ldrst && rcv_type && output.memtv);
		|	output.valpc = !(ldrst && output.memtv);
		|
		|	output.trcv = !(output.typpc && norcv);
		|	output.vrcv = !(output.valpc && norcv);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOC53", PartModel("XIOC53", XIOC53))
