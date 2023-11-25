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
   SEQ Instruction buffer
   ======================

'''

from part import PartModel, PartFactory

class XSEQIBUF(PartFactory):
    ''' SEQ Instruction buffer '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t typ, val;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "BUS_IBOE_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	unsigned iboe;
		|
		|	if (PIN_CLK.posedge()) {
		|		BUS_TYP_READ(state->typ);
		|		BUS_VAL_READ(state->val);
		|	} 
		|
		|	BUS_IBOE_READ(iboe);
		|
		|	if (!(iboe & 0x80))
		|		output.disp = state->typ >> 48;
		|	else if (!(iboe & 0x40))
		|		output.disp = state->typ >> 32;
		|	else if (!(iboe & 0x20))
		|		output.disp = state->typ >> 16;
		|	else if (!(iboe & 0x10))
		|		output.disp = state->typ >> 0;
		|	else if (!(iboe & 0x08))
		|		output.disp = state->val >> 48;
		|	else if (!(iboe & 0x04))
		|		output.disp = state->val >> 32;
		|	else if (!(iboe & 0x02))
		|		output.disp = state->val >> 16;
		|	else if (!(iboe & 0x01))
		|		output.disp = state->val >> 0;
		|	else
		|		output.disp = 0xffff;
		|	TRACE(
		|		<< " clk^ " << PIN_CLK.posedge()
		|		<< " iboe " << BUS_IBOE_TRACE()
		|		<< " disp " << std::hex << output.disp
		|	);
		|
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQIBUF", PartModel("XSEQIBUF", XSEQIBUF))
