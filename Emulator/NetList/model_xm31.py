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
   MEM32 pg 31
   ===========

'''

from part import PartModel, PartFactory

class XM31(PartFactory):
    ''' MEM32 pg 31 '''

    autopin = ("TMP", "DSYNC", "DFRZE", "PARER", "CSTOP", "TLWDR",)

    def state(self, file):
        file.fmt('''
		|	unsigned cmdreg;
		|	bool tlwdr;
		|	bool diag_sync;
		|	bool diag_freeze;
		|''')

    def sensitive(self):
        yield "PIN_Q2.pos()"
        yield "PIN_Q4"
        yield "PIN_DLWDR"
        yield "PIN_DENLW"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned cmdreg = 0;
		|
		|	if (PIN_Q2.posedge()) {
		|		if (PIN_SEL=>) {
		|			BUS_TRACE_READ(cmdreg);
		|		} else {
		|			if (PIN_LDWDR=>)
		|				cmdreg |= 2;
		|		}
		|		state->tlwdr = (cmdreg & 2) == 0;
		|		bool diag_sync = !PIN_BDISYN=>;
		|		bool diag_freeze = !PIN_BDIFRZ=>;
		|		output.dsync = diag_sync;
		|		output.dfrze = diag_freeze;
		|		output.cstop = !(diag_sync || diag_freeze);
		|	}
		|
		|	if (PIN_Q4.posedge()) {
		|		output.tlwdr = false;
		|		if (PIN_CMDE=>) {
		|			if (PIN_SEL=>) {
		|				BUS_TRACE_READ(cmdreg);
		|			} else {
		|				unsigned tmp;
		|				BUS_MCMD_READ(tmp);
		|				cmdreg |= tmp << 4;
		|				if (PIN_CONT=>)
		|					cmdreg |= 8;
		|				cmdreg |= 5;
		|			}
		|			output.tmp = cmdreg >> 2;
		|		}
		|	} else if (!PIN_Q4=>) {
		|		if (PIN_DLWDR=> || (
		|		    state->tlwdr &&
		|		    !state->diag_sync &&
		|		    !state->diag_freeze &&
		|		    PIN_DENLW=>
		|		)) {
		|			output.tlwdr = true;
		|		}
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM31", PartModel("XM31", XM31))
