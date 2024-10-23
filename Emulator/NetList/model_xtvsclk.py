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

    autopin = True

    def sensitive(self):
        yield "PIN_Q4E"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_Q4E.negedge()) {
		|		output.zclk = true;
		|		output.cclk = true;
		|		output.aclk = true;
		|		output.uclk = true;
		|		output.arfwe = true;
		|	} else if (PIN_Q4E.posedge()) {
		|		bool uon = PIN_UON=>;
		|		bool ram_stop = PIN_RMS=>;
		|		bool sce = !(PIN_STS=> && ram_stop && PIN_WEL=>);
		|		bool uena = !(
		|			(uon && PIN_UOF=>) ||
		|			(uon && PIN_SFS=>)
		|		);
		|		output.uclk = !uena;
		|
		|		output.zclk = sce || PIN_ZCE=>;
		|		output.cclk = sce || PIN_CCE=>;
		|		output.aclk = sce || PIN_ACE=>;
		|
		|		bool ween = PIN_DSTOP=>;
		|		output.arfwe = !(!(ween || PIN_ARFWR=>) && ram_stop);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTVSCLK", PartModel("XTVSCLK", XTVSCLK))
