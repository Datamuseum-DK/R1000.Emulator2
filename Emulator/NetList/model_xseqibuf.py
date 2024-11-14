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
   SEQ Instruction buffer
   ======================

			VAL                                             TYP
IR0     IR1     IR2     0-32            32-47           48-63           0-31            32-63
0       0       0       TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE_VAL.OE~    TYPE VAL BUS
0       0       1       OFFS.OE~        OFFS.OE~        CUR_INSTRA.OE~  CUR_NAME.OE~    OFFS.OE~        CURRENT MACRO INSTRUCTION
0       1       0       OFFS.OE~        OFFS.OE~        DECODE.OE~      CUR_NAME.OE~    OFFS.OE~        DECODING MACRO INSTRUCTION
0       1       1       OFFS.OE~        OFFS.OE~        TOP_STACK.OE~   CUR_NAME.OE~    OFFS.OE~        TOP OF THE MICRO STACK
1       0       0       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        SAVE OFFSET
1       0       1       OFFS.OE~        OFFS.OE~        PC.OE~          REF_NAME.OE~    OFFS.OE~        RESOLVE RAM
1       1       0       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        CONTROL TOP
1       1       1       OFFS.OE~        OFFS.OE~        PC.OE~          CUR_NAME.OE~    OFFS.OE~        CONTROL PRED
'''

from part import PartModelDQ, PartFactory

class XSEQIBUF(PartFactory):
    ''' SEQ Instruction buffer '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t top[1<<10];	// Z020
		|	uint32_t bot[1<<10];	// Z020
		|	uint16_t nxtuadr;	// Z020
		|	uint16_t curuadr;	// Z020
		|	uint32_t cbot, ctop;
		|	unsigned emac;
		|	unsigned curins;
		|	bool topbot;
		|
		|	uint64_t typ, val;
		|	unsigned word;
		|	unsigned mpc;
		|	unsigned curr_lex;
		|	unsigned retrn_pc_ofs;
		|	unsigned boff;
		|	unsigned break_mask;
		|
		|	// XSEQNAM
		|	uint32_t tost, vost, cur_name;
		|	uint32_t namram[1<<BUS_RSAD_WIDTH];
		|	unsigned pcseg, retseg, last;
		|
		|	uint64_t tosram[1<<BUS_RSAD_WIDTH];
		|	uint64_t tosof;
		|	uint32_t savrg;
		|	uint32_t pred;
		|	uint32_t topcnt;
		|
		|	// XUSTK
		|	uint16_t ram[16];
		|	uint16_t topu;
		|	uint16_t adr;
		|	unsigned fiu;
		|	unsigned other;
		|	unsigned late_u;
		|	unsigned prev;
		|	unsigned uei;
		|	unsigned uev;
		|
		|	uint8_t prom43[512];
		|	uint8_t prom44[512];
		|	uint8_t bhreg;
		|	unsigned rreg;
		|	unsigned lreg;
		|	unsigned treg;
		|	bool hint_last;
		|	bool hint_t_last;
		|	bool last_late_cond;
		|	bool uadr_mux, preturn, push_br, push;
		|	uint64_t typ_bus;
		|	uint64_t val_bus;
		|	uint64_t output_ob;
		|	uint64_t name_bus;
		|	unsigned coff;
		|	unsigned uadr_decode;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom43, sizeof state->prom43,
		|	    "PA043-02");
		|	load_programmable(this->name(),
		|	    state->prom44, sizeof state->prom44,
		|	    "PA044-01");
		|''')

    def xsensitive(self):
        yield "PIN_ACLK.pos()"
        yield "PIN_BCLK.pos()"
        yield "PIN_CLCLK.pos()"
        # yield "PIN_CNDLD"		# BCLK
        # yield "PIN_DISPA"		# ACLK
        # yield "BUS_EMAC"		# ACLK
        yield "PIN_FLIP.pos()"
        yield "PIN_ICLK.pos()"
        # yield "PIN_ILDRN"		# ACLK
        # yield "PIN_IMX"		# ACLK
        yield "BUS_IRD"
        yield "BUS_LAUIR"
        yield "PIN_LINC"
        # yield "PIN_MD0"		# BCLK
        yield "PIN_MIBMT"
        yield "PIN_MUX"
        yield "PIN_QVOE"
        yield "BUS_RASEL"
        yield "PIN_RTCLK.pos()"
        # yield "PIN_RND1"		# BCLK
        yield "PIN_SCLKE"
        # yield "BUS_TYP"		# ICLK
        yield "BUS_URAND"
        yield "BUS_DV"
        yield "PIN_WDISP"

    def priv_decl(self, file):
        file.fmt('''
		|	void int_reads(unsigned ir);
		|	unsigned group_sel(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|int_reads(unsigned ir)
		|{
		|	if (ir == 0) {
		|		BUS_DT_READ(state->typ_bus);
		|		state->typ_bus ^= BUS_DT_MASK;
		|		BUS_DV_READ(state->val_bus);
		|		state->val_bus ^= BUS_DV_MASK;
		|		return;
		|	}		
		|
		|	BUS_CSA_READ(state->typ_bus);
		|	state->typ_bus |= state->output_ob << 7;
		|	state->typ_bus ^= 0xffffffff;
		|
		|	switch (ir) {
		|	case 5:
		|		state->typ_bus |= (uint64_t)(state->name_bus ^ 0xffffffff) << 32;
		|		break;
		|	default:
		|		state->typ_bus |= (uint64_t)state->cur_name << 32;
		|		break;
		|	}
		|
		|	
		|	if (!PIN_CSEL) {
		|		state->val_bus = (uint64_t)state->pcseg << 32;
		|	} else {
		|		state->val_bus = (uint64_t)state->retseg << 32;
		|	}
		|	state->val_bus ^= 0xffffffffULL << 32; 
		|	state->val_bus ^= (uint64_t)(state->coff >> 12) << 16;
		|	state->val_bus ^= 0xffffULL << 16; 
		|	switch (ir) {
		|	case 1:
		|		state->val_bus |= state->curins ^ 0xffff;
		|		break;
		|	case 2:
		|		state->val_bus |= output.disp;
		|		break;
		|	case 3:
		|		state->val_bus |= state->topu & 0xffff;
		|		break;
		|	default:
		|		state->val_bus |= (state->coff << 4) & 0xffff;
		|		state->val_bus |= (state->curr_lex & 0xf);
		|		state->val_bus ^= 0xffff;
		|		break;
		|	}
		|}
		|
		|unsigned
		|SCM_«mmm» ::
		|group_sel(void)
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	unsigned retval;
		|	switch(br_type) {
		|	case 0x0: retval = 3; break;
		|	case 0x1: retval = 3; break;
		|	case 0x2: retval = 3; break;
		|	case 0x3: retval = 3; break;
		|	case 0x4: retval = 3; break;
		|	case 0x5: retval = 3; break;
		|	case 0x6: retval = 3; break;
		|	case 0x7: retval = 3; break;
		|	case 0x8: retval = 2; break;
		|	case 0x9: retval = 2; break;
		|	case 0xa: retval = 2; break;
		|	case 0xb: retval = 0; break;
		|	case 0xc: retval = 1; break;
		|	case 0xd: retval = 1; break;
		|	case 0xe: retval = 1; break;
		|	case 0xf: retval = 0; break;
		|	}
		|	if (state->uadr_mux) {
		|		retval |= 4;
		|	}
		|	return (retval);
		|}
		|''')


    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool aclk = PIN_ACLK.posedge();
		|	bool sclk = aclk && !PIN_SCLKE=>;
		|
		|	unsigned internal_reads;
		|	BUS_IRD_READ(internal_reads);
		|
		|	int_reads(internal_reads);
		|
		|{
		|	if (PIN_ICLK.posedge()) {
		|		state->typ = state->typ_bus;
		|		state->val = state->val_bus;
		|	}
		|
		|	unsigned macro_pc_ofs = state->mpc;
		|
		|	if (PIN_RTCLK.posedge()) {
		|		state->retrn_pc_ofs = state->mpc;
		|	}
		|
		|	bool wdisp = PIN_WDISP;
		|	bool mibmt = PIN_MIBMT;
		|	bool oper;
		|	unsigned a;
		|	if (!wdisp && !mibmt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!wdisp && mibmt) {
		|		a = output.disp;
		|		oper = false;
		|	} else if (wdisp && !mibmt) {
		|		a = state->curins;
		|		oper = true;
		|	} else {
		|		a = state->curins;
		|		oper = true;
		|	}
		|	a &= 0x7ff;
		|	if (a & 0x400)
		|		a |= 0x7800;
		|	a ^= 0x7fff;
		|	unsigned b = macro_pc_ofs & 0x7fff;
		|	if (oper) {
		|		if (wdisp)
		|			a += 1;
		|		a &= 0x7fff;
		|		state->boff = a + b;
		|	} else {
		|		if (!wdisp)
		|			a += 1;
		|		state->boff = b - a;
		|	}
		|	state->boff &= 0x7fff;
		|	output.bridx = state->boff & 7;
		|
		|	if (PIN_BCLK.posedge()) {
		|		unsigned mode = 0;
		|		unsigned u = 0;
		|		if (PIN_CNDLD=>) u |= 1;
		|		if (PIN_WDISP=>) u |= 2;
		|		switch (u) {
		|		case 0: mode = 1; break;
		|		case 1: mode = 1; break;
		|		case 3: mode = 0; break;
		|		case 2:
		|			if (PIN_MD0=>) mode |= 2;
		|			if (PIN_RND1=>) mode |= 1;
		|			break;
		|		}
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			if (!PIN_MUX=>) {
		|				tmp = state->val_bus;
		|				state->word = (tmp >> 4) & 7;
		|				state->mpc = (tmp >> 4) & 0x7fff;
		|			} else {
		|				state->mpc = state->boff;
		|				state->word = state->boff & 7;
		|			}
		|		} else if (mode == 2) {
		|			state->mpc += 1;
		|			state->word += 1;
		|			if (state->word == 0x8)
		|				state->word = 0;
		|		} else if (mode == 1) {
		|			state->mpc -= 1;
		|			if (state->word == 0x0)
		|				state->word = 7;
		|			else
		|				state->word -= 1;
		|		}
		|	}
		|
		|	unsigned rand;
		|	BUS_URAND_READ(rand);
		|	switch (rand & 3) {
		|	case 3:	state->coff = state->retrn_pc_ofs; break;
		|	case 2: state->coff = state->boff; break;
		|	case 1: state->coff = state->mpc; break;
		|	case 0: state->coff = state->boff; break;
		|	}
		|	state->coff ^= 0x7fff;;
		|
		|	unsigned disp = output.disp;
		|
		|	output.empty = state->word != 0;
		|
		|	if (state->word == 7)
		|		output.disp = state->typ >> 48;
		|	else if (state->word == 6)
		|		output.disp = state->typ >> 32;
		|	else if (state->word == 5)
		|		output.disp = state->typ >> 16;
		|	else if (state->word == 4)
		|		output.disp = state->typ >> 0;
		|	else if (state->word == 3)
		|		output.disp = state->val >> 48;
		|	else if (state->word == 2)
		|		output.disp = state->val >> 32;
		|	else if (state->word == 1)
		|		output.disp = state->val >> 16;
		|	else if (state->word == 0)
		|		output.disp = state->val >> 0;
		|	else
		|		output.disp = 0xffff;
		|	output.disp &= 0xffff;
		|
		|	unsigned val, iclex;
		|
		|	val = state->val_bus;
		|	iclex = (val & 0xf) + 1;
		|
		|	if (PIN_CLCLK.posedge()) {
		|		state->curr_lex = val & 0xf;
		|		state->curr_lex ^= 0xf;
		|	}
		|	unsigned sel, res_addr = 0;
		|	BUS_RASEL_READ(sel);
		|	switch (sel) {
		|	case 0:
		|		if (PIN_LAUIR0=> && PIN_LAUIR1=>)
		|			res_addr = 0xe;
		|		else
		|			res_addr = 0xf;
		|		break;
		|	case 1:
		|		res_addr = (output.disp >> 9) & 0xf;
		|		break;
		|	case 2:
		|		res_addr = iclex;
		|		break;
		|	case 3:
		|		res_addr = state->curr_lex ^ 0xf;
		|		break;
		|	default:
		|		assert(sel < 4);
		|	}
		|	output.radr = res_addr;
		|	if (PIN_LINC=>) {
		|		output.icond = true;
		|		output.sext = true;
		|	} else {
		|		output.icond = !(res_addr == 0xf);
		|		output.sext = !((res_addr > 0xd));
		|	}
		|
		|	if (aclk) {
		|		BUS_EMAC_READ(state->emac);
		|		output.me = state->emac;
		|		output.emp = state->emac != BUS_EMAC_MASK;
		|	}
		|	if (state->emac != BUS_EMAC_MASK) {
		|		unsigned uad = 0;
		|		if (!(state->emac & 0x40))
		|			uad = 0x04e0;
		|		else if (!(state->emac & 0x20))
		|			uad = 0x04c0;
		|		else if (!(state->emac & 0x10))
		|			uad = 0x04a0;
		|		else if (!(state->emac & 0x08))
		|			uad = 0x0480;
		|		else if (!(state->emac & 0x04))
		|			uad = 0x0460;
		|		else if (!(state->emac & 0x02))
		|			uad = 0x0440;
		|		else if (!(state->emac & 0x01))
		|			uad = 0x0420;
		|		// output.uad = uad;
		|		output.ustos = (uad >> 2) & 1;
		|		output.ibfil = (uad >> 1) & 1;
		|		state->uadr_decode = uad;
		|	} else {
		|		unsigned ai = disp;
		|		ai ^= 0xffff;
		|		bool top = (disp >> 10) != 0x3f;
		|		uint32_t *ptr;
		|		if (top)
		|			ptr = &state->top[ai >> 6];
		|		else
		|			ptr = &state->bot[ai & 0x3ff];
		|		unsigned uad = (*ptr >> 16);
		|		//output.uad = uad;
		|		output.ustos = (uad >> 2) & 1;
		|		output.ibfil = (uad >> 1) & 1;
		|		state->uadr_decode = (*ptr >> 16);
		|		output.dec = (*ptr >> 8) & BUS_DEC_MASK;
		|	}
		|
		|	if (sclk) {
		|		unsigned dsp = 0;
		|		if (!PIN_IMX=>) {
		|			dsp = disp;
		|		} else {
		|			uint64_t tval = state->val_bus;
		|			dsp = tval & 0xffff;
		|		}
		|		dsp ^= 0xffff;;
		|
		|		bool gate = !(PIN_ILDRN=> && PIN_DISPA=>);
		|		if (gate && state->topbot)
		|			state->ctop = dsp;
		|		if (gate && !state->topbot)
		|			state->cbot = dsp;
		|	}
		|
		|	if (PIN_FLIP.posedge()) {
		|		state->topbot = !state->topbot;
		|	}
		|
		|	if (state->topbot)
		|		state->curins = state->cbot;
		|	else
		|		state->curins = state->ctop;
		|
		|	if (sclk && !PIN_BMCLK=>) {
		|		uint64_t tmp = state->val_bus;
		|		state->break_mask = (tmp >> 16) & 0xffff;
		|	}
		|
		|	uint32_t *ciptr;
		|	if (state->curins & 0xfc00) {
		|		ciptr = &state->top[state->curins >> 6];
		|	} else {
		|		ciptr = &state->bot[state->curins & 0x3ff];
		|	}
		|
		|	unsigned ccl = (*ciptr >> 4) & 0xf;
		|
		|	if (ccl == 0) {
		|		output.bmcls = false;
		|	} else {
		|		output.bmcls = (state->break_mask >> (15 - ccl)) & 1;
		|	}
		|	output.bmcls = !output.bmcls;
		|
		|}
		|{
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
		|		intreads1 = !((internal_reads >> 1) & 1);
		|		intreads2 = !((internal_reads >> 0) & 1);
		|		sel1 = false;
		|		sel2 = true;
		|	} else {
		|		uses_tos = (state->uadr_decode >> 2) & 1;
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
		|	unsigned typl = state->typ_bus & 0xffffffff;
		|
		|	output.z_ospc = PIN_OSPCOE=>;
		|	if (!output.z_ospc) {
		|		BUS_ISPC_READ(output.ospc);
		|		output.ospc ^= BUS_OSPC_MASK;
		|	}
		|
		|	if (PIN_TOSCLK.posedge()) {
		|		state->tost = state->typ_bus >> 32;
		|		state->vost = state->val_bus >> 32;
		|		state->tosof = (typl >> 7) & 0xfffff;
		|	}
		|
		|	if (PIN_CNCK.posedge()) {
		|		state->cur_name = state->typ_bus >> 32;
		|	}
		|
		|	if (PIN_RAMWE.posedge()) {
		|		unsigned radr;
		|		BUS_RSAD_READ(radr);
		|		state->namram[radr] = state->typ_bus >> 32;
		|	}
		|
		|	if (!type_name_oe) {
		|		state->name_bus = state->tost ^ 0xffffffff;
		|	} else if (!val_name_oe) {
		|		state->name_bus = state->vost ^ 0xffffffff;
		|	} else if (!name_ram_cs) {
		|		unsigned radr;
		|		BUS_RSAD_READ(radr);
		|		state->name_bus = state->namram[radr] ^ 0xffffffff;
		|	} else {
		|		state->name_bus = 0xffffffff;
		|	}
		|
		|	if (PIN_RTCLK.posedge()) {
		|		state->retseg = state->pcseg;
		|	}
		|	if (PIN_MCLK.posedge()) {
		|		unsigned val;
		|		val = state->val_bus >> 32;
		|		val ^= 0xffffffff;
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
		|				output.adrn = state->name_bus;
		|			}
		|		}
		|
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
		|		BUS_RSAD_READ(res_adr);
		|		if (PIN_RWE.posedge()) {
		|			state->tosram[res_adr] = (typl >> 7) & 0xfffff;
		|		}
		|		offs = state->tosram[res_adr];
		|	}
		|	offs ^= 0xfffff;
		|       offs &= 0xfffff;
		|
		|       unsigned disp;
		|       BUS_DSPL_READ(disp);
		|	//disp = output.disp;
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
		|		uint64_t cnb;
		|		if (!PIN_CMR=>) {
		|			cnb = typl ^ 0xffffffffULL;
		|		} else {
		|			BUS_DF_READ(cnb);
		|			cnb &= 0xffffffffULL;
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
		|	if (dis) {
		|		state->output_ob = 0xfffff;
		|	} else if (intreads == 0) {
		|		state->output_ob = state->pred;
		|	} else if (intreads == 1) {
		|		state->output_ob = state->topcnt;
		|	} else if (intreads == 2) {
		|		state->output_ob = resolve_offset;
		|	} else if (intreads == 3) {
		|		state->output_ob = state->savrg;
		|	} else {
		|		state->output_ob = 0xfffff;
		|	}
		|	state->output_ob &= 0xfffff;
		|
		|	output.z_nam = PIN_NAMOE=>;
		|	if (!output.z_nam) {
		|		if (!PIN_RESDR=>) {
		|			output.nam = resolve_offset;
		|		} else if (PIN_ADRICD=>) {
		|			//BUS_CODE_READ(output.nam);
		|			output.nam = state->coff >> 3;
		|		} else {
		|			output.nam = state->output_ob;
		|		}
		|		output.nam <<= 7;
		|
		|		unsigned branch;
		|		BUS_BRNC_READ(branch);
		|		branch ^= BUS_BRNC_MASK;
		|		output.nam |= branch << 4;
		|	}
		|
		|}
		|{
		|	bool q2pos = PIN_Q2.posedge();
		|	bool stkclk = PIN_Q4.posedge() && PIN_SSTOP=> && output.macro_hic;
		|	bool uevent = output.u_event;
		|
		|	if (q2pos) {
		|		state->ram[(state->adr + 1) & 0xf] = state->topu;
		|	}
		|
		|	if (stkclk) {
		|		bool xwrite;
		|		bool pop;
		|		bool stkinpsel_0;
		|		bool stkinpsel_1;
		|		if (uevent) {
		|			xwrite = true;
		|			pop = true;
		|			stkinpsel_0 = true;
		|			stkinpsel_1 = true;
		|		} else if (!state->push) {
		|			xwrite = true;
		|			pop = false;
		|			stkinpsel_0 = !state->push_br;
		|			stkinpsel_1 = output.bhp;
		|		} else {
		|			xwrite = !PIN_PUSHRND=>;
		|			pop = !!(state->preturn || PIN_POPRND=>);
		|			stkinpsel_0 = false;
		|			stkinpsel_1 = true;
		|		}
		|
		|		unsigned stkinpsel = 0;
		|		if (stkinpsel_0) stkinpsel |= 2;
		|		if (stkinpsel_1) stkinpsel |= 1;
		|
		|		if (xwrite) {
		|			switch(stkinpsel) {
		|			case 0:
		|				BUS_BRN_READ(state->topu);
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 1:
		|				BUS_DF_READ(state->topu);
		|				state->topu &= 0xffff;
		|				break;
		|			case 2:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 3:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (output.ldc) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			}
		|		} else if (pop) {
		|			state->topu = state->ram[state->adr];
		|		}
		|		output.svlat = !((state->topu >> 14) & 0x1);
		|
		|		if (PIN_CSR=> && PIN_STOP=>) {
		|			state->adr = xwrite;
		|		} else if (xwrite || pop) {
		|			if (xwrite) {
		|				state->adr = (state->adr + 1) & 0xf;
		|			} else {
		|				state->adr = (state->adr + 0xf) & 0xf;
		|			}
		|		}
		|		output.ssz = state->adr == 0;
		|	}
		|
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = state->topu ^ 0xffff;
		|		output.qf ^= 0xffff;
		|	}
		|
		|	unsigned data = 0, sel;
		|	bool macro_hic = true;
		|	bool u_event = true;
		|
		|	if (PIN_FIU_CLK.posedge()) {
		|		BUS_DF_READ(state->fiu);
		|		state->fiu &= 0x3fff;
		|	}
		|
		|	if (PIN_LCLK.posedge()) {
		|		BUS_LATE_READ(state->late_u);
		|		sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|		case 7:
		|			data = state->curuadr;
		|			data += 1;
		|			break;
		|		case 1:
		|		case 2:
		|		case 3:
		|			BUS_BRN_READ(data);
		|			break;
		|		case 4:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 5:
		|			data = output.dec >> 3;
		|			data <<= 1;
		|			break;
		|		case 6:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		default:
		|			abort();
		|		}
		|		state->other = data;
		|	}
		|
		|	if (!PIN_DV_U) {
		|		data = state->nxtuadr;
		|	} else if (output.bhp) {
		|		data = state->other;
		|	} else if (PIN_LMAC=>) {
		|		// Not tested by expmon_test_seq ?
		|		data = state->late_u << 3;
		|		data ^= (7 << 3);
		|		data |= 0x0140;
		|		macro_hic = false;
		|	} else if (state->uei != 0) {
		|		data = state->uev;
		|		data <<= 3;
		|		data |= 0x0180;
		|		u_event = false;
		|	} else {
		|		sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|			BUS_BRN_READ(data);
		|			data += state->fiu;
		|			break;
		|		case 1:
		|			data = state->uadr_decode >> 3;
		|			data <<= 1;
		|			break;
		|		case 2:
		|			data = (state->topu ^ 0xffff) & 0x3fff;
		|			break;
		|		case 3:
		|		case 4:
		|			data = state->curuadr;
		|			data += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			BUS_BRN_READ(data);
		|			break;
		|		default:
		|			abort();
		|		}
		|	}
		|	if (q2pos) {
		|
		|		output.nu = data;
		|	}
		|
		|	output.macro_hic = macro_hic;
		|	output.u_event = !u_event;
		|	output.u_eventnot = u_event;
		|
		|	if (PIN_ACK.posedge()) {
		|		BUS_UEI_READ(state->uei);
		|		state->uei <<= 1;
		|		state->uei |= 1;
		|		state->uei ^= 0xffff;
		|		state->uev = 16 - fls(state->uei);
		|		output.uevp = state->uei == 0;
		|
		|		if (PIN_SSTOP=> && PIN_DMODE=>) {
		|			state->curuadr = output.nu;
		|		}
		|	}
		|}
		|''')

        file.fmt('''
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	bool bad_hint = output.bhp;
		|
		|	bool brtm3;
		|	unsigned btimm;
		|	if (bad_hint) {
		|		btimm = 2;
		|		brtm3 = ((state->bhreg) >> 5) & 1;
		|	} else {
		|		BUS_BRTIM_READ(btimm);
		|		brtm3 = br_type & 1;
		|	}
		|
		|	switch (btimm) {
		|	case 0: state->uadr_mux = !PIN_COND=>; break;
		|	case 1: state->uadr_mux = !output.ldc; break;
		|	case 2: state->uadr_mux = false; break;
		|	case 3: state->uadr_mux = true; break;
		|	}
		|	if (brtm3)
		|		state->uadr_mux = !state->uadr_mux;
		|
		|	unsigned adr = 0;
		|	if (bad_hint) adr |= 0x01;
		|	adr |= (br_type << 1);
		|	if (state->bhreg & 0x20) adr |= 0x20;
		|	if (state->bhreg & 0x40) adr |= 0x80;
		|	if (state->bhreg & 0x80) adr |= 0x100;
		|	unsigned rom = state->prom43[adr];
		|
		|	bool wanna_dispatch = !(((rom >> 5) & 1) && !state->uadr_mux);
		|	output.vdisp  = wanna_dispatch;
		|	state->preturn = !(((rom >> 3) & 1) ||  state->uadr_mux);
		|	state->push_br =    (rom >> 1) & 1;
		|	state->push   = !(((rom >> 0) & 1) ||
		|		        !(((rom >> 2) & 1) || !state->uadr_mux));
		|
		|	if (PIN_ACK.posedge()) {
		|		adr = 0;
		|		if (output.u_eventnot) adr |= 0x02;
		|		if (PIN_MEVENT=>) adr |= 0x04;
		|		adr |= btimm << 3;
		|		adr |= br_type << 5;
		|		rom = state->prom44[adr];
		|
		|		if (PIN_SCKE=>) {
		|			rom |= 0x2;
		|		} else {
		|			rom ^= 0x2;
		|		}
		|		unsigned mode = 3;
		|		if (!PIN_BHCKE=>) {
		|			mode = 0;
		|			state->bhreg = rom;
		|		}
		|
		|		state->hint_last = (state->bhreg >> 1) & 1;
		|		state->hint_t_last = (state->bhreg >> 0) & 1;
		|	}
		|	output.dtime = !(!bad_hint && (state->bhreg & 0x10));
		|	output.dbhint = !(!bad_hint || (state->bhreg & 0x08));
		|	bool bhint2 = (!bad_hint || (state->bhreg & 0x08));
		|	output.dmdisp = !(!bad_hint || (state->bhreg & 0x04));
		|	if (!bad_hint) {
		|		output.mpcmb = PIN_MPRND=>;
		|	} else {
		|		output.mpcmb = !((state->bhreg >> 2) & 1);
		|	}
       		|
		|	if (!PIN_TCLR=>) {
		|		state->treg = 0;
		|		output.fo7 = false;
		|	}
		|
		|	if (PIN_ACK.posedge()) {
		|		if (PIN_SSTOP=> && PIN_BHEN=> && bhint2) {
		|			unsigned restrt_rnd;
		|			BUS_RRND_READ(restrt_rnd);
		|			if (!wanna_dispatch) {
		|				state->rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->rreg = (restrt_rnd & 0x3) << 1;
		|			} else {
		|				state->rreg &= 0xa;
		|			}
		|			if (PIN_MEV=>) {
		|				state->rreg &= ~0x2;
		|			}
		|			BUS_TIN_READ(state->treg);
		|			state->treg ^= 0x4;
		|		} else if (PIN_SSTOP=> && PIN_BHEN=>) {
		|			state->rreg <<= 1;
		|			state->rreg &= 0xe;
		|			state->rreg |= 0x1;
		|			state->treg <<= 1;
		|			state->treg &= 0xe;
		|			state->treg |= 0x1;
		|		}
		|		output.rq = state->rreg;
		|		output.fo7 = state->treg >> 3;
		|
		|		unsigned lin;
		|		BUS_LIN_READ(lin);
		|		lin &= 0x7;
		|		lin |= output.ldc << 3;
		|
		|		if (!PIN_SCKE=>) {
		|			state->lreg = lin;
		|		}
		|
		|		if ((lin & 0x4) && !PIN_SCKE=>) {
		|			state->last_late_cond = PIN_COND=>;
		|		}
		|
		|		switch(state->lreg & 0x6) {
		|		case 0x0:
		|		case 0x4:
		|			output.ldc = (state->lreg >> 3) & 1;
		|			break;
		|		case 0x2:
		|			output.ldc = (state->lreg >> 0) & 1;
		|			break;
		|		case 0x6:
		|			output.ldc = state->last_late_cond;
		|			break;
		|		}
		|	}
		|
		|	bool last_cond_late = (state->lreg >> 2) & 1;
		|	if (state->hint_last) {
		|		output.bhp = false;
		|	} else if (!last_cond_late && !state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		output.bhp = e_or_ml_cond;
		|	} else if (!last_cond_late &&  state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		output.bhp = !e_or_ml_cond;
		|	} else if ( last_cond_late && !state->hint_t_last) {
		|		output.bhp = state->last_late_cond;
		|	} else if ( last_cond_late &&  state->hint_t_last) {
		|		output.bhp = !state->last_late_cond;
		|	}
		|	output.bhn = !output.bhp;
		|
		|}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		int_reads(internal_reads);
		|		output.qt = state->typ_bus;
		|		output.qt ^= BUS_QT_MASK;
		|	}
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qt) {
		|		output.qv = state->val_bus;
		|		output.qv ^= BUS_QV_MASK;
		|	}
		|
		|{
		|	uint64_t val = state->val_bus >> 32;
		|	val &= 0xffffff;
		|
		|	unsigned tmp = (val >> 7) ^ state->curins;
		|	tmp &= 0x3ff;
		|	output.fner = tmp != 0x3ff;
		|	output.ferr = !(output.fner && !(PIN_FCHR=> || !PIN_ENFU=>));
		|}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQIBUF", PartModelDQ("XSEQIBUF", XSEQIBUF))
