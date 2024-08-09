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
   Zero bit counter
   ================

'''


from part import PartModel, PartFactory

class XZCNT(PartFactory):

    ''' Zero bit counter'''

    autopin = True

    def state(self, file):
        file.write("\tuint64_t count;\n")

    def sensitive(self):
        yield 'PIN_OE'
        yield 'PIN_CLK.pos()'

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t data = 0, probe = (1ULL<<63);
		|
		|	if (PIN_CLK.posedge()) {
		|		BUS_I_READ(data);
		|		for (state->count = 0; state->count < 65; state->count++) {
		|			if (!(data & probe))
		|				break;
		|			probe >>= 1;
		|		}
		|	}
		|
		|	TRACE(
		|	   << " clk " << PIN_CLK.posedge()
		|	   << " oe " << PIN_OE?
		|	   << " i " << BUS_I_TRACE()
		|	   << " reg " << std::hex << state->count
		|	);
		|
		|	output.z_z = PIN_OE=>;
		|	if (!output.z_z)
		|		output.z = ~state->count;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XZCNT", PartModel("XZCNT", XZCNT))
