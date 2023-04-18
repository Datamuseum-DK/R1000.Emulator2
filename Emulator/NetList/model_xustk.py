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
   Micro Stack
   ===========

'''

from part import PartModel, PartFactory

class XUSTK(PartFactory):
    ''' Micro Stack '''

    def state(self, file):
        file.fmt('''
		|	uint16_t topu;
		|''')

    def sensitive(self):
        #yield "PIN_WRITE"
        #yield "PIN_H2"
        #yield "PIN_Q2"
        #yield "BUS_SEL_SENSITIVE()"
        yield "PIN_TOSWE.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint16_t tmp;
		|	const char *what = "?";
		|
		|	if (PIN_TOSWE.posedge()) {
		|		if (PIN_H2 && !PIN_WRITE) {
		|			BUS_SEL_READ(tmp);
		|			switch(tmp) {
		|			case 0:
		|				BUS_BRNCH_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "0";
		|				break;
		|			case 1:
		|				BUS_FIU_READ(state->topu);
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "1";
		|				break;
		|			case 2:
		|				BUS_CURU_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "2";
		|				break;
		|			case 3:
		|				BUS_CURU_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (PIN_LATCHED) state->topu |= (1<<14);
		|				state->topu ^= BUS_TOPU_MASK;
		|				what = "3";
		|				break;
		|			}
		|		} else {
		|			what = "4";
		|			BUS_TOPS_READ(state->topu);
		|		}
		|		BUS_TOPU_WRITE(~state->topu);
		|	}
		|	TRACE(
		|		<< " w " << what
		|		<< " q2 " << PIN_Q2
		|		<< " h2 " << PIN_H2
		|		<< " wr " << PIN_WRITE
		|		<< " sel " << BUS_SEL_TRACE()
		|		<< " toswe^ " << PIN_TOSWE.posedge()
		|		<< " q3c " << PIN_Q3COND
		|		<< " lted " << PIN_LATCHED
		|		<< " curu " << BUS_CURU_TRACE()
		|		<< " fiu " << BUS_FIU_TRACE()
		|		<< " brnch " << BUS_BRNCH_TRACE()
		|		<< " a " << BUS_A_TRACE()
		|		<< " tops " << BUS_TOPS_TRACE()
		|	);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XUSTK", PartModel("XUSTK", XUSTK))
