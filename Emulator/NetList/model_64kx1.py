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
   64Kx1 SRAM
   =========

'''


from part import PartModel, PartFactory

class SRAM64KX1(PartFactory):

    ''' 64Kx1 SRAM '''

    def extra(self, file):
        file.include("Infra/vend.h")
        super().extra(file)

    def state(self, file):
        file.fmt('''
		|	uint32_t *iopram;
		|	uint32_t mymask;
		|	bool parity;
		|''')

    def init(self, file):
        file.fmt('''
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	if (c1 == NULL)
		|		std::cerr << "IOP.iop_ram_space not found\\n";
		|	assert(c1 != NULL);
		|	state->iopram = (uint32_t*)(c1 + 1);
		|	const char *p = strchr(this->name(), 'M');
		|	assert(p != NULL);
		|	p++;
		|	if (p[0] == 'P') {
		|		state->parity = true;
		|		p++;
		|	}
		|	int nbr = atoi(p);
		|	if (state->parity) {
		|		if (nbr >= 10) {
		|			state->iopram += 0x10000;
		|			nbr %= 10;
		|		}
		|		state->mymask = 0xff << (24 - (8 * nbr));
		|	} else {
		|		if (nbr >= 100) {
		|			state->iopram += 0x10000;
		|			nbr %= 100;
		|		}
		|		state->mymask = 1U << (31 - nbr);
		|	}
		|	std::cout
		|		<< this->name()
		|		<< " "
		|		<< nbr
		|		<< " "
		|		<< std::hex
		|		<< state->mymask
		|		<< " "
		|		<< state->parity
		|		<< "\\n";
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0, data;
		|
		|	if (!PIN_CS=>) {
		|		BUS_A_READ(adr);
		|		adr ^= BUS_A_MASK;
		|		data = vbe32dec(state->iopram + adr);
		|		if (!PIN_WE=> && !state->parity) {
		|			if (PIN_D=>)
		|				data |= state->mymask;
		|			else
		|				data &= ~state->mymask;
		|			vbe32enc(state->iopram + adr, data);
		|		}
		|		TRACE(
		|		    << " a " << BUS_A_TRACE()
		|		    << " CS# " << PIN_CS?
		|		    << " WE# " << PIN_WE?
		|		    << " D " << PIN_D?
		|		    << " adr "
		|		    << std::hex << (adr << 2)
		|		    << " data "
		|		    << (data & state->mymask)
		|		);
		|		if (state->parity) {
		|			uint32_t par = data;
		|			par &= state->mymask;
		|			par ^= (par >> 16);
		|			par ^= (par >> 8);
		|			par ^= (par >> 4);
		|			par ^= (par >> 2);
		|			par ^= (par >> 1);
		|			PIN_Q<=(!(par & 1));
		|		} else if (data & state->mymask)
		|			PIN_Q<=(true);
		|		else
		|			PIN_Q<=(false);
		|	} else {
		|		PIN_Q = sc_dt::sc_logic_Z;
		|		next_trigger(PIN_CS.negedge_event());
		|	}
		|''')

class SRAM64KXN(PartFactory):

    ''' 64Kx1 SRAM '''

    def state(self, file):
        file.fmt('''
		|	uint16_t ram[1<<16];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|
		|	BUS_A_READ(adr);
		|	if (!PIN_CS=> && !PIN_WE=>)
		|		BUS_D_READ(state->ram[adr]);
		|    if(!PIN_CS=>)
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " CS# " << PIN_CS?
		|	    << " WE# " << PIN_WE?
		|	    << " D " << BUS_D_TRACE()
		|	    << " adr "
		|	    << std::hex << adr
		|	    << " data "
		|	    << state->ram[adr]
		|	);
		|	if (!PIN_CS=>) {
		|		BUS_Q_WRITE(state->ram[adr]);
		|	} else {
		|		BUS_Q_Z();
		|		next_trigger(PIN_CS.negedge_event());
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("64KX1", PartModel("64KX1", SRAM64KX1))
