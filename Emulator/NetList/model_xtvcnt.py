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
   TYP/VAL Counter
   ===============

'''

from part import PartModel, PartFactory

class XTVCNT(PartFactory):
    ''' TYP/VAL Counter '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned count;
		|''')

    def sensitive(self):
        yield "PIN_CLKQ4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	if (PIN_CLKQ4.posedge()) {
		|		if (PIN_SCLKEN=>) {
		|			unsigned uir;
		|			BUS_UIR_READ(uir);
		|			if (uir == 0x28) {
		|				BUS_D_READ(state->count);
		|			} else if (!PIN_DEC=>) {
		|				state->count += 1;
		|				state->count &= BUS_D_MASK;
		|				output.co = state->count != BUS_D_MASK;
		|			} else if (!PIN_INC=>) {
		|				state->count += BUS_D_MASK;
		|				state->count &= BUS_D_MASK;
		|				output.co = state->count != 0;
		|			}
		|		} else {
		|			output.co = true;
		|		}
		|		output.q = state->count;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVCNT", PartModel("XTVCNT", XTVCNT))
