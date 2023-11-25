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
   SEQ Macro PC adder
   ==================

'''

from part import PartModel, PartFactory

class XMPCADD(PartFactory):
    ''' SEQ Macro PC adder '''

    # XXX: autopin failed

    def state(self, file):
        file.fmt('''
		|	unsigned retrn_pc_ofs;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)
        file.fmt('''
		|	bool wdisp, mibmt, oper;
		|	unsigned macro_pc_ofs;
		|	unsigned a, b, boff = 0;
		|
		|	wdisp = PIN_WDISP;
		|	mibmt = PIN_MIBMT;
		|	BUS_MPC_READ(macro_pc_ofs);
		|	if (PIN_RCLK.posedge()) {
		|		state->retrn_pc_ofs = macro_pc_ofs;
		|	}
		|	b = macro_pc_ofs;
		|	if (!wdisp && !mibmt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!wdisp && mibmt) {
		|		BUS_DISP_READ(a);
		|		oper = false;
		|	} else if (wdisp && !mibmt) {
		|		BUS_CURI_READ(a);
		|		a |= 0xf800;
		|		oper = true;
		|	} else {
		|		BUS_CURI_READ(a);
		|		a |= 0xf800;
		|		oper = true;
		|	}
		|	a &= 0x7ff;
		|	if (a & 0x400)
		|		a |= 0x7800;
		|	a ^= 0x7fff;
		|	b &= 0x7fff;
		|	if (oper) {
		|		if (wdisp)
		|			a += 1;
		|		a &= 0x7fff;
		|		boff = a + b;
		|	} else {
		|		if (!wdisp)
		|			a += 1;
		|		boff = b - a;
		|	}
		|	boff &= 0x7fff;
		|	BUS_BOFF_WRITE(boff);
		|	unsigned code_sel, coff;
		|	BUS_COSEL_READ(code_sel);
		|	switch (code_sel) {
		|	case 0:	coff = state->retrn_pc_ofs; break;
		|	case 1: coff = boff; break;
		|	case 2: coff = macro_pc_ofs; break;
		|	case 3: coff = boff; break;
		|	}
		|	coff ^= BUS_COFF_MASK;
		|	BUS_COFF_WRITE(coff);
		|	TRACE(
		|	    << " wdisp " << PIN_WDISP
		|	    << " mibmt " << PIN_MIBMT
		|	    << " disp " << BUS_DISP_TRACE()
		|	    << " curi " << BUS_CURI_TRACE()
		|	    << " mpc " << BUS_MPC_TRACE()
		|	    << " - boff " << std::hex << boff
		|	    << " a " << std::hex << a
		|	    << " b " << std::hex << b
		|	);
		''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMPCADD", PartModel("XMPCADD", XMPCADD))
