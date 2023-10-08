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
   SEQ Address generation
   ======================

'''

from part import PartModel, PartFactory

class XSEQADR(PartFactory):
    ''' SEQ Address generation '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|
		|	bool nsoer;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	output.nspoe = !(
		|		PIN_DADOF=> && !(
		|			PIN_DADON=> && PIN_SEQAE=>
		|		)
		|	);
		|	if (PIN_Q4.posedge()) {
		|		state->nsoer = !output.nspoe;
		|	}
		|
		|	output.aparoe = !(PIN_Q4=> && state->nsoer);
		|
		|	output.tosrck = !(
		|		PIN_Q3=> &&
		|		!PIN_SEQSTP=> &&
		|		PIN_TOSVRN=>
		|	);
		|
		|	bool maybe_dispatch = PIN_MD=>;
		|	bool uses_tos, dis;
		|	unsigned mem_start;
		|	bool intreads1, intreads2;
		|	bool sel1, sel2;
		|
		|	if (maybe_dispatch) {
		|		uses_tos = false;
		|		mem_start = 7;
		|		dis = false;
		|		intreads1 = !PIN_IRDS1=>;
		|		intreads2 = !PIN_IRDS2=>;
		|		sel1 = false;
		|		sel2 = true;
		|	} else {
		|		uses_tos = PIN_UTOS=>;
		|		BUS_MSD_READ(mem_start);
		|		dis = !PIN_H2=>;
		|		intreads1 = !(mem_start == 0 || mem_start == 4);
		|		intreads2 = false;
		|		sel1 = !(mem_start < 3);
		|		sel2 = !(mem_start == 3 || mem_start == 7);
		|	}
		|	if (dis) {
		|		output.nram=1;
		|		output.tnam=1;
		|		output.vnam=1;
		|	} else {
		|		output.nram=(!(!sel1 && sel2));
		|		output.tnam=(!(sel1 && !sel2));
		|		output.vnam=(!(sel1 && sel2));
		|	}
		|
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQADR", PartModel("XSEQADR", XSEQADR))
