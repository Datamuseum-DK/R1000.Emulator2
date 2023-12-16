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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t tosram[1<<BUS_RADR_WIDTH];
		|	uint64_t tosof;
		|	uint32_t savrg;
		|	uint32_t pred;
		|	uint32_t topcnt;
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_NAMOE",
            "PIN_TYQOE",
            "PIN_STCLK",
            "PIN_SVCLK",
            "PIN_TCLK",
            "PIN_PDCLK",
            "BUS_IRDS",
            "PIN_UTOS",
            "BUS_MSD",
            "PIN_H2",
        )
        yield from self.event_or(
            "idle_event_md",
            "PIN_NAMOE",
            "PIN_TYQOE",
            "PIN_STCLK",
            "PIN_SVCLK",
            "PIN_TCLK",
            "PIN_PDCLK",
            "BUS_IRDS",
        )


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool maybe_dispatch = PIN_MD=>;
		|	bool uses_tos, dis;
		|	unsigned mem_start, res_alu_s;
		|	bool intreads1, intreads2;
		|	bool sel1, sel2;
		|	unsigned output_rofs, output_ob;
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
		|	unsigned typ;
		|	BUS_TYP_READ(typ);
		|
		|	if (PIN_TCLK.posedge()) {
		|		state->tosof = (typ >> 7) & 0xfffff;
		|	}
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (PIN_TOSS=>) {
		|			offs = (typ >> 7) & 0xfffff;
		|		} else {
		|			offs = state->tosof;
		|		}
		|	} else {
		|		unsigned res_adr;
		|		BUS_RADR_READ(res_adr);
		|		if (PIN_RWE.posedge()) {
		|			offs = (typ >> 7) & 0xfffff;
		|			state->tosram[res_adr] = offs;
		|		} else {
		|			offs = state->tosram[res_adr];
		|		}
		|	}
		|	offs ^= 0xfffff;
		|
		|       unsigned disp;
		|       BUS_DSP_READ(disp);
		|       bool d7 = (disp & 0x8100) == 0;
		|       unsigned sgdisp = disp & 0xff;
		|       if (!d7)
		|               sgdisp |= 0x100;
		|       if (!(PIN_SGEXT && d7))
		|               sgdisp |= 0xffe00;
		|
		|	unsigned intreads = 0;
		|	if (intreads1) intreads |= 2;
		|	if (intreads2) intreads |= 1;
		|	bool acin = ((mem_start & 1) != 0);
		|       offs &= 0xfffff;
		|       sgdisp &= 0xfffff;
		|       unsigned rofs = 0;
		|       bool co = false;
		|
		|	switch(mem_start) {
		|	case 0:
		|	case 2:
		|		res_alu_s = 0x9;
		|               rofs = offs + sgdisp + 1;
		|               co = (rofs >> 20) == 0;
		|		break;
		|	case 1:
		|	case 3:
		|		res_alu_s = 0x6;
		|               rofs = (1<<20) + offs - (sgdisp + 1);
		|               co = acin && (offs == 0);
		|		break;
		|	case 4:
		|	case 6:
		|		res_alu_s = 0x5;
		|               rofs = sgdisp ^ 0xfffff;
		|               // Carry is probably "undefined" here.
		|		break;
		|	case 5:
		|	case 7:
		|		res_alu_s = 0xf;
		|               rofs = offs;
		|               co = acin && (offs == 0);
		|		break;
		|	}
		|
		|	output_rofs = rofs;
		|	output_rofs &= 0xfffff;
		|
		|	unsigned cnb;
		|	if (PIN_CMR=>) {
		|		cnb = typ ^ BUS_TYP_MASK;
		|	} else {
		|		BUS_FIU_READ(cnb);
		|	}
		|	cnb >>= 7;
		|	cnb &= 0xfffff;
		|
		|	unsigned csa_cntl;
		|	BUS_CTL_READ(csa_cntl);
		|
		|	if (PIN_SVCLK.posedge()) {
		|		state->savrg = rofs;
		|		output.cout = co;
		|	}
		|	if (PIN_PDCLK.posedge()) {
		|		state->pred = cnb;
		|	}
		|	if (PIN_STCLK.posedge()) {
		|		bool ten = (csa_cntl != 2 && csa_cntl != 3);
		|		bool tud = !(csa_cntl & 1);
		|		if (!PIN_TOPLD=>) {
		|			state->topcnt = cnb;
		|		} else if (!PIN_LSTPD=> || ten) {
		|			// Nothing
		|		} else if (tud) {
		|			state->topcnt += 1;
		|		} else {
		|			state->topcnt += 0xfffff;
		|		}
		|		state->topcnt &= 0xfffff;
		|	}
		|
		|	if (dis) {
		|		output_ob = 0xfffff;
		|	} else if (intreads == 0) {
		|		output_ob = state->pred;
		|	} else if (intreads == 1) {
		|		output_ob = state->topcnt;
		|	} else if (intreads == 2) {
		|		output_ob = rofs;
		|	} else if (intreads == 3) {
		|		output_ob = state->savrg;
		|	} else {
		|		output_ob = 0xfffff;
		|	}
		|	output_ob &= 0xfffff;
		|	
		|	output.z_tyq = PIN_TYQOE=>;
		|	if (!output.z_tyq) {
		|		BUS_CSA_READ(output.tyq);
		|		output.tyq |= output_ob << 7;
		|		output.tyq ^= BUS_TYQ_MASK;
		|	}
		|
		|	uint64_t nam;
		|
		|	if (!PIN_RESDR=>) {
		|		//BUS_RES_READ(nam);
		|		nam = output_rofs;
		|	} else if (PIN_ADRIC=>) {
		|		BUS_CODE_READ(nam);
		|	} else {
		|		//BUS_OFFS_READ(nam);
		|		nam = output_ob;
		|	}
		|	nam <<= 7;
		|
		|	unsigned branch;
		|	BUS_BRNC_READ(branch);
		|	branch ^= BUS_BRNC_MASK;
		|	nam |= branch << 4;
		|
		|	output.z_nam = PIN_NAMOE=>;
		|	if (!output.z_nam) {
		|		output.nam = nam;
		|		output.par = offset_parity(nam);
		|	}
		|
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|		if (output.z_nam && output.z_tyq && maybe_dispatch) {
		|			next_trigger(idle_event_md);
		|		} else if (output.z_nam && output.z_tyq) {
		|			next_trigger(idle_event);
		|		}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQ12", PartModel("XSEQ12", XSEQ12))
