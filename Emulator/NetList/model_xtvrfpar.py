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
   TYP/VAL RF Parity Check
   =======================

'''

from part import PartModel, PartFactory

class XTVRFPAR(PartFactory):
    ''' TYP/VAL RF Parity Check '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t reg;
		|''')

    def sensitive(self):
        yield "PIN_Q4.pos()"
        yield "BUS_AP_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned tmp = 0;
		|
		|	bool cm_diag_on = PIN_DGCO=>;
		|	bool c_source = PIN_CSRC=>;
		|	bool split_c = PIN_CSPL=>;
		|
		|	bool efiu0 = cm_diag_on && !c_source;
		|	bool efiu1 = cm_diag_on && (c_source != split_c);
		|
		|	if (efiu0 || efiu1) {
		|		unsigned fiu;
		|		BUS_FIU_READ(fiu);
		|		fiu ^= BUS_FIU_MASK;
		|		if (efiu0)
		|			tmp |= fiu & 0xf0;
		|		if (efiu1)
		|			tmp |= fiu & 0x0f;
		|	}
		|	if (!efiu0 || !efiu1) {
		|		unsigned wdr;
		|		BUS_WDR_READ(wdr);
		|		if (!efiu0)
		|			tmp |= wdr & 0xf0;
		|		if (!efiu1)
		|			tmp |= wdr & 0x0f;
		|	}
		|	if (!PIN_SNEAK=>) {
		|		unsigned cchk;
		|		BUS_CCHK_READ(cchk);
		|		tmp &= 0xfe;
		|		tmp |= cchk & 1;
		|	}
		|	if (PIN_Q4.posedge()) {
		|		state->reg = tmp;
		|	}
		|	unsigned ap;
		|	BUS_AP_READ(ap);
		|	output.perr = ap != state->reg;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVRFPAR", PartModel("XTVRFPAR", XTVRFPAR))
