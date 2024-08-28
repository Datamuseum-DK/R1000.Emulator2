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
   SEQ lex level
   =============

'''

from part import PartModel, PartFactory

class XSLEX(PartFactory):
    ''' SEQ lex-level '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t pa041[512];
		|	uint16_t lex_valid;
		|	uint16_t dns;
		|	uint16_t dra;
		|	uint16_t dlr;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pa041, sizeof state->pa041,
		|	    "PA041-01");
		|''')
        super().init(file)

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "BUS_RES"
        # yield "BUS_LRN"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned res;
		|	BUS_RES_READ(res);
		|
		|	unsigned adr;
		|
		|	if (PIN_Q4.posedge()) {
		|		uint16_t nv = 0;
		|		adr = ((state->lex_valid >> 12) & 0xf) << 5;
		|		adr |= state->dra << 3;
		|		adr |= ((state->dlr >> 2) & 1) << 2;
		|		adr |= ((state->dns >> 3) & 1) << 1;
		|		bool pm3 = !((state->dns & 0x7) && !(state->dlr & 1));
		|		adr |= pm3;
		|		nv |= (state->pa041[adr] >> 4) << 12;
		|
		|		adr = ((state->lex_valid >> 8) & 0xf) << 5;
		|		adr |= state->dra << 3;
		|		adr |= ((state->dlr >> 2) & 1) << 2;
		|		adr |= ((state->dns >> 2) & 1) << 1;
		|		bool pm2 = !((state->dns & 0x3) && !(state->dlr & 1));
		|		adr |= pm2;
		|		nv |= (state->pa041[adr] >> 4) << 8;
		|
		|		adr = ((state->lex_valid >> 4) & 0xf) << 5;
		|		adr |= state->dra << 3;
		|		adr |= ((state->dlr >> 2) & 1) << 2;
		|		adr |= ((state->dns >> 1) & 1) << 1;
		|		bool pm1 = !((state->dns & 0x1) && !(state->dlr & 1));
		|		adr |= pm1;
		|		nv |= (state->pa041[adr] >> 4) << 4;
		|
		|		adr = ((state->lex_valid >> 0) & 0xf) << 5;
		|		adr |= state->dra << 3;
		|		adr |= ((state->dlr >> 2) & 1) << 2;
		|		adr |= ((state->dns >> 0) & 1) << 1;
		|		adr |= (state->dlr >> 0) & 1;
		|		nv |= (state->pa041[adr] >> 4) << 0;
		|
		|		state->lex_valid = nv;
		|	}
		|
		|	if (PIN_SCLK.posedge()) {
		|		unsigned lex_random;
		|		BUS_LRN_READ(lex_random);
		|		state->dra = res & 3;
		|		state->dlr = lex_random;
		|		if (lex_random & 0x2) {
		|			state->dns = 0xf;
		|		} else {
		|			state->dns = 0xf ^ (0x8 >> (res >> 2));
		|		}
		|	}
		|
		|	uint16_t nv = 0;
		|	adr = ((state->lex_valid >> 12) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 3) & 1) << 1;
		|	bool pm3 = !((state->dns & 0x7) && !(state->dlr & 1));
		|	adr |= pm3;
		|	nv |= (state->pa041[adr] >> 4) << 12;
		|
		|	adr = ((state->lex_valid >> 8) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 2) & 1) << 1;
		|	bool pm2 = !((state->dns & 0x3) && !(state->dlr & 1));
		|	adr |= pm2;
		|	nv |= (state->pa041[adr] >> 4) << 8;
		|
		|	adr = ((state->lex_valid >> 4) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 1) & 1) << 1;
		|	bool pm1 = !((state->dns & 0x1) && !(state->dlr & 1));
		|	adr |= pm1;
		|	nv |= (state->pa041[adr] >> 4) << 4;
		|
		|	adr = ((state->lex_valid >> 0) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 0) & 1) << 1;
		|	adr |= (state->dlr >> 0) & 1;
		|	nv |= (state->pa041[adr] >> 4) << 0;
		|
		|	output.lxcn = !((nv >> (15 - res)) & 1);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSLEX", PartModel("XSLEX", XSLEX))
