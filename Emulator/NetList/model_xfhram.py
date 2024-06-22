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
   FIU Hash RAM 
   ============

'''

from part import PartModel, PartFactory

class XFHRAM(PartFactory):
    ''' FIU Hash RAM '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint8_t ramhi[1<<10];
		|	uint8_t ramlo[1<<10];
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_WE",
            "PIN_OE",
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned q = 0, ahi=0, alo=0, spc, nam, off;
		|	BUS_SPC_READ(spc);
		|	BUS_NAM_READ(nam);
		|	BUS_OFF_READ(off);
		|
		|#define BITSPC(n) ((spc >> BUS_SPC_LSB(n)) & 1)
		|#define BITNAM(n) ((nam >> BUS_NAM_LSB(n)) & 1)
		|#define BITOFF(n) ((off >> BUS_OFF_LSB(n)) & 1)
		|
		|	ahi |= BITNAM(14) << 9;
		|	ahi |= BITNAM(15) << 8;
		|	ahi |= BITNAM(16) << 7;
		|	ahi |= BITNAM(17) << 6;
		|	ahi |= BITOFF( 9) << 5;
		|	ahi |= BITOFF(10) << 4;
		|	ahi |= BITOFF(11) << 3;
		|	ahi |= BITOFF( 7) << 2;
		|	ahi |= BITOFF(17) << 1;
		|	ahi |= BITOFF(18) << 0;
		|
		|	alo |= BITNAM(18) << 9;
		|	alo |= BITNAM(19) << 8;
		|	alo |= BITNAM(20) << 7;
		|	alo |= BITNAM(21) << 6;
		|	alo |= BITOFF(10) << 5;
		|	alo |= BITOFF(11) << 4;
		|	alo |= BITOFF(12) << 3;
		|	alo |= BITOFF(13) << 2;
		|	alo |= BITOFF(14) << 1;
		|	alo |= BITOFF(15) << 0;
		|
		|	if (PIN_WE.posedge()) {
		|		unsigned data;
		|		BUS_D_READ(data);
		|
		|		state->ramhi[ahi] = (data >> 14) & 0xf;
		|		state->ramlo[alo] = (data >> 10) & 0xf;
		|		
		|	}
		|
		|	if (!PIN_BIG=>) {
		|		q |= (BITSPC(1) ^ BITNAM(12) ^ BITOFF(17)) << (11- 0);
		|	}
		|	q |= (BITOFF(8) ^ BITNAM(13)) << (11- 1);
		|	q |= (BITSPC(0) ^ BITOFF(18)) << (11-10);
		|	q |= (BITSPC(2) ^ BITOFF(16)) << (11-11);
		|	q |= state->ramhi[ahi] << 6;
		|	q |= state->ramlo[alo] << 2;
		|	q ^= 0xff << 2;
		|	output.q = q;
		|	if (PIN_OE=>)
		|		idle_next = &idle_event;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFHRAM", PartModel("XFHRAM", XFHRAM))
