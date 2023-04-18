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
   2Kx8 SRAM
   =========

'''


from part import PartModel, PartFactory

class SRAM2KX8(PartFactory):

    ''' 2Kx8 SRAM '''

    def state(self, file):
        file.fmt('''
		|	uint16_t ram[1<<11];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|	unsigned data = 0;
		|
		|#if 0
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " d " << BUS_IO_TRACE()
		|	    << " cs " << PIN_CS?
		|	    << " oe " << PIN_OE?
		|	    << " we " << PIN_WE?
		|	);
		|#endif
		|
		|	if (PIN_CS=> || PIN_OE=> || !PIN_WE=>) {
		|		BUS_IO_Z();
		|	}
		|
		|	BUS_A_READ(adr);
		|
		|	if (!PIN_CS=> && PIN_WE.posedge()) {
		|		BUS_IO_READ(data);
		|		state->ram[adr] = data;
		|		TRACE(<< " write " << std::hex << adr << " " << std::hex << data);
		|	} else if (!PIN_CS=> && PIN_WE=> && !PIN_OE=>) {
		|		data = state->ram[adr];
		|		BUS_IO_WRITE(data);
		|		TRACE(<< " read " << std::hex << adr << " " << std::hex << data);
		|''')

        if not self.comp["CS"].net.is_const():
            file.fmt('''
		|	} else if (PIN_CS=>) {
		|		next_trigger(PIN_CS.negedge_event());
		|''')

        file.fmt('''
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("2KX8", PartModel("2KX8", SRAM2KX8))
    part_lib.add_part("2KX16", PartModel("2KX16", SRAM2KX8))
