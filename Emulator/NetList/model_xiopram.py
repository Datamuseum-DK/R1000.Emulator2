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
   IOP RAM
   =======

'''


from part import PartModel, PartFactory

class XIOPRAM(PartFactory):

    ''' IOP RAM '''

    def extra(self, file):
        file.include("Infra/vend.h")
        super().extra(file)

    def state(self, file):
        file.fmt('''
		|	uint8_t *ram;
		|''')

    def sensitive(self):
        yield "PIN_CS"
        yield "BUS_WE_SENSITIVE()"

    def init(self, file):

        super().init(file)

        file.fmt('''
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ram = (uint8_t*)(c1 + 1);
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint32_t adr, data, we, tmp;
		|
		|	BUS_A_READ(adr);
		|	BUS_WE_READ(we);
		|	data = vbe32dec(state->ram + (adr << 2));
		|
		|	if (PIN_CS=>) {
		|		// TRACE(<<"Z");
		|		//next_trigger(PIN_CS.negedge_event());
		|	} else if (we == BUS_WE_MASK) {
		|		if (BUS_Q_WIDTH == 4) {
		|			tmp = (data ^ (data >> 4)) & 0x0f0f0f0f;
		|			tmp = (tmp ^ (tmp >> 2)) & 0x03030303;
		|			tmp = (tmp ^ (tmp >> 1)) & 0x01010101;
		|			tmp ^= 0x01010101;
		|			data = 0;
		|			if (tmp & 0x1) data |= 0x1;
		|			if (tmp & 0x100) data |= 0x2;
		|			if (tmp & 0x10000) data |= 0x4;
		|			if (tmp & 0x1000000) data |= 0x8;
		|		}
		|		TRACE(
		|		    << " R "
		|		    << " a " << BUS_A_TRACE()
		|		    << " we " << BUS_WE_TRACE()
		|		    << " cs " << PIN_CS?
		|		    << " adr " << std::hex << (adr << 2)
		|		    << " data " << std::hex << data
		|		);
		|		BUS_Q_WRITE(data);
		|	} else {
		|		BUS_D_READ(data);
		|		TRACE(
		|		    << " W"
		|		    << " a " << BUS_A_TRACE()
		|		    << " d " << BUS_D_TRACE()
		|		    << " we " << BUS_WE_TRACE()
		|		    << " cs " << PIN_CS?
		|		    << " adr " << std::hex << (adr << 2)
		|		    << " data " << std::hex << data
		|		);
		|		if (BUS_Q_WIDTH == 32)
		|			vbe32enc(state->ram + (adr << 2), data);
		|		BUS_Q_WRITE(data);
		|	}
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOPRAM4", PartModel("XIOPRAM4", XIOPRAM))
    part_lib.add_part("XIOPRAM32", PartModel("XIOPRAM32", XIOPRAM))
