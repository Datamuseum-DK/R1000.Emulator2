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
   IOC Dummy register
   ==================

'''

from part import PartModelDQ, PartFactory

class XDUMMY(PartFactory):
    ''' IOC Dummy register '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t typ, val;
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_QTYPOE",
            "PIN_QVALOE",
            "PIN_LDDUM",
            "PIN_DGSEL",
        )

    def sensitive(self):
        yield "PIN_QTYPOE"
        yield "PIN_QVALOE"
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 2) {
		|		state->typ = -1;
		|		state->val = -1;
		|	}
		|	if (PIN_Q4.posedge() && !PIN_LDDUM=>) {
		|		BUS_DTYP_READ(state->typ);
		|		BUS_DVAL_READ(state->val);
		|	}
		|	output.z_qval = PIN_QVALOE=>;
		|	if (!output.z_qval)
		|		output.qval = state->val;
		|	output.z_qtyp = PIN_QTYPOE=>;
		|	if (!output.z_qtyp)
		|		output.qtyp = state->typ;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XDUMMY", PartModelDQ("XDUMMY", XDUMMY))
