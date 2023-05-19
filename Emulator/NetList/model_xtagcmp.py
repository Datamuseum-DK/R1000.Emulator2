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
   MEM32 Tag comparator
   ====================

'''

from part import PartModel, PartFactory

class XTAGCMP(PartFactory):
    ''' Select next micro address '''

    def state(self, file):
        file.fmt('''
		|	bool nme;
		|	bool ome;
		|	bool nml;
		|	bool oml;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_EQ"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t ta, ts, nm, pg, sp;
		|	bool name, offset;
		|
		|	BUS_TA_READ(ta);
		|	ts = ta & 0x7;
		|	ta = ta >> 19;
		|	BUS_NM_READ(nm);
		|	BUS_PG_READ(pg);
		|	BUS_SP_READ(sp);
		|
		|	if (PIN_E) {
		|		name = true;
		|		offset = true;
		|	} else {
		|		name = (nm != (ta >> BUS_PG_WIDTH));
		|		offset = (pg != (ta & BUS_PG_MASK)) || (sp != ts);
		|	}
		|	
		|	TRACE(
		|	    << " clk^ " << PIN_CLK.posedge()
		|	    << " e " << PIN_E?
		|	    << " eq " << PIN_EQ?
		|	    << " ta " << BUS_TA_TRACE()
		|	    << " nm " << BUS_NM_TRACE()
		|	    << " pg " << BUS_PG_TRACE()
		|	    << " sp " << BUS_SP_TRACE()
		|	    << " - "
		|	    << " n " << name
		|	    << " o " << offset
		|	);
		|
		|	PIN_NME<=(!state->nme);
		|	PIN_OME<=(!(PIN_EQ=> && state->ome));
		|	PIN_NML<=(!state->nml);
		|	PIN_OML<=(!(PIN_EQ=> && state->oml));
		|
		|	if (PIN_CLK.posedge()) {
		|		state->nme = name;
		|		state->ome = offset;
		|		next_trigger(5, SC_NS);
		|		//PIN_NME<=(state->nme);
		|		//PIN_OME<=(state->ome);
		|	} else if (PIN_CLK.negedge()) {	 
		|		state->nml = name;
		|		state->oml = offset;
		|		next_trigger(5, SC_NS);
		|		//PIN_NML<=(state->nml);
		|		//PIN_OML<=(state->oml);
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTAGCMP", PartModel("XTAGCMP", XTAGCMP))
