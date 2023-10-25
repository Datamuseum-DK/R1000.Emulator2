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
   TV state clock
   ==============

'''

from part import PartModel, PartFactory

class XTVSCLK(PartFactory):
    ''' TV state clock '''

    def sensitive(self):
        yield "PIN_Q3.pos()"
        yield "PIN_2XE.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	if (state->ctx.job == 1) {
		|		state->ctx.job = 0;
		|		PIN_UCLK<=(true);
		|		PIN_CCLK<=(true);
		|		PIN_ACLK<=(true);
		|		PIN_ZCLK<=(true);
		|		PIN_ARFWE<=(true);
		|		PIN_BRFWE<=(true);
		|		next_trigger(PIN_H2.negedge_event());
		|	} else if (PIN_H2.negedge()) {
		|		//bool ram_stop = PIN_RMS=>;
		|		//PIN_ARFCS<=(!(PIN_ACOFF=> && ram_stop));
		|		//PIN_BRFCS<=(!(PIN_BCOFF=> && ram_stop));
		|		PIN_ARFCS<=(!PIN_ACOFF=>);
		|		PIN_BRFCS<=(!PIN_BCOFF=>);
		|		next_trigger(PIN_H2.posedge_event());
		|	} else if (PIN_H2.posedge()) {
		|		if (PIN_ALOFF=>)
		|			PIN_ARFCS<=(true);
		|		if (PIN_BLOFF=>)
		|			PIN_BRFCS<=(true);
		|		next_trigger(PIN_Q3.posedge_event());
		|	} else if (PIN_Q3.posedge()) {
		|		bool uon = PIN_UON=>;
		|		bool ram_stop = PIN_RMS=>;
		|
		|		bool sce = !(PIN_STS=> && ram_stop && PIN_WEL=>);
		|		bool uena = !(
		|			(uon && PIN_UOF=>) ||
		|			(uon && PIN_SFS=>)
		|		);
		|		PIN_UCLK<=(!uena);
		|
		|		// bool sce = PIN_SCE=>;
		|		bool zena = !(sce || PIN_ZCE=>);
		|		PIN_ZCLK<=(!zena);
		|		bool cena = !(sce || PIN_CCE=>);
		|		PIN_CCLK<=(!cena);
		|		bool aena = !(sce || PIN_ACE=>);
		|		PIN_ACLK<=(!aena);
		|
		|		bool ween = !PIN_H2=> || PIN_DSTOP=>;
		|		bool arfwe = !(
		|			PIN_ACOFF=> &&
		|			!(ween || PIN_ARFWR=>) &&
		|			ram_stop
		|		);
		|		PIN_ARFWE<=(arfwe);
		|
		|		bool brfwe = !(
		|			PIN_BCOFF=> &&
		|			!(ween || PIN_BRFWR=>) &&
		|			ram_stop
		|		);
		|		PIN_BRFWE<=(brfwe);
		|
		|		next_trigger(PIN_2XE.posedge_event());
		|	} else if (PIN_2XE.posedge()) {
		|		PIN_ARFWE<=(true);
		|		PIN_BRFWE<=(true);
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVSCLK", PartModel("XTVSCLK", XTVSCLK))
