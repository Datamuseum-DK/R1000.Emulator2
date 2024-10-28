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

TYP drivers

IOP     CPURAM  RTC     CTR     CBBUF
--------------------------------------------- 
-       X       -       X       -       0-31
-       -       X       -       -       32-47
X       -       -       -       X       48-63
---------------------------------------------
0x05    -       0x05    0x05    -       XXX

-       -       0x08    0x08    0x8     XXX
-       -       0x09    0x09    0x9     XXX
-       -       0x19    0x19    0x19    XXX

-       0x16    0x16    -       0x16    XXX
-       0x1c    0x1c    -       0x1c    XXX
-       0x1d    0x1d    -       0x1d    XXX
---------------------------------------------

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
		|	
		|	unsigned rand;
		|	BUS_RAND_READ(rand);
		|	bool load_wdr = rand >> 5;
		|	rand &= 0x1f;
		|	output.r = 0;
		|	output.r |= state->pb010[rand] << 16;
		|	output.r |= state->pb011[rand] << 8;
		|	output.r |= state->pb012[rand] << 0;
		|	output.r &= 0x01f064;
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
		|	bool disable_ecc = ((state->pb011[rand] >> 0) & 1);
		|	output.decc = !(disable_ecc || output.memtv);
		|
		|	bool drive_other_cb = ((state->pb011[rand] >> 5) & 1);
		|	output.ncben = !(uir_load_wdr && drive_other_cb && output.memtv);
		|	if (!(output.r & 0x2000))
		|		output.ncben = false;
		|
		|	bool rcv_type = ((state->pb012[rand] >> 3) & 1);
		|	bool typpc = !(ldrst && rcv_type && output.memtv);
		|
		|	output.trcv = !(typpc && rddum);
		|
		|	bool read_rdr_t = ((state->pb013[rand] >> 6) & 1);
		|	output.dumvoe = output.ioctv;
		|	output.dumtoe = output.ioctv || read_rdr_t;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOC53", PartModel("XIOC53", XIOC53))
