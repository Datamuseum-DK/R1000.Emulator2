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
   SEQ Name generation
   ===================

'''

from part import PartModelDQ, PartFactory

class XSEQNAM(PartFactory):
    ''' SEQ Name generation '''

    autopin = True

    def xprivate(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_NAMOE",
            "PIN_QTLOE",
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
            "PIN_QTLOE",
            "PIN_STCLK",
            "PIN_SVCLK",
            "PIN_TCLK",
            "PIN_PDCLK",
            "BUS_IRDS",
        )

    def state(self, file):
        file.fmt('''
		|	uint32_t tost, vost, cur_name;
		|	uint32_t namram[1<<BUS_RADR_WIDTH];
		|	unsigned pcseg, retseg, last;
		|
		|	uint64_t tosram[1<<BUS_RADR_WIDTH];
		|	uint64_t tosof;
		|	uint32_t savrg;
		|	uint32_t pred;
		|	uint32_t topcnt;
		|''')

    def sensitive(self):
        yield "PIN_ADRICD"
        yield "PIN_ADRNOE"
        yield "BUS_BRNC"
        # yield "PIN_CMR"		# STCLK, PDCLK
        yield "PIN_CNCK.pos()"
        yield "PIN_CNOE"
        yield "BUS_CODE"
        yield "BUS_CSA"
        yield "PIN_CSEL"
        # yield "BUS_CTL"		# STCLK, PDCLK
        yield "BUS_DSP"
        # yield "BUS_DTH"		# TOSCLK, CNCK, RAMWE
        yield "BUS_DTL"
        # yield "BUS_DV"		# TOSCLK, MCLK
        # yield "BUS_FIU"		# STCLK PDCLK
        yield "PIN_H2"
        yield "BUS_IRDS"
        yield "BUS_ISPC"
        yield "PIN_MCLK.pos()"
        yield "PIN_MD"
        yield "BUS_MSD"
        yield "PIN_NAMOE"
        yield "PIN_OSPCOE"
        yield "PIN_PDCLK.pos()"
        yield "PIN_QTHOE"
        yield "PIN_QTLOE"
        yield "PIN_QVOE"
        yield "BUS_RADR"
        yield "PIN_RAMWE.pos()"
        yield "PIN_RCLK"
        yield "PIN_RESDR"
        yield "PIN_RWE.pos()"
        yield "PIN_SGEXT"
        yield "PIN_STCLK.pos()"
        yield "PIN_SVCLK.pos()"
        # yield "PIN_TOPLD"		# STCLK PDCLK
        yield "PIN_TOSCLK"
        yield "PIN_TOSS"
        yield "PIN_UTOS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool maybe_dispatch = PIN_MD=>;
		|	bool uses_tos, dis;
		|	unsigned mem_start, res_alu_s;
		|	bool intreads1, intreads2;
		|	bool sel1, sel2;
		|
		|	bool name_ram_cs = true;
		|	bool type_name_oe = true;
		|	bool val_name_oe = true;
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
		|	unsigned intreads = 0;
		|	if (intreads1) intreads |= 2;
		|	if (intreads2) intreads |= 1;
		|
		|	if (!dis) {
		|		name_ram_cs = (!(!sel1 && sel2));
		|		type_name_oe = (!(sel1 && !sel2));
		|		val_name_oe = (!(sel1 && sel2));
		|	}
		|
		|	unsigned typl;
		|	BUS_DTL_READ(typl);
		|
		|	output.z_ospc = PIN_OSPCOE=>;
		|	if (!output.z_ospc) {
		|		BUS_ISPC_READ(output.ospc);
		|		output.ospc ^= BUS_OSPC_MASK;
		|	}
		|
		|	if (PIN_TOSCLK.posedge()) {
		|		BUS_DTH_READ(state->tost);
		|		BUS_DV_READ(state->vost);
		|		state->tosof = (typl >> 7) & 0xfffff;
		|	}
		|
		|	if (PIN_CNCK.posedge()) {
		|		BUS_DTH_READ(state->cur_name);
		|	}
		|
		|	if (PIN_RAMWE.posedge()) {
		|		unsigned radr;
		|		BUS_RADR_READ(radr);
		|		BUS_DTH_READ(state->namram[radr]);
		|	}
		|
		|	uint32_t name_bus;
		|	if (!type_name_oe) {
		|		name_bus = state->tost ^ 0xffffffff;
		|	} else if (!val_name_oe) {
		|		name_bus = state->vost ^ 0xffffffff;
		|	} else if (!name_ram_cs) {
		|		unsigned radr;
		|		BUS_RADR_READ(radr);
		|		name_bus = state->namram[radr] ^ 0xffffffff;
		|	} else {
		|		name_bus = 0xffffffff;
		|	}
		|	output.z_qth = PIN_QTHOE=>;
		|	if (!output.z_qth) {
		|		if (PIN_CNOE=>)
		|			output.qth = name_bus ^ BUS_QTH_MASK;
		|		else
		|			output.qth = state->cur_name;
		|	}
		|
		|	if (PIN_RCLK.posedge()) {
		|		state->retseg = state->pcseg;
		|	}
		|	if (PIN_MCLK.posedge()) {
		|		unsigned val;
		|		BUS_DV_READ(val);
		|		val ^= BUS_DV_MASK;
		|		state->pcseg = val;
		|		state->pcseg &= 0xffffff;
		|	}
		|
		|	{
		|		unsigned cseg;
		|		if (!PIN_CSEL) {
		|			cseg = state->pcseg;
		|		} else {
		|			cseg = state->retseg;
		|		}
		|
		|		output.z_adrn = PIN_ADRNOE=>;
		|		if (!output.z_adrn) {
		|			if (PIN_ADRICD=>) {
		|				output.adrn = cseg;
		|			} else {
		|				output.adrn = name_bus;
		|			}
		|		}
		|	
		|		output.z_qv = PIN_QVOE=>;
		|		if (!output.z_qv) {
		|			output.qv = cseg ^ BUS_QV_MASK;
		|		}
		|	}
		|
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (PIN_TOSS=>) {
		|			offs = (typl >> 7) & 0xfffff;
		|		} else {
		|			offs = state->tosof;
		|		}
		|	} else {
		|		unsigned res_adr;
		|		BUS_RADR_READ(res_adr);
		|		if (PIN_RWE.posedge()) {
		|			state->tosram[res_adr] = (typl >> 7) & 0xfffff;
		|		}
		|		offs = state->tosram[res_adr];
		|	}
		|	offs ^= 0xfffff;
		|       offs &= 0xfffff;
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
		|	bool acin = ((mem_start & 1) != 0);
		|       sgdisp &= 0xfffff;
		|       unsigned resolve_offset = 0;
		|       bool co = false;
		|
		|	switch(mem_start) {
		|	case 0:
		|	case 2:
		|		res_alu_s = 0x9;
		|               resolve_offset = offs + sgdisp + 1;
		|               co = (resolve_offset >> 20) == 0;
		|		break;
		|	case 1:
		|	case 3:
		|		res_alu_s = 0x6;
		|               resolve_offset = (1<<20) + offs - (sgdisp + 1);
		|               co = acin && (offs == 0);
		|		break;
		|	case 4:
		|	case 6:
		|		res_alu_s = 0x5;
		|               resolve_offset = sgdisp ^ 0xfffff;
		|               // Carry is probably "undefined" here.
		|		break;
		|	case 5:
		|	case 7:
		|		res_alu_s = 0xf;
		|               resolve_offset = offs;
		|               co = acin && (offs == 0);
		|		break;
		|	}
		|
		|	resolve_offset &= 0xfffff;
		|
		|	if (PIN_SVCLK.posedge()) {
		|		state->savrg = resolve_offset;
		|		output.cout = co;
		|	}
		|
		|	if (PIN_PDCLK.posedge() || PIN_STCLK.posedge()) {
		|		unsigned cnb;
		|		if (!PIN_CMR=>) {
		|			cnb = typl ^ BUS_DTL_MASK;
		|		} else {
		|			BUS_FIU_READ(cnb);
		|		}
		|		cnb >>= 7;
		|		cnb &= 0xfffff;
		|
		|		if (PIN_PDCLK.posedge()) {
		|			state->pred = cnb;
		|		}
		|		if (PIN_STCLK.posedge()) {
		|			unsigned csa_cntl;
		|			BUS_CTL_READ(csa_cntl);
		|
		|			bool ten = (csa_cntl != 2 && csa_cntl != 3);
		|			bool tud = !(csa_cntl & 1);
		|			if (!PIN_TOPLD=>) {
		|				state->topcnt = cnb;
		|			} else if (ten) {
		|				// Nothing
		|			} else if (tud) {
		|				state->topcnt += 1;
		|			} else {
		|				state->topcnt += 0xfffff;
		|			}
		|			state->topcnt &= 0xfffff;
		|		}
		|	}
		|
		|	unsigned output_ob;
		|	if (dis) {
		|		output_ob = 0xfffff;
		|	} else if (intreads == 0) {
		|		output_ob = state->pred;
		|	} else if (intreads == 1) {
		|		output_ob = state->topcnt;
		|	} else if (intreads == 2) {
		|		output_ob = resolve_offset;
		|	} else if (intreads == 3) {
		|		output_ob = state->savrg;
		|	} else {
		|		output_ob = 0xfffff;
		|	}
		|	output_ob &= 0xfffff;
		|	
		|	output.z_qtl = PIN_QTLOE=>;
		|	if (!output.z_qtl) {
		|		BUS_CSA_READ(output.qtl);
		|		output.qtl |= output_ob << 7;
		|		output.qtl ^= BUS_QTL_MASK;
		|	}
		|
		|	output.z_nam = PIN_NAMOE=>;
		|	if (!output.z_nam) {
		|		if (!PIN_RESDR=>) {
		|			output.nam = resolve_offset;
		|		} else if (PIN_ADRICD=>) {
		|			BUS_CODE_READ(output.nam);
		|		} else {
		|			output.nam = output_ob;
		|		}
		|		output.nam <<= 7;
		|
		|		unsigned branch;
		|		BUS_BRNC_READ(branch);
		|		branch ^= BUS_BRNC_MASK;
		|		output.nam |= branch << 4;
		|	}
		|
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQNAM", PartModelDQ("XSEQNAM", XSEQNAM))
