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
   MEM32 LRU logic
   ===============

'''

from part import PartModel, PartFactory

class XLRU(PartFactory):
    ''' MEM32 LRU logic '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	bool qhit;
		|	bool qlog;
		|	bool qsoil;
		|	bool dsoil;
		|	bool qmod;
		|	bool qlpar;
		|	bool dlpar;
		|	bool dpar6;
		|	unsigned qlru;
		|	unsigned dlru;
		|	bool dhit;
		|	bool hhit;
		|	bool qpar;
		|	bool oeq;
		|	bool oeh;
		|	bool modd;
		|	bool modm;
		|	unsigned lrua, lrub;
		|	bool para, parb;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_NMAT"
        yield "PIN_LRUP"
        yield "BUS_LRI_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool late = PIN_LATE=>;
		|	bool neg = PIN_CLK.negedge();
		|	bool pos = PIN_CLK.posedge();
		|	bool nxthhit = false;
		|
		|	bool hit = true;
		|	if (state->qhit)
		|		hit = false;
		|	if (PIN_NMAT=> && state->qlog)
		|		hit = false;
		|
		|	if (pos) {
		|		// LUXXPAL
		|		if (state->dhit) {
		|			state->lrua = state->dlru ^ 0xf;
		|			state->lrub = state->dlru;
		|			if (state->lrub > 0)
		|				state->lrub -= 1;
		|			state->lrub ^= 0xf;
		|			state->para = !state->dpar6;
		|			switch(state->dlru) {
		|			case 0x2:
		|			case 0x6:
		|			case 0x8:
		|			case 0xa:
		|			case 0xe:
		|				// par(n) == par(n-1)
		|				state->parb = !state->dpar6;
		|				break;
		|			default:
		|				// par(n) != par(n-1)
		|				state->parb = state->dpar6;
		|				break;
		|			}
		|		} else {
		|			bool mrif = PIN_MRIF=>;
		|			if (mrif) {
		|				state->lrua = 0x0;
		|				state->lrub = 0x0;
		|			} else {
		|				state->lrua = 0x8;
		|				state->lrub = 0x8;
		|			}
		|			state->para = state->dsoil ^ state->dlpar ^ state->dpar6 ^ mrif;
		|			state->parb = state->para;
		|		}
		|
		|		if (!late) {
		|			state->modd = !(state->modm || (state->dsoil && !state->dhit));
		|			state->modm = state->qmod;
		|			state->oeq = !(PIN_LRUP=> && (!PIN_H1=>) && (!hit));
		|		} else {
		|			state->modd = !((state->qmod) || (state->dsoil && !state->dhit));
		|			state->oeq = !(PIN_LRUP=> && !hit);
		|		}
		|		state->oeh = !(PIN_LRUP=> && (!PIN_H1=>) && (!state->dhit));
		|		nxthhit = state->dhit;
		|	}
		|
		|	if (neg) {
		|		// LRUREG
		|		state->dhit = hit;
		|		state->dsoil = state->qsoil;
		|		state->dlpar = state->qlpar;
		|		state->dpar6 = state->qpar;
		|		state->dlru = state->qlru;
		|	}
		|
		|	if ((!late && neg) || (late && pos)) {
		|
		|		unsigned tag, cmd;
		|		BUS_TAG_READ(tag);
		|		state->qpar = PIN_PAR=>;
		|		state->qmod = (tag >> 6) & 0x1;
		|		state->qlru = (tag >> 2) & 0xf;
		|
		|		unsigned page_state = tag & 3;
		|		// R1000_Micro_Arch_Mem.pdf p19:
		|		//    00: Loading, 01: Read-only, 10: Read-Write, 11: Invalid
		|
		|		BUS_CMD_READ(cmd);
		|
		|		bool p_phit = PIN_PHIT=>;
		|		bool p_mcyc1 = PIN_CYC1=>;
		|
		|		if (!PIN_FHIT=>) {
		|			state->qhit = !p_phit;
		|			state->qlog = false;
		|		} else if (p_mcyc1) {
		|			state->qhit = !state->hhit;
		|			state->qlog = false;
		|		} else {
		|			state->qhit = false;
		|			state->qlog = false;
		|
		|			switch(cmd) {
		|			case 0x1:	// AVAILABLE QUERY
		|				state->qhit = !page_state;
		|				break;
		|			case 0x2:	// LRU QUERY
		|				state->qhit = (state->qlru == 0);
		|				break;
		|			case 0x3:	// NAME QUERY
		|			case 0x4:	// LOGICAL TAG READ
		|				state->qlog = (page_state != 0);
		|				break;
		|			case 0x5:	// INITIALIZE MRU
		|			case 0x6:	// PHYSICAL TAG READ
		|			case 0x7:	// PHYSICAL TAG WRITE
		|			case 0x8:	// SET HIT FLIP FLOPS
		|				state->qhit = !p_phit;
		|				break;
		|			case 0x9:	// COPY 1 to 0
		|				state->qhit = !state->hhit;
		|				break;
		|			case 0xa:	// MEMORY_TO_TAGSTORE
		|			case 0xb:	// COPY 0 TO 1
		|				state->qhit = !p_phit;
		|				break;
		|			case 0xc:	// LOGICAL_MEM_READ
		|				state->qlog = (page_state == 1 || page_state == 2);
		|				break;
		|			case 0xd:	// LOGICAL_MEM_WRITE
		|				state->qlog = (page_state == 1);
		|				break;
		|			case 0xe:	// PHYSICAL_MEM_READ
		|			case 0xf:	// PHYSICAL_MEM_WRITE
		|				state->qhit = !p_phit;
		|				break;
		|			default:
		|				break;
		|			}
		|		}
		|
		|		state->qsoil = ((!state->qmod) && (!p_mcyc1) && cmd == 0xd);
		|
		|		state->qlpar = odd_parity(state->qlru);
		|
		|		output.logq = state->qlog;
		|	}
		|
		|	hit = true;
		|	if (state->qhit)
		|		hit = false;
		|	if (PIN_NMAT=> && state->qlog)
		|		hit = false;
		|	PIN_HIT<=(hit);
		|
		|	if (late) {
		|		state->oeq = !(PIN_LRUP=> && !hit); 
		|	} else {
		|		state->oeq = !(PIN_LRUP=> && (!PIN_H1=>) && (!hit));
		|	}
		|
		|	if (!state->oeq) {
		|		output.hlru = state->qlru;
		|		output.z_hlru = false;
		|	} else if (!state->oeh) {
		|		output.hlru = state->dlru;
		|		output.z_hlru = false;
		|	} else {
		|		output.z_hlru = true;
		|	}
		|
		|	unsigned wrd = BUS_WRD_MASK + 1;
		|	if (pos) {
		|		state->hhit = nxthhit;
		|	}
		|
		|	wrd = 0;
		|	wrd |= state->modd << 5;
		|	unsigned lri;
		|	BUS_LRI_READ(lri);
		|	if (state->lrua < lri) {
		|		wrd |= state->lrub << 1;
		|		wrd |= state->parb;
		|	} else {
		|		wrd |= state->lrua << 1;
		|		wrd |= state->para;
		|	}
		|	wrd ^= 0xff;
		|	output.wrd = wrd;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XLRU", PartModel("XLRU", XLRU))
