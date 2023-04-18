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
   Dualport 256x16 SRAM
   ====================

'''


from part import PartModel, PartFactory

class FIFORAM(PartFactory):

    ''' Dualport 256x16 SRAM'''

    def state(self, file):
        file.fmt('''
		|	uint16_t ram[1<<BUS_AR_WIDTH];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned wadr, radr;
		|	unsigned data;
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
		|	BUS_AW_READ(wadr);
		|	BUS_AR_READ(radr);
		|
		|	if (PIN_WE.posedge()) {
		|		BUS_I_READ(data);
		|		state->ram[wadr] = data;
		|		TRACE(<< " write " << std::hex << wadr << " " << std::hex << data);
		|	}
		|	data = state->ram[radr];
		|	BUS_Y_WRITE(data);
		|	TRACE(<< " read " << std::hex << radr << " " << std::hex << data);
		|
		|	PIN_EQ<=(radr != wadr);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("FIFORAM", PartModel("FIFORAM", FIFORAM))
