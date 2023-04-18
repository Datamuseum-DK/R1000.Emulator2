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
   F189 64-Bit Random Acess Memory with 3-STATE Outputs
   ====================================================

   Ref: Fairchild DS009493 April 1988 Revised January 2004
'''


from part import PartModel, PartFactory

class F189(PartFactory):

    ''' F189 64-Bit Random Acess Memory with 3-STATE Outputs '''

    def state(self, file):
        file.fmt('''
		|	unsigned ram[16];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|
		|	BUS_A_READ(adr);
		|	if (!PIN_CS=> && !PIN_WE=>) {
		|		BUS_D_READ(state->ram[adr]);
		|	}
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	    << " | "
		|	    << std::hex << adr
		|	    << " "
		|	    << std::hex << state->ram[adr]
		|	);
		|	if (!PIN_CS=> && PIN_WE=>) {
		|		BUS_Q_WRITE(state->ram[adr] ^ 0xf);
		|	} else {
		|		BUS_Q_Z();
		|	}
		|	if (PIN_CS=>)
		|		next_trigger(PIN_CS.negedge_event());
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F189", PartModel("F189", F189))
