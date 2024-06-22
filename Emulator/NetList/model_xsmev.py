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
   SEQ Macro Event resolver
   ========================

'''

from part import PartModel, PartFactory

class XSMEV(PartFactory):
    ''' SEQ Macro Event resolver '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_WDISP",
            "PIN_MDISP",
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool wanna_dispatch = PIN_WDISP=>;
		|	bool maybe_dispatch = PIN_MDISP=>;
		|	bool e_macro_pend = PIN_EMP=>;
		|	unsigned lmp;
		|	BUS_LMP_READ(lmp);
		|	bool l_macro_pend = lmp != BUS_LMP_MASK;
		|
		|	output.disp = wanna_dispatch || e_macro_pend || l_macro_pend;
		|	output.mevh = (!wanna_dispatch) && (e_macro_pend || l_macro_pend);
		|	output.mevl = !output.mevh;
		|	output.lmac = output.mevh && !e_macro_pend;
		|
		|	if (maybe_dispatch)
		|		output.lmu = 7;
		|	else if (!(lmp & 0x80))
		|		output.lmu = 0;
		|	else if (!(lmp & 0x40))
		|		output.lmu = 1;
		|	else if (!(lmp & 0x20))
		|		output.lmu = 2;
		|	else if (!(lmp & 0x10))
		|		output.lmu = 3;
		|	else if (!(lmp & 0x08))
		|		output.lmu = 4;
		|	else if (!(lmp & 0x04))
		|		output.lmu = 5;
		|	else if (!(lmp & 0x02))
		|		output.lmu = 6;
		|	else
		|		output.lmu = 7;
		|
		|	output.mibf = !(output.lmac && output.lmu == 7);
		|
		|	if (wanna_dispatch && maybe_dispatch) {
		|		idle_next = &idle_event;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSMEV", PartModel("XSMEV", XSMEV))
