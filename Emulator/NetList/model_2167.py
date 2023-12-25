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
   2167 CMOS Static RAM 16K x 1-Bit
   ================================

   Ref: Rensas DSC2981/08 February 2001
'''


from part import PartModel, PartFactory

class SRAM2167(PartFactory):

    ''' 2167 CMOS Static RAM 16K x 1-Bit '''

    def state(self, file):
        file.fmt('''
		|	bool ram[16384];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        if not self.comp.nodes["CS"].net.is_pd():
            file.fmt('''
		|	if (PIN_CS=>) {
		|		TRACE("Z");
		|		PIN_Q = sc_dt::sc_logic_Z;
		|		next_trigger(PIN_CS.negedge_event());
		|		return;
		|	}
		|''')

        file.fmt('''
		|	unsigned adr = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (!PIN_WE=>)
		|		state->ram[adr] = PIN_D=>;
		|	PIN_Q<=(state->ram[adr]);
		|
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " d "
		|	    << PIN_D?
		|	    << " w "
		|	    << PIN_WE?
		|	    << " cs "
		|	    << PIN_CS?
		|	    << " | "
		|	    << std::hex << adr
		|	    << " "
		|	    << state->ram[adr]
		|	);
		|''')

class Model2167(PartModel):
    ''' Fix Q pin to be tri-state '''

    def assign(self, comp, part_lib):
        if comp.nodes["CS"].net.is_pd():
            comp.nodes["Q"].pin.set_role("output")
        super().assign(comp, part_lib)


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("2167", Model2167("2167", SRAM2167))
