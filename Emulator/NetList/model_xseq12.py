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
   SEQ 12 Noodle Logic
   ===================

'''

from part import PartModel, PartFactory

class XSEQ12(PartFactory):
    ''' SEQ 12 Noodle Logic '''

    def state(self, file):
        file.fmt('''
		|	uint64_t tosram[1<<BUS_RADR_WIDTH];
		|	uint64_t tosof;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool maybe_dispatch = PIN_MD=>;
		|	bool uses_tos, dis;
		|	unsigned mem_start, res_alu_s;
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
		|	PIN_ACIN<=((mem_start & 1) != 0);
		|	PIN_AMOD<=((mem_start & 4) != 0);
		|	switch(mem_start) {
		|	case 0: res_alu_s = 0x9; break;
		|	case 1: res_alu_s = 0x6; break;
		|	case 2: res_alu_s = 0x9; break;
		|	case 3: res_alu_s = 0x6; break;
		|	case 4: res_alu_s = 0x5; break;
		|	case 5: res_alu_s = 0xf; break;
		|	case 6: res_alu_s = 0x5; break;
		|	case 7: res_alu_s = 0xf; break;
		|	}
		|	BUS_AS_WRITE(res_alu_s);
		|	if (dis) {
		|		PIN_NRAM<=1;
		|		PIN_TNAM<=1;
		|		PIN_VNAM<=1;
		|		PIN_PRED<=1;
		|		PIN_TOP<=1;
		|		PIN_RES<=1;
		|		PIN_SAVE<=1;
		|	} else {
		|		PIN_NRAM<=(!(!sel1 && sel2));
		|		PIN_TNAM<=(!(sel1 && !sel2));
		|		PIN_VNAM<=(!(sel1 && sel2));
		|		PIN_PRED<=(!(!intreads1 && !intreads2));
		|		PIN_TOP<=(!(!intreads1 &&  intreads2));
		|		PIN_RES<=(!(intreads1 && !intreads2));
		|		PIN_SAVE<=(!(intreads1 && intreads2));
		|	}
		|	if (PIN_TCLK.posedge()) {
		|		BUS_TYP_READ(state->tosof);
		|	}
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (PIN_TOSS=>) {
		|			BUS_TYP_READ(offs);
		|		} else {
		|			offs = state->tosof;
		|		}
		|	} else {
		|		unsigned res_adr;
		|		BUS_RADR_READ(res_adr);
		|		if (PIN_RWE.posedge()) {
		|			BUS_TYP_READ(offs);
		|			state->tosram[res_adr] = offs;
		|		} else {
		|			offs = state->tosram[res_adr];
		|		}
		|	}
		|	offs ^= BUS_OFFS_MASK;
		|	BUS_OFFS_WRITE(offs);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQ12", PartModel("XSEQ12", XSEQ12))
