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
   128x4 NOVRAM
   ============

'''

from part import PartModel, PartFactory

class NOVRAM(PartFactory):

    ''' 128x4 NOVRAM '''

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint8_t perm[256];\n")
        file.write("\tuint8_t ram[256];\n")
        file.write("\tbool writing;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	memset(state->ram, 0, sizeof state->ram);
		|	int i, j;
		|	should_i_trace(this->name(), &state->ctx.do_trace);
		|
		|	if (strstr(this->name(), "FIU")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_FIU_NOVRAM");
		|	} else if (strstr(this->name(), "VAL")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_VAL_NOVRAM");
		|	} else if (strstr(this->name(), "TYP")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_TYP_NOVRAM");
		|	} else if (strstr(this->name(), "SEQ")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_SEQ_NOVRAM");
		|	} else if (strstr(this->name(), "MEM0")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_MEM0_NOVRAM");
		|	} else if (strstr(this->name(), "MEM2")) {
		|		load_programmable(arg, state->perm, sizeof state->perm,
		|		    "R1000_MEM2_NOVRAM");
		|	} else {
		|		unsigned part, serial, artwork, eco, year, month, day, tstamp;
		|
		|		part = 99; serial = 9999; artwork = 99; eco = 99;
		|		year = 1998; month = 9; day = 9;
		|
		|		state->perm[0x01] = (part >> 4) & 0xf;
		|		state->perm[0x02] = part & 0xf;
		|
		|		state->perm[0x03] = (serial >> 12) & 0xf;
		|		state->perm[0x04] = (serial >> 8) & 0xf;
		|		state->perm[0x05] = (serial >> 4) & 0xf;
		|		state->perm[0x06] = serial & 0xf;
		|
		|		state->perm[0x07] = (artwork >> 4) & 0xf;
		|		state->perm[0x08] = artwork & 0xf;
		|
		|		state->perm[0x09] = (eco >> 4) & 0xf;
		|		state->perm[0x0a] = eco & 0xf;
		|
		|		tstamp = (year - 1901) << 9;
		|		tstamp |= month << 5;
		|		tstamp |= day;
		|
		|		state->perm[0x0b] = (tstamp >> 12) & 0xf;
		|		state->perm[0x0c] = (tstamp >> 8) & 0xf;
		|		state->perm[0x0d] = (tstamp >> 4) & 0xf;
		|		state->perm[0x0e] = tstamp & 0xf;
		|
		|		j = 0x56;
		|		for (i = 1; i < 0x0f; i += 2) {
		|			j += state->perm[i] << 4;
		|			j += state->perm[i + 1];
		|		}
		|		j = ~j;
		|		j += 1;
		|		j &= 0xff;
		|		printf("NOVRAM CHECKSUM1 0x%x\\n", j);
		|		state->perm[0x0f] = (j >> 4) & 0xf;
		|		state->perm[0x10] = j & 0xf;
		|	}
		|
		|	// READ_NOVRAM.FIU expects zero byte XOR checksum.
		|	// We dont know which location is for adjustment, use last two.
		|	j = 0xaa;
		|	for (i = 0; i < 254; i += 2)
		|		j ^= ((state->perm[i] << 4) | state->perm[i + 1]);
		|	j &= 0xff;
		|	state->perm[0xfe] = (j >> 4 & 0xf);
		|	state->perm[0xff] = j & 0xf;
		|	memcpy(state->ram, state->perm, sizeof state->ram);
		|''')


    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned adr = 0, data = 0;
		|
		|
		|	if (!PIN_RECALL=>) {
		|		TRACE("RCL");
		|		BUS_DQ_Z();
		|		memcpy(state->ram, state->perm, sizeof state->ram);
		|		next_trigger(PIN_RECALL.default_event());
		|		state->writing = false;
		|		return;
		|	}
		|
		|	BUS_A_READ(adr);
		|
		|	if (state->writing) {
		|		BUS_DQ_READ(data);
		|		state->ram[adr] = data;
		|	}
		|
		|	if (PIN_CS=>) {
		|		BUS_DQ_Z();
		|		next_trigger(PIN_CS.negedge_event() | PIN_RECALL.negedge_event());
		|		if (state->writing)
		|			TRACE("ZW");
		|		else
		|			TRACE("Z");
		|		state->writing = false;
		|		return;
		|	}
		|
		|	if (!PIN_WE=> && PIN_STORE=> && PIN_RECALL=>) {
		|		BUS_DQ_Z();
		|		BUS_DQ_READ(data);
		|		state->ram[adr] = data;
		|		state->writing = true;
		|	} else {
		|		data = state->ram[adr];
		|		BUS_DQ_WRITE(data);
		|		state->writing = false;
		|	}
		|	TRACE(
		|	    << " cs_ " <<PIN_CS?
		|	    << " store_" <<PIN_STORE?
		|	    << " recall_ " <<PIN_RECALL?
		|	    << " we_ " <<PIN_WE?
		|	    << " a " << BUS_A_TRACE()
		|	    << " dq " <<BUS_DQ_TRACE()
		|	    << " A " << std::hex << adr
		|	    << " D " << std::hex << data
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("NOVRAM", PartModel("NOVRAM", NOVRAM))
