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
   Decode RAM
   ==========

'''


from part import PartModel, PartFactory

class XDECRAM(PartFactory):

    ''' Decode RAM '''

    def state(self, file):
        file.fmt('''
		|#if BUS_Q_WIDTH <= 8
		|	uint8_t ram[2048];
		|#else
		|	uint16_t ram[2048];
		|#endif
		|''')

    def sensitive(self):
        yield "BUS_A_SENSITIVE()"
        if not self.comp.nodes["CS"].net.is_pd():
            yield "PIN_CS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0;
		|
		|	BUS_A_READ(adr);
		|
		|''')

        if not self.comp.nodes["CS"].net.is_pd():
            file.fmt('''
		|	if (PIN_CS=>) {
		|		TRACE(<< "z");
		|		BUS_Q_Z();
		|		next_trigger(PIN_CS.negedge_event());
		|		return;
		|	}
		|''')

        file.fmt('''
		|
		|
		|	if (adr < 1024)
		|		BUS_Q_WRITE(state->ram[adr]);
		|	else
		|		BUS_Q_WRITE(state->ram[1024 + (adr >> 6)]);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XDECRAM4", PartModel("XDECRAM4", XDECRAM))
    part_lib.add_part("XDECRAM8", PartModel("XDECRAM8", XDECRAM))
    part_lib.add_part("XDECRAM16", PartModel("XDECRAM16", XDECRAM))
