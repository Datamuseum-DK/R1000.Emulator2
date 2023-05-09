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

    def state(self, file):
        file.fmt('''
		|	bool qhit;
		|	bool qlog;
		|	bool qsoil;
		|	bool dsoil;
		|	bool qt49;
		|	bool qt50;
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
		|	bool oeu;
		|	bool t49d, t50d, modd;
		|	bool t49m, t50m, modm;
		|	unsigned lrua, lrub;
		|	bool para, parb;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_NMAT"
        yield "PIN_OMAT"
        yield "PIN_LRUP"
        yield "BUS_LRI_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool late = PIN_LATE=>;
		|	bool neg = PIN_CLK.negedge();
		|	bool pos = PIN_CLK.posedge();
		|	bool hit = true;
		|	bool nxthhit = false;
		|	bool mrif = false;
		|	unsigned hrlu;
		|
		|	if (state->qhit)
		|		hit = false;
		|	if (PIN_NMAT=> && PIN_OMAT=> && state->qlog)
		|		hit = false;
		|
		|	if (pos) {
		|		mrif = PIN_MRIF=>;
		|		// LUXXPAL
		|		if (state->dhit) {
		|			state->lrua = state->dlru ^ 0xf;
		|			state->lrub = state->dlru;
		|			if (state->lrub > 0)
		|				state->lrub -= 1;
		|			state->lrub ^= 0xf;
		|		} else if (mrif) {
		|			state->lrua = 0x0;
		|			state->lrub = 0x0;
		|		} else {
		|			state->lrua = 0x8;
		|			state->lrub = 0x8;
		|		}
		|		if (state->dhit) {
		|			state->para = !state->dpar6;
		|			switch(state->dlru) {
		|			case 0x2:
		|			case 0x6:
		|			case 0x8:
		|			case 0xa:
		|			case 0xe:
		|				state->parb = !state->dpar6;
		|				break;
		|			default:
		|				state->parb = state->dpar6;
		|				break;
		|			}
		|		} else {
		|			state->para =
		|				state->dsoil ^
		|				state->dlpar ^
		|				state->dpar6 ^
		|				mrif;
		|			state->parb = state->para;
		|		}
		|	}
		|	if (pos) {
		|		// MUX[LE]PAL common
		|		state->oeu = !PIN_LRUP=>;
		|		//PIN_OEU<=(state->oeu);
		|	}
		|	if (pos && !late) {
		|		state->t49d = !state->t49m;
		|		state->t50d = !state->t50m;
		|		state->modd = !(
		|			state->modm ||
		|			(state->dsoil && !state->dhit)
		|		);
		|		state->t49m = state->qt49;
		|		state->t50m = state->qt50;
		|		state->modm = state->qmod;
		|		state->oeq = !(
		|			PIN_LRUP=> && (!PIN_H1=>) && (!hit)
		|		);
		|		state->oeh = !(
		|			PIN_LRUP=> && (!PIN_H1=>) && (!state->dhit)
		|		);
		|	}
		|
		|	if (pos && late) {
		|		state->t49d = !state->qt49;
		|		state->t50d = !state->qt50;
		|		state->modd = !(
		|			(state->qmod) ||
		|			(state->dsoil && !state->dhit)
		|		);
		|		state->oeq = !(
		|			PIN_LRUP=> && !hit
		|		);
		|		state->oeh = !(
		|			PIN_LRUP=> && (!PIN_H1=>) && (!state->dhit)
		|		);
		|		nxthhit = state->dhit;
		|	}
		|
		|	if (neg) {
		|		// LRUREG
		|		state->dhit = true;
		|		if (state->qhit)
		|			state->dhit = false;
		|		if (PIN_NMAT=> && PIN_OMAT=> && state->qlog)
		|			state->dhit = false;
		|		state->dsoil = state->qsoil;
		|		state->dlpar = state->qlpar;
		|		state->dpar6 = state->qpar;
		|		state->dlru = state->qlru;
		|		//PIN_HITD<=(state->dhit);
		|		//PIN_SOILH<=(state->dsoil);
		|		//PIN_LPARH<=(state->dlpar);
		|		//PIN_PAR6H<=(state->dpar6);
		|		//BUS_LRUH_WRITE(state->dlru);
		|	}
		| 
		|	if ((!late && neg) || (late && pos)) {
		|		// LRUREG4
		|		unsigned tag, cmd;
		|		BUS_TAG_READ(tag);
		|		state->qpar = PIN_PAR=>;
		|		state->qt49 = (tag >> 8) & 0x1;
		|		state->qt50 = (tag >> 7) & 0x1;
		|		state->qmod = (tag >> 6) & 0x1;
		|		state->qlru = (tag >> 2) & 0xf;
		|
		|		// TSXXPAL
		|		BUS_CMD_READ(cmd);
		|
		|		bool p_tag_57 = (tag >> 0) & 1;
		|		bool p_tag_56 = (tag >> 1) & 1;
		|		bool p_tag_55 = (tag >> 2) & 1;
		|		bool p_tag_54 = (tag >> 3) & 1;
		|		bool p_tag_53 = (tag >> 4) & 1;
		|		bool p_tag_52 = (tag >> 5) & 1;
		|		bool p_tag_51 = (tag >> 6) & 1;
		|		bool p_phit_al = PIN_PHIT=>;
		|		bool p_force_hit = PIN_FHIT=>;
		|		bool p_hit_h = state->hhit;
		|		bool p_mcyc1 = PIN_CYC1=>;
		|
		|		bool out_hitq =
		|		    ((!p_tag_55) && (!p_tag_54) && (!p_tag_53) && (!p_tag_52) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x2) ||
		|		    (  p_force_hit  && (!p_hit_h) &&   (!p_mcyc1) && cmd == 0x9) ||
		|		    ((!p_tag_57) && (!p_tag_56) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x01) ||
		|		    ((!p_phit_al) && (!p_force_hit)) ||
		|		    ((!p_phit_al) &&   p_force_hit  && (!p_mcyc1) && (cmd == 0x6 || cmd == 0x7 || cmd == 0xe || cmd == 0xf)) ||
		|		    ((!p_phit_al) &&   p_force_hit  && (!p_mcyc1) && (cmd == 0xa || cmd == 0xb)) ||
		|		    ((!p_phit_al) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x8) ||
		|		    ((!p_phit_al) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x5) ||
		|		    (  p_force_hit  && (!p_hit_h) &&   p_mcyc1 );
		|		bool out_logq =
		|		    (  p_tag_57  && (!p_tag_56) &&   p_force_hit  && (!p_mcyc1) && (cmd == 0xc || cmd == 0xd)) ||
		|		    (  p_tag_57  && (!p_tag_56) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x4) ||
		|		    (  p_tag_57  && (!p_tag_56) &&   p_force_hit  && (!p_mcyc1) && cmd == 0x3) ||
		|		    (  p_tag_56  &&                  p_force_hit  && (!p_mcyc1) && cmd == 0x4) ||
		|		    (  p_tag_56  &&                  p_force_hit  && (!p_mcyc1) && cmd == 0x3) ||
		|		    ((!p_tag_57) &&   p_tag_56  &&   p_force_hit  && (!p_mcyc1) && cmd == 0xc);
		|		bool out_soil_q =
		|		    ((!p_tag_51) && (!p_mcyc1) && cmd == 0xd);
		|		bool out_lpar_q =
		|		    ((!p_tag_55) &&   p_tag_54  &&   p_tag_53  &&   p_tag_52 ) ||
		|		    (  p_tag_55  && (!p_tag_54) &&   p_tag_53  &&   p_tag_52 ) ||
		|		    (  p_tag_55  &&   p_tag_54  && (!p_tag_53) &&   p_tag_52 ) ||
		|		    (  p_tag_55  &&   p_tag_54  &&   p_tag_53  && (!p_tag_52)) ||
		|		    ((!p_tag_55) && (!p_tag_54) && (!p_tag_53) &&   p_tag_52 ) ||
		|		    ((!p_tag_55) && (!p_tag_54) &&   p_tag_53  && (!p_tag_52)) ||
		|		    ((!p_tag_55) &&   p_tag_54  && (!p_tag_53) && (!p_tag_52)) ||
		|		    (  p_tag_55  && (!p_tag_54) && (!p_tag_53) && (!p_tag_52));
		|
		|		state->qhit = out_hitq;
		|		state->qlog = out_logq;
		|		state->qsoil = out_soil_q;
		|		state->qlpar = out_lpar_q;
		|		PIN_LOGQ<=(state->qlog);
		|	}
		|	if (pos && late) {
		|		state->hhit = nxthhit;
		|	}
		|	if (pos && !late) {
		|		state->hhit = state->dhit;
		|	}
		|
		|	hit = true;
		|	if (state->qhit)
		|		hit = false;
		|	if (PIN_NMAT=> && PIN_OMAT=> && state->qlog)
		|		hit = false;
		|	PIN_HIT<=(hit);
		|
		|	if (late) {
		|		state->oeq = !(
		|			PIN_LRUP=> && !hit
		|		);
		|	}
		|
		|	if (!state->oeq) {
		|		BUS_HLRU_WRITE(state->qlru);
		|		hrlu = state->qlru;
		|	} else if (!state->oeh) {
		|		BUS_HLRU_WRITE(state->dlru);
		|		hrlu = state->dlru;
		|	} else {
		|		BUS_HLRU_Z();
		|		hrlu = BUS_HLRU_MASK + 1;
		|	}
		|
		|	unsigned wrd = BUS_WRD_MASK + 1;
		|	if (pos) {
		|		if (state->oeu) {
		|			BUS_WRD_Z();
		|		}
		|	}
		|	if (!state->oeu) {
		|		unsigned lri;
		|		wrd = 0;
		|		wrd |= state->t49d << 7;
		|		wrd |= state->t50d << 6;
		|		wrd |= state->modd << 5;
		|		BUS_LRI_READ(lri);
		|		if (state->lrua < lri) {
		|			wrd |= state->lrub << 1;
		|			wrd |= state->parb;
		|		} else {
		|			wrd |= state->lrua << 1;
		|			wrd |= state->para;
		|		}
		|		wrd ^= 0xff;
		|		BUS_WRD_WRITE(wrd);
		|	}
		|
		|	TRACE(
		|		<< " late " << late
		|		<< " clk^v " << pos << neg
		|		<< " n " << PIN_NMAT?
		|		<< " o " << PIN_OMAT?
		|		<< " up " << PIN_LRUP?
		|		<< " i " << BUS_LRI_TRACE()
		|		<< " - "
		|		<< " f " << PIN_MRIF?
		|		<< " h1 " << PIN_H1?
		|		<< " par " << PIN_PAR?
		|		<< " fh " << PIN_FHIT?
		|		<< " ph " << PIN_PHIT?
		|		<< " c1 " << PIN_CYC1?
		|		<< " cmd " << BUS_CMD_TRACE()
		|		<< " tag " << BUS_TAG_TRACE()
		|		<< " - "
		|		<< " " << std::hex << state->qhit
		|		<< " " << std::hex << state->qlog
		|		<< " " << std::hex << state->qsoil
		|		<< " " << std::hex << state->dsoil
		|		<< " " << std::hex << state->qt49
		|		<< " " << std::hex << state->qt50
		|		<< " " << std::hex << state->qmod
		|		<< " " << std::hex << state->qlpar
		|		<< " " << std::hex << state->dlpar
		|		<< " " << std::hex << state->dpar6
		|		<< " " << std::hex << state->qlru
		|		<< " " << std::hex << state->dlru
		|		<< " " << std::hex << state->dhit
		|		<< " " << std::hex << state->hhit
		|		<< " " << std::hex << state->qpar
		|		<< " " << std::hex << state->oeq
		|		<< " " << std::hex << state->oeh
		|		<< " " << std::hex << state->oeu
		|		<< " " << std::hex << state->t49d
		|		<< " " << std::hex << state->t50d
		|		<< " " << std::hex << state->modd
		|		<< " " << std::hex << state->t49m
		|		<< " " << std::hex << state->t50m
		|		<< " " << std::hex << state->modm
		|		<< " " << std::hex << state->lrua
		|		<< " " << std::hex << state->lrub
		|		<< " " << std::hex << state->para
		|		<< " " << std::hex << state->parb
		|		<< " - "
		|		<< " hrlu " << std::hex << hrlu
		|		<< " hit " << hit
		|		<< " oeu " << state->oeu
		|		<< " wrd " << std::hex << wrd
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XLRU", PartModel("XLRU", XLRU))
