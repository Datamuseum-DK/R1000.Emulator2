#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   LRU logic
   =========

'''


from part import PartModel, PartFactory

class XLRULOGIC(PartFactory):

    ''' The LRU logic'''

    def state(self, file):
        file.fmt('''
		|	unsigned qd;		// PAR6,49,50,MOD,LRU0,LRU1,LRU2,LRU3
		|	unsigned xd;		// PAR6,49,50,MOD,LRU0,LRU1,LRU2,LRU3 pin13-15
		|	unsigned hd;		// SOIL,LPAR,LRU0,LRU1,LRU2,LRU3,PAR6,HIT
		|	unsigned lrud;		// LRU#~D
		|	unsigned lruupd;	// LRU#~UPD
		|	bool par_d;
		|	bool par_upd;
		|	bool lru_upd_oe;
		|	bool hit_hd;
		|	bool lru_0_oe;
		|	bool lru_1_oe;
		|	bool lpar_qd;
		|	bool soil_qd;
		|	bool logq;
		|	bool hitq;
		|	bool hith;
		|	unsigned lhit;
		|	unsigned tag_d;		// -,49,50,MOD,-,-,-,-
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        if 1 and self.comp.nodes["LATE"].net.is_pu():
            yield "PIN_HITQ"
        yield "PIN_NMATCH"
        yield "PIN_LRU_UPDATE"
        yield "PIN_OMATCH"
        yield "BUS_LHIT_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool hitpin, didlate = false;
		|	unsigned hitbus = 0;
		|
		|	if (state->hitq) {
		|		hitpin = false;
		|	} else if (PIN_NMATCH=> && PIN_OMATCH=> && state->logq) {
		|		hitpin = false;
		|	} else {
		|		hitpin = true;
		|	}
		|
		|	if (PIN_CLK.negedge() && PIN_H1=>) { // GOOD
		|		BUS_HITLRU_READ(state->lhit);
		|		state->lhit ^= 0xf;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		didlate = true;
		|
		|		// MUXxPAL
		|		state->lru_upd_oe = !PIN_LRU_UPDATE;
		|
		|		if (PIN_LATE=>) {
		|			// MUXLPAL
		|			state->hit_hd = state->hd & 1;
		|			state->tag_d = 0x70 ^ (state->qd & 0x70);
		|			if (state->soil_qd && (!(state->hd & 1)))
		|				state->tag_d &= ~0x10;
		|			state->lru_1_oe = !(
		|				PIN_LRU_UPDATE=> &&
		|				(!PIN_H1=>) &&
		|				(!(state->hd & 1))
		|			);
		|		} else {
		|			// MUXEPAL
		|			state->tag_d = 0x70 ^ state->xd;
		|			if ((state->hd & 0x80) && (!(state->hd & 1)))
		|				state->tag_d &= ~0x10;
		|			state->xd = state->qd & 0x70;
		|			state->lru_0_oe = !(
		|				PIN_LRU_UPDATE=> &&
		|				(!PIN_H1=>) &&
		|				(!hitpin)
		|			);
		|			state->lru_1_oe = !(
		|				PIN_LRU_UPDATE=> &&
		|				(!PIN_H1=>) &&
		|				(!(state->hd & 1))
		|			);
		|		}
		|		
		|		// LUXXPAL
		|		bool mruisf = PIN_MRUIS_F=>;
		|		unsigned lru = (state->hd & 0x3c) >> 2;
		|		if (state->hd & 0x01) {
		|			state->lrud = lru;
		|			if (lru > 1)
		|				state->lruupd = lru - 1;
		|			else
		|				state->lruupd = 0x0;
		|		} else if (mruisf) {
		|			state->lrud = 0xf;
		|			state->lruupd = 0xf;
		|		} else {
		|			state->lrud = 0x7;
		|			state->lruupd = 0x7;
		|		}
		|
		|		unsigned par_d = state->hd >> 1; // PAR6
		|		if (!(state->hd & 0x01)) {
		|			if (state->hd & 0x80) par_d++;	// SOIL
		|			if (state->hd & 0x40) par_d++;	// LPAR
		|			if (mruisf) par_d++;
		|			par_d += 1;
		|		}
		|		state->par_d = !(par_d & 1);
		|
		|		unsigned par_upd = 0;
		|		if (!(state->hd & 0x01)) {
		|			if (state->hd & 0x02) par_upd++;	// PAR6
		|			if (state->hd & 0x80) par_upd++;	// SOIL
		|			if (state->hd & 0x40) par_upd++;	// LPAR
		|			if (mruisf) par_upd++;
		|			par_upd += 1;
		|		} else {
		|			switch(lru) {
		|			case 0x2:
		|			case 0x6:
		|			case 0x8:
		|			case 0xa:
		|			case 0xe:
		|				par_upd = state->hd >> 1;
		|				break;
		|			case 0x0:
		|			case 0x1:
		|			case 0x3:
		|			case 0x4:
		|			case 0x5:
		|			case 0x7:
		|			case 0x9:
		|			case 0xb:
		|			case 0xc:
		|			case 0xd:
		|			case 0xf:
		|				par_upd = 1 ^ (state->hd >> 1);
		|				break;
		|			}
		|		}
		|		state->par_upd = !(par_upd & 1);
		|
		|	}
		|
		|	if (PIN_LATE=>) {
		|		state->lru_0_oe = !(
		|			(
		|				PIN_LRU_UPDATE=> &&
		|				(!hitpin)
		|			)
		|		);
		|	}
		|
		|	int hitl;
		|	if (!state->lru_0_oe) {
		|		hitl = state->qd & 0x0f;
		|		BUS_HITLRU_WRITE(state->qd & 0x0f);
		|	} else if (!state->lru_1_oe) {
		|		hitl = (state->hd >> 2) & 0x0f;
		|		BUS_HITLRU_WRITE((state->hd >> 2) & 0x0f);
		|	} else {
		|		hitl = -1;
		|		BUS_HITLRU_Z();
		|	}
		|
		|	int hitb;
		|	unsigned lhit;
		|	BUS_LHIT_READ(lhit);
		|	//if (lhit != state->lhit) printf("LH %x %x\\n", lhit, state->lhit);
		|	// lhit = state->lhit;
		|	if ((0x0f ^ state->lrud) < lhit) {
		|		hitbus |= (~state->lruupd) & 0xf;
		|		if (state->par_upd) {
		|			hitbus |= 1 << 7;
		|		}
		|	} else {
		|		hitbus |= (~state->lrud) & 0xf;
		|		if (state->par_d) {
		|			hitbus |= 1 << 7;
		|		}
		|	}
		|	hitbus |= state->tag_d;
		|
		|	if (state->lru_upd_oe) {
		|		hitb = -1;
		|		BUS_TAG_Z();
		|	} else {
		|		hitb = hitbus ^ 0xff;
		|		BUS_TAG_WRITE(hitbus ^ 0xff);
		|	}		
		|
		|	if (PIN_CLK.negedge()) {
		|		// Middle register
		|		state->hd = (state->qd & 0xf) << 2;
		|		state->hd |= (state->qd >> 7) << 1;
		|		if (hitpin)
		|			state->hd |= 1;
		|		if (state->soil_qd)
		|			state->hd |= 0x80;
		|		if (state->lpar_qd)
		|			state->hd |= 0x40;
		|	}
		|
		|	if ((PIN_LATE=> && PIN_CLK.posedge()) ||
		|	   (!(PIN_LATE=>) && PIN_CLK.negedge())) {
		|
		|		// First register
		|		BUS_TAG_READ(state->qd);
		|
		|		// TSXXPAL
		|
		|		unsigned cmd;
		|		BUS_CMD_READ(cmd);
		|
		|		unsigned u = 0;
		|		if (state->qd & 0x01) u++;
		|		if (state->qd & 0x02) u++;
		|		if (state->qd & 0x04) u++;
		|		if (state->qd & 0x08) u++;
		|		state->lpar_qd = u & 1;
		|
		|		bool cyc1 = PIN_MCYC1;
		|
		|		if (cmd == 0xd && !cyc1 && !(state->qd & 0x10))
		|			state->soil_qd = true;
		|		else
		|			state->soil_qd = false;
		|
		|		bool tag56 = PIN_ITAG56=>;
		|		bool tag57 = PIN_ITAG57=>;
		|		bool phit = PIN_PHIT=>;
		|		bool fhit = PIN_FORCE_HIT=>;
		|		state->logq = false;
		|		if (fhit && !cyc1) {
		|			if (tag57 && !tag56 &&
		|			    (cmd == 0xc || cmd == 0xd ||
		|			     cmd == 0x4 || cmd == 0x3))
		|				state->logq = true;
		|			if (tag56 && (
		|			     cmd == 0x4 || cmd == 0x3))
		|				state->logq = true;
		|			if (!tag57 && tag56 && cmd == 0xc)
		|				state->logq = true;
		|		}
		|		PIN_TMP1<=(state->logq);
		|
		|		state->hitq = false;
		|
		|		if (!phit && !fhit)
		|			state->hitq = true;
		|
		|		if (!cyc1) {
		|			if (!(state->qd & 0xf) && fhit && cmd == 0x2)
		|				state->hitq = true;
		|
		|			if (!tag56 && !tag57 && fhit && cmd == 0x1)
		|				state->hitq = true;
		|
		|			if (!phit && fhit &&
		|			    (cmd == 0x5 || cmd == 0x6 || cmd == 0x7 || cmd == 0x08
		|			    || cmd == 0xa || cmd == 0x0b || cmd == 0x0e || cmd == 0xf))
		|				state->hitq = true;
		|
		|			if (fhit && !state->hith && cmd == 9)
		|				state->hitq = true;
		|		} else {
		|			if (fhit && !state->hith)
		|				state->hitq = true;
		|		}
		|
		|	}
		|	PIN_TMP2<=(state->hitq);
		|
		|	if (state->hitq) {
		|		hitpin = false;
		|	} else if (PIN_NMATCH=> && PIN_OMATCH=> && state->logq) {
		|		hitpin = false;
		|	} else {
		|		hitpin = true;
		|	}
		|
		|	if (didlate) {
		|		if (PIN_LATE=>) {
		|			state->hith = state->hit_hd;
		|		} else {
		|			state->hith = state->hd & 1;
		|		}
		|	}
		|	PIN_TMP0<=(state->hith);
		|	PIN_HIT<=(hitpin);
		|
		|	TRACE(
		|	    << " clk↑↓ " << PIN_CLK.posedge() << PIN_CLK.negedge()
		|''')
        if self.comp.nodes["LATE"].net.is_pu():
            file.fmt('''
		|	    << " hitq↑↓ " << PIN_HITQ.posedge() << PIN_HITQ.negedge()
		|''')
        else:
            file.fmt('''
		|	    << " hitq↑↓ ??" 
		|''')
        file.fmt('''
		|	    << " nmatch↑↓ " << PIN_NMATCH.posedge() << PIN_NMATCH.negedge()
		|	    << " omatch↑↓ " << PIN_OMATCH.posedge() << PIN_OMATCH.negedge()
		|	    << " cyc1 " << PIN_MCYC1?
		|	    << " cmd " << BUS_CMD_TRACE()
		|	    << " h1 " << PIN_H1?
		|	    << " late " << PIN_LATE?
		|	    << " lhit " << BUS_LHIT_TRACE()
		|	    << " hitlru " << BUS_HITLRU_TRACE()
		|	    << " hitpin " << hitpin
		|	    << " hitq " << state->hitq
		|	    << " hith " << state->hith
		|	    << " hithd " << state->hit_hd
		|	    << " hitl " << hitl
		|	    << " hitb " << hitb
		|	    << " phit " << PIN_PHIT?
		|	    << " fhit " << PIN_FORCE_HIT?
		|	    << " logq " << state->logq
		|	    << " lru " << state->lru_0_oe << state->lru_1_oe
		|	    << " tag " << BUS_TAG_TRACE()
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XLRULOGIC", PartModel("XLRULOGIC", XLRULOGIC))
