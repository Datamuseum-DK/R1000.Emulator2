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

class SEQ(PartFactory):
    ''' SEQ Instruction buffer '''

    autopin = True
    def extra(self, file):
        file.fmt('''
		|#define RND_PUSH		(1<<31)
		|#define RND_POP		(1<<30)
		|#define RND_CLEAR_ST		(1<<29)
		|#define RND_RESTRT0		(1<<28)
		|#define RND_RESTRT1		(1<<27)
		|#define RND_FLD_CHK		(1<<26)
		|#define RND_TOP_LD		(1<<25)
		|#define RND_HALT		(1<<24)
		|
		|#define RND_CNTL_MUX		(1<<23)
		|#define RND_CHK_EXIT		(1<<22)
		|#define RND_RETRN_LD		(1<<21)
		|#define RND_M_PC_MUX		(1<<20)
		|#define RND_M_PC_MD0		(1<<19)
		|#define RND_M_PC_MD1		(1<<18)
		|#define RND_M_PC_LDH		(1<<17)
		|#define RND_ADR_SEL		(1<<16)
		|
		|#define RND_TOS_VLB		(1<<15)
		|#define RND_RES_OFFS		(1<<14)
		|#define RND_RES_NAME		(1<<13)
		|#define RND_CUR_LEX		(1<<12)
		|#define RND_NAME_LD		(1<<11)
		|#define RND_SAVE_LD		(1<<10)
		|#define RND_PRED_LD		(1<< 9)
		|#define RND_L_ABRT		(1<< 8)
		|
		|#define RND_LEX_COMM0		(1<< 7)
		|#define RND_LEX_COMM1		(1<< 6)
		|#define RND_LEX_COMM2		(1<< 5)
		|#define RND_CIB_PC_L		(1<< 4)
		|#define RND_INSTR_MX		(1<< 3)
		|#define RND_IBUFF_LD		(1<< 2)
		|#define RND_BR_MSK_L		(1<< 1)
		|#define RND_INSTR_LD		(1<< 0)
		|#define RNDX(x) ((state->rndx & (x)) != 0)
		|''')

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
		|	// SEQNAM
		|	uint32_t tost, vost, cur_name;
		|	uint32_t namram[1<<4];
		|	unsigned pcseg, retseg, last;
		|
		|	uint64_t tosram[1<<4];
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
		|	uint8_t pa040[512];
		|	uint8_t pa043[512];
		|	uint8_t pa044[512];
		|	uint8_t pa045[512];
		|	uint8_t pa046[512];
		|	uint8_t pa047[512];
		|	uint8_t pa048[512];
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
		|	unsigned display;
		|       unsigned resolve_offset;
		|       unsigned rndx;
		|	bool cload;
		|	bool ibuf_fill;
		|	bool uses_tos;
		|	bool l_macro_hic;
		|	bool m_pc_mb;
		|	unsigned n_in_csa;
		|	unsigned decode;
		|	unsigned lmp;
		|	unsigned wanna_dispatch;
		|	bool ibld;
		|	bool field_number_error;
		|	bool import_condition;
		|	bool m_break_class;
		|	bool latched_cond;
		|	bool saved_latched;
		|	bool stack_size_zero;
		|	unsigned rq;
		|	bool m_tos_invld;
		|	bool m_underflow;
		|	bool m_overflow;
		|	bool disp_cond0;
		|	bool tos_vld_cond;
		|	bool foo7;
		|	bool check_exit_ue;
		|	bool carry_out;
		|	bool bad_hint;
		|	bool m_res_ref;
		|	bool bad_hint_enable;
		|	bool ferr;
		|
		|	uint8_t pa041[512];
		|	uint16_t lex_valid;
		|	uint16_t dns;
		|	uint16_t dra;
		|	uint16_t dlr;
		|	bool lxval;
		|	unsigned resolve_address;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->pa040, sizeof state->pa040, "PA040-02");
		|	load_programmable(this->name(), state->pa043, sizeof state->pa043, "PA043-02");
		|	load_programmable(this->name(), state->pa044, sizeof state->pa044, "PA044-01");
		|	load_programmable(this->name(), state->pa045, sizeof state->pa045, "PA045-03");
		|	load_programmable(this->name(), state->pa046, sizeof state->pa046, "PA046-02");
		|	load_programmable(this->name(), state->pa047, sizeof state->pa047, "PA047-02");
		|	load_programmable(this->name(), state->pa048, sizeof state->pa048, "PA048-02");
		|''')
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->pa041, sizeof state->pa041,
		|	    "PA041-01");
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "PIN_H2"

        yield "PIN_ACLK"
        # yield "PIN_BCLK"
        yield "PIN_LCLK"
        yield "PIN_TOSCLK"

        yield "PIN_SCLKE"
        #yield "PIN_BHCKE"	# aclk

        yield "PIN_BHEN"
        yield "PIN_COND"
        yield "BUS_CSA"
        #yield "BUS_CTL"		# q4pos
        #yield "BUS_DF"		# FIU_CLK, stkclk, q4pos
        yield "PIN_DMODE"
        #yield "BUS_DT"
        #yield "BUS_DV"
        yield "PIN_DV_U"
        #yield "BUS_EMAC"	# aclk
        yield "PIN_ENFU"
        #yield "PIN_FIU_CLK"
        # yield "PIN_FLIP"
        #yield "BUS_LIN"		# aclk
        #yield "PIN_LXVAL"
        yield "PIN_MIBMT"
        yield "PIN_Q3COND"
        yield "PIN_SGEXT"
        #yield "PIN_SSTOP"	# q4pos, aclk
        yield "PIN_STOP"
        yield "PIN_TCLR"
        #yield "BUS_UEI"		# aclk

        yield "PIN_ADROE"
        #yield "PIN_OSPCOE"
        #yield "PIN_QFOE"
        #yield "PIN_QTOE"
        #yield "PIN_QVOE"

        #yield "BUS_BRN"		# ucode
        #yield "BUS_BRTIM"	# ucode
        #yield "BUS_BRTYP"	# ucode
        #yield "BUS_CSEL"	# ucode
        #yield "BUS_IRD"		# ucode
        #yield "BUS_LAUIR"	# ucode
        #yield "PIN_LINC"	# ucode
        #yield "PIN_LMAC"	# ucode
        #yield "PIN_MD"		# ucode
        #yield "BUS_RASEL"	# ucode
        #yield "BUS_URAND"	# ucode

    def priv_decl(self, file):
        file.fmt('''
		|	void int_reads(unsigned ir, unsigned urand);
		|	unsigned group_sel(void);
		|	unsigned late_macro_pending(void);
		|	void seq_cond(void);
		|       unsigned nxt_lex_valid(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|int_reads(unsigned ir, unsigned urand)
		|{
		|	if (ir == 0) {
		|		BUS_DT_READ(state->typ_bus);
		|		state->typ_bus ^= BUS_DT_MASK;
		|		BUS_DV_READ(state->val_bus);
		|		state->val_bus ^= BUS_DV_MASK;
		|		return;
		|	}		
		|
		|	state->typ_bus = state->n_in_csa;
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
		|	if (!(urand & 0x2)) {
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
		|		state->val_bus |= state->display;
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
		|
		|unsigned
		|SCM_«mmm» ::
		|late_macro_pending(void)
		|{
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|	unsigned dec = state->decode >> 3;
		|
		|	if (csa < (dec & 7))
		|		return (0);
		|	if (csa > ((dec >> 3) | 12))
		|		return (1);
		|	if (PIN_STOP=>)
		|		return (2);
		|	if (!state->m_res_ref)
		|		return (3);
		|	if (!state->m_tos_invld)
		|		return (4);
		|	if (!state->m_break_class)
		|		return (6);
		|	if (!output.mibuf)
		|		return (7);
		|	return (8);
		|}
		|
		|void
		|SCM_«mmm» ::
		|seq_cond(void)
		|{
		|	unsigned condsel;
		|	BUS_CSEL_READ(condsel);
		|	condsel ^= BUS_CSEL_MASK;
		|	switch (condsel) {
		|	case 0x28: // FIELD_NUM_ERR
		|		output.conda = !state->field_number_error;
		|		break;
		|	case 0x29: // LATCHED_COND
		|		output.conda = !state->latched_cond;
		|		break;
		|	case 0x2a: // E_MACRO_PEND
		|		output.conda = state->emac == 0x7f;
		|		break;
		|	case 0x2b: // E_MACRO_EVNT~6
		|		output.conda = !((state->emac >> 0) & 1);
		|		break;
		|	case 0x2c: // E_MACRO_EVNT~5
		|		output.conda = !((state->emac >> 1) & 1);
		|		break;
		|	case 0x2d: // E_MACRO_EVNT~3
		|		output.conda = !((state->emac >> 3) & 1);
		|		break;
		|	case 0x2e: // E_MACRO_EVNT~2
		|		output.conda = !((state->emac >> 4) & 1);
		|		break;
		|	case 0x2f: // E_MACRO_EVNT~0
		|		output.conda = !((state->emac >> 6) & 1);
		|		break;
		|
		|	case 0x30: // DISP_COND0
		|		output.condb = state->disp_cond0;
		|		break;
		|	case 0x31: // True
		|		output.condb = true;
		|		break;
		|	case 0x32: // M_IBUFF_MT
		|		output.condb = PIN_MIBMT=>;
		|		break;
		|	case 0x33: // M_BRK_CLASS
		|		output.condb = state->m_break_class;
		|		break;
		|	case 0x34: // M_TOS_INVLD
		|		output.condb = state->m_tos_invld;
		|		break;
		|	case 0x35: // M_RES_REF
		|		output.condb = state->m_res_ref;
		|		break;
		|	case 0x36: // M_OVERFLOW
		|		output.condb = state->m_overflow;
		|		break;
		|	case 0x37: // M_UNDERFLOW
		|		output.condb = state->m_underflow;
		|		break;
		|
		|	case 0x38: // STACK_SIZE
		|		output.condc = state->stack_size_zero;
		|		break;
		|	case 0x39: // LATCHED_COND
		|		output.condc = state->latched_cond;
		|		break;
		|	case 0x3a: // SAVED_LATCHED
		|		output.condc = state->saved_latched;
		|		break;
		|	case 0x3b: // TOS_VLD.COND
		|		output.condc = state->tos_vld_cond;
		|		break;
		|	case 0x3c: // LEX_VLD.COND
		|		output.condc = state->lxval;
		|		break;
		|	case 0x3d: // IMPORT.COND
		|		output.condc = state->import_condition;
		|		break;
		|	case 0x3e: // REST_PC_DEC
		|		output.condc = ((state->rq >> 1) & 1);
		|		break;
		|	case 0x3f: // RESTARTABLE
		|		output.condc = ((state->rq >> 3) & 1);
		|		break;
		|	}
		|}
		|
		|unsigned
		|SCM_«mmm» ::
		|nxt_lex_valid(void)
		|{
		|	unsigned adr;
		|	uint16_t nv = 0;
		|	adr = ((state->lex_valid >> 12) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 3) & 1) << 1;
		|	bool pm3 = !((state->dns & 0x7) && !(state->dlr & 1));
		|	adr |= pm3;
		|	nv |= (state->pa041[adr] >> 4) << 12;
		|
		|	adr = ((state->lex_valid >> 8) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 2) & 1) << 1;
		|	bool pm2 = !((state->dns & 0x3) && !(state->dlr & 1));
		|	adr |= pm2;
		|	nv |= (state->pa041[adr] >> 4) << 8;
		|
		|	adr = ((state->lex_valid >> 4) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 1) & 1) << 1;
		|	bool pm1 = !((state->dns & 0x1) && !(state->dlr & 1));
		|	adr |= pm1;
		|	nv |= (state->pa041[adr] >> 4) << 4;
		|
		|	adr = ((state->lex_valid >> 0) & 0xf) << 5;
		|	adr |= state->dra << 3;
		|	adr |= ((state->dlr >> 2) & 1) << 2;
		|	adr |= ((state->dns >> 0) & 1) << 1;
		|	adr |= (state->dlr >> 0) & 1;
		|	nv |= (state->pa041[adr] >> 4) << 0;
		|
		|	return(nv);
		|}
		|''')


    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	//bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	bool aclk = PIN_ACLK.posedge();
		|	bool sclke = PIN_SCLKE=>;
		|	bool sclk = aclk && !sclke;
		|	bool state_clock = q4pos && !sclke;
		|
		|	if (q3pos) {
		|		state->bad_hint_enable = !(
		|			output.u_event ||
		|			(PIN_LMAC=> && output.bhn)
		|		);
		|	}
		|
		|	unsigned urand;
		|	BUS_URAND_READ(urand);
		|	state->rndx = state->pa048[urand | (state->bad_hint ? 0x100 : 0)] << 24;
		|	state->rndx |= state->pa046[urand | (state->bad_hint ? 0x100 : 0)] << 16;
		|	state->rndx |=  state->pa045[urand | 0x100] << 8;
		|	state->rndx |= state->pa047[urand | 0x100];
		|	output.halt = RNDX(RND_HALT);
		|
		|{
		|
		|	if (state_clock) {
		|		unsigned lex_random;
		|		BUS_LRN_READ(lex_random);
		|		state->dra = state->resolve_address & 3;
		|		state->dlr = lex_random;
		|		if (lex_random & 0x2) {
		|			state->dns = 0xf;
		|		} else {
		|			state->dns = 0xf ^ (0x8 >> (state->resolve_address >> 2));
		|		}
		|	}
		|
		|	if (PIN_Q4.posedge()) {
		|		state->lex_valid = nxt_lex_valid();
		|	}
		|
		|	state->lxval = !((nxt_lex_valid() >> (15 - state->resolve_address)) & 1);
		|}
		|
		|	unsigned pa040a;
		|	unsigned pa040d;
		|{
		|	unsigned tmp = 0;
		|	tmp |= (state->decode & 0x7) << 6;
		|	if (state->wanna_dispatch) tmp |= 0x20;
		|	if (RNDX(RND_ADR_SEL)) tmp |= 0x10;
		|	if (state->import_condition) tmp |= 0x08;
		|	if (PIN_STOP=>) tmp |= 0x04;
		|	if (PIN_MD=>) tmp |= 0x02;
		|	if (state->bad_hint) tmp |= 0x01;
		|	pa040a = tmp;
		|	pa040d = state->pa040[tmp];
		|}
		|
		|	state->disp_cond0 = (pa040d >> 7) & 1;
		|
		|	unsigned internal_reads;
		|	BUS_IRD_READ(internal_reads);
		|
		|	int_reads(internal_reads, urand);
		|
		|	state->lmp = late_macro_pending();
		|	bool early_macro_pending = state->emac != 0x7f;
		|	bool macro_event = (!state->wanna_dispatch) && (early_macro_pending || (state->lmp != 8));
		|	bool dispatch = state->wanna_dispatch || early_macro_pending || (state->lmp != 8);
		|	bool lmac = macro_event && !early_macro_pending;
		|
		|	bool mbuf = !(lmac && (state->lmp >= 7));
		|	if (macro_event) {
		|		output.bar8 = !mbuf;
		|	} else {
		|		output.bar8 = !((pa040d >> 1) & 1);
		|	}
		|	output.meh = macro_event;
		|	output.lmaco = macro_event && !early_macro_pending;
		|	output.disp = dispatch;
		|{
		|	if (q4pos && !sclke && !state->ibld) {
		|		state->typ = state->typ_bus;
		|		state->val = state->val_bus;
		|	}
		|
		|	unsigned macro_pc_ofs = state->mpc;
		|
		|	if (q4pos && !sclke && !RNDX(RND_RETRN_LD)) {
		|		state->retrn_pc_ofs = state->mpc;
		|	}
		|
		|	bool mibmt = PIN_MIBMT;
		|	bool oper;
		|	unsigned a;
		|	if (!state->wanna_dispatch && !mibmt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!state->wanna_dispatch && mibmt) {
		|		a = state->display;
		|		oper = false;
		|	} else if (state->wanna_dispatch && !mibmt) {
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
		|		if (state->wanna_dispatch)
		|			a += 1;
		|		a &= 0x7fff;
		|		state->boff = a + b;
		|	} else {
		|		if (!state->wanna_dispatch)
		|			a += 1;
		|		state->boff = b - a;
		|	}
		|	state->boff &= 0x7fff;
		|
		|	//if (PIN_BCLK.posedge()) {
		|	if (q4pos && !PIN_BHCKE=> && !output.meh) {
		|		unsigned mode = 0;
		|		unsigned u = 0;
		|		if (state->cload) u |= 1;
		|		if (state->wanna_dispatch) u |= 2;
		|		switch (u) {
		|		case 0: mode = 1; break;
		|		case 1: mode = 1; break;
		|		case 3: mode = 0; break;
		|		case 2:
		|			if (state->m_pc_mb) mode |= 2;
		|			if (RNDX(RND_M_PC_MD1)) mode |= 1;
		|			break;
		|		}
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			if (!RNDX(RND_M_PC_MUX)) {
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
		|	switch (urand & 3) {
		|	case 3:	state->coff = state->retrn_pc_ofs; break;
		|	case 2: state->coff = state->boff; break;
		|	case 1: state->coff = state->mpc; break;
		|	case 0: state->coff = state->boff; break;
		|	}
		|	state->coff ^= 0x7fff;;
		|
		|	unsigned iclex;
		|
		|	iclex = (state->val_bus & 0xf) + 1;
		|
		|	if (q4pos && !sclke && !RNDX(RND_CUR_LEX)) {
		|		state->curr_lex = state->val_bus & 0xf;
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
		|		res_addr = (state->display >> 9) & 0xf;
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
		|	res_addr &= 0xf;
		|	state->resolve_address = res_addr;
		|	if (PIN_LINC=>) {
		|		state->import_condition = true;
		|		output.sext = true;
		|	} else {
		|		state->import_condition = !(res_addr == 0xf);
		|		output.sext = !((res_addr > 0xd));
		|	}
		|
		|	if (aclk) {
		|		BUS_EMAC_READ(state->emac);
		|	}
		|{
		|	if (!(state->emac & 0x40)) {
		|		state->uadr_decode = 0x04e0;
		|	} else if (!(state->emac & 0x20)) {
		|		state->uadr_decode = 0x04c0;
		|	} else if (!(state->emac & 0x10)) {
		|		state->uadr_decode = 0x04a0;
		|	} else if (!(state->emac & 0x08)) {
		|		state->uadr_decode = 0x0480;
		|	} else if (!(state->emac & 0x04)) {
		|		state->uadr_decode = 0x0460;
		|	} else if (!(state->emac & 0x02)) {
		|		state->uadr_decode = 0x0440;
		|	} else if (!(state->emac & 0x01)) {
		|		state->uadr_decode = 0x0420;
		|	} else {
		|		unsigned ai = state->display;
		|		ai ^= 0xffff;
		|		bool top = (state->display >> 10) != 0x3f;
		|		uint32_t *ptr;
		|		if (top)
		|			ptr = &state->top[ai >> 6];
		|		else
		|			ptr = &state->bot[ai & 0x3ff];
		|		state->uadr_decode = (*ptr >> 16);
		|		state->decode = (*ptr >> 8) & 0xff;
		|	}
		|	state->uses_tos = (state->uadr_decode >> 2) & 1;
		|	state->ibuf_fill = (state->uadr_decode >> 1) & 1;
		|}
		|
		|	if (sclk) {
		|		unsigned dsp = 0;
		|		if (!RNDX(RND_INSTR_MX)) {
		|			dsp = state->display;
		|		} else {
		|			uint64_t tval = state->val_bus;
		|			dsp = tval & 0xffff;
		|		}
		|		dsp ^= 0xffff;;
		|
		|		bool gate = !(RNDX(RND_INSTR_LD) && dispatch);
		|		if (gate && state->topbot)
		|			state->ctop = dsp;
		|		if (gate && !state->topbot)
		|			state->cbot = dsp;
		|	}
		|
		|	//if (PIN_FLIP.posedge()) {
		|	if (q4pos && !PIN_BHCKE=>) {
		|		bool crnana = !(RNDX(RND_INSTR_LD) && output.disp);
		|		bool crnor0a = !(crnana || output.dmdisp);
		|		if (!crnor0a)
		|			state->topbot = !state->topbot;
		|	}
		|
		|	if (state->topbot)
		|		state->curins = state->cbot;
		|	else
		|		state->curins = state->ctop;
		|
		|	if (sclk && !RNDX(RND_BR_MSK_L)) {
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
		|		state->m_break_class = false;
		|	} else {
		|		state->m_break_class = (state->break_mask >> (15 - ccl)) & 1;
		|	}
		|	state->m_break_class = !state->m_break_class;
		|
		|}
		|{
		|	bool maybe_dispatch = PIN_MD=>;
		|	bool uses_tos, dis;
		|	unsigned mem_start;
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
		|		mem_start = state->decode & 0x7;
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
		|		if (macro_event) {
		|			output.ospc = 0x6;
		|		} else {
		|			output.ospc = (pa040d >> 3) & 0x7;
		|		}
		|	}
		|
		|	if (PIN_TOSCLK.posedge()) {
		|		state->tost = state->typ_bus >> 32;
		|		state->vost = state->val_bus >> 32;
		|		state->tosof = (typl >> 7) & 0xfffff;
		|	}
		|
		|	if (q4pos && !sclke && !RNDX(RND_NAME_LD)) {
		|		state->cur_name = state->typ_bus >> 32;
		|	}
		|
		|	if (q4pos && !sclke && !RNDX(RND_RES_NAME)) {
		|		state->namram[state->resolve_address] = state->typ_bus >> 32;
		|	}
		|
		|	if (!type_name_oe) {
		|		state->name_bus = state->tost ^ 0xffffffff;
		|	} else if (!val_name_oe) {
		|		state->name_bus = state->vost ^ 0xffffffff;
		|	} else if (!name_ram_cs) {
		|		state->name_bus = state->namram[state->resolve_address] ^ 0xffffffff;
		|	} else {
		|		state->name_bus = 0xffffffff;
		|	}
		|
		|	if (q4pos && !sclke && !RNDX(RND_RETRN_LD)) {
		|		state->retseg = state->pcseg;
		|	}
		|	if (q4pos && !sclke && !RNDX(RND_M_PC_LDH)) {
		|		unsigned val;
		|		val = state->val_bus >> 32;
		|		val ^= 0xffffffff;
		|		state->pcseg = val;
		|		state->pcseg &= 0xffffff;
		|	}
		|
		|
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (RNDX(RND_TOS_VLB)) {
		|			offs = (typl >> 7) & 0xfffff;
		|		} else {
		|			offs = state->tosof;
		|		}
		|	} else {
		|		if (q4pos && !sclke && !RNDX(RND_RES_OFFS)) {
		|			state->tosram[state->resolve_address] = (typl >> 7) & 0xfffff;
		|		}
		|		offs = state->tosram[state->resolve_address];
		|	}
		|	offs ^= 0xfffff;
		|       offs &= 0xfffff;
		|
		|       bool d7 = (state->display & 0x8100) == 0;
		|       unsigned sgdisp = state->display & 0xff;
		|       if (!d7)
		|               sgdisp |= 0x100;
		|       if (!(PIN_SGEXT && d7))
		|               sgdisp |= 0xffe00;
		|
		|	bool acin = ((mem_start & 1) != 0);
		|       sgdisp &= 0xfffff;
		|       state->resolve_offset = 0;
		|       bool co = false;
		|
		|	switch(mem_start) {
		|	case 0:
		|	case 2:
		|               state->resolve_offset = offs + sgdisp + 1;
		|               co = (state->resolve_offset >> 20) == 0;
		|		break;
		|	case 1:
		|	case 3:
		|               state->resolve_offset = (1<<20) + offs - (sgdisp + 1);
		|               co = acin && (offs == 0);
		|		break;
		|	case 4:
		|	case 6:
		|               state->resolve_offset = sgdisp ^ 0xfffff;
		|               // Carry is probably "undefined" here.
		|		break;
		|	case 5:
		|	case 7:
		|               state->resolve_offset = offs;
		|               co = acin && (offs == 0);
		|		break;
		|	}
		|
		|	state->resolve_offset &= 0xfffff;
		|
		|	if (q4pos && !sclke && !RNDX(RND_SAVE_LD)) {
		|		state->savrg = state->resolve_offset;
		|		state->carry_out = co;
		|	}
		|
		|	if ((q4pos && !sclke && !RNDX(RND_PRED_LD)) || state_clock) {
		|		uint64_t cnb;
		|		if (!RNDX(RND_CNTL_MUX)) {
		|			cnb = typl ^ 0xffffffffULL;
		|		} else {
		|			BUS_DF_READ(cnb);
		|			cnb &= 0xffffffffULL;
		|		}
		|		cnb >>= 7;
		|		cnb &= 0xfffff;
		|
		|		if (q4pos && !sclke && !RNDX(RND_PRED_LD)) {
		|			state->pred = cnb;
		|		}
		|		if (state_clock) {
		|			unsigned csa_cntl;
		|			BUS_CTL_READ(csa_cntl);
		|
		|			bool ten = (csa_cntl != 2 && csa_cntl != 3);
		|			bool tud = !(csa_cntl & 1);
		|			if (!RNDX(RND_TOP_LD)) {
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
		|		state->output_ob = state->resolve_offset;
		|	} else if (intreads == 3) {
		|		state->output_ob = state->savrg;
		|	} else {
		|		state->output_ob = 0xfffff;
		|	}
		|	state->output_ob &= 0xfffff;
		|
		|
		|}
		|{
		|	bool stkclk = q4pos && PIN_SSTOP=> && state->l_macro_hic;
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
		|			stkinpsel_1 = state->bad_hint;
		|		} else {
		|			xwrite = !RNDX(RND_PUSH);
		|			pop = !!(state->preturn || RNDX(RND_POP));
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
		|				if (state->latched_cond) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 1:
		|				BUS_DF_READ(state->topu);
		|				state->topu &= 0xffff;
		|				break;
		|			case 2:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (state->latched_cond) state->topu |= (1<<14);
		|				state->topu += 1;
		|				state->topu ^= 0xffff;;
		|				break;
		|			case 3:
		|				state->topu = state->curuadr;
		|				if (PIN_Q3COND)	state->topu |= (1<<15);
		|				if (state->latched_cond) state->topu |= (1<<14);
		|				state->topu ^= 0xffff;;
		|				break;
		|			}
		|		} else if (pop) {
		|			state->topu = state->ram[state->adr];
		|		}
		|		state->saved_latched = !((state->topu >> 14) & 0x1);
		|
		|		if (RNDX(RND_CLEAR_ST) && !PIN_STOP=>) {
		|			state->adr = xwrite;
		|		} else if (xwrite || pop) {
		|			if (xwrite) {
		|				state->adr = (state->adr + 1) & 0xf;
		|			} else {
		|				state->adr = (state->adr + 0xf) & 0xf;
		|			}
		|		}
		|		state->stack_size_zero = state->adr == 0;
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
		|	if (sclk && aclk) {
		|		BUS_DF_READ(state->fiu);
		|		state->fiu &= 0x3fff;
		|	}
		|
		|	if (PIN_LCLK.posedge()) {
		|		if (PIN_MD=>) {
		|			state->late_u = 7;
		|		} else {
		|			state->late_u = state->lmp;
		|			if (state->late_u == 8)
		|				state->late_u = 7;
		|		}
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
		|			data = state->decode >> 3;
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
		|	} else if (state->bad_hint) {
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
		|	state->l_macro_hic = macro_hic;
		|	output.u_event = !u_event;
		|	output.u_eventnot = u_event;
		|
		|	if (aclk) {
		|		BUS_UEI_READ(state->uei);
		|		state->uei &= ~(1 << BUS_UEI_LSB(4));
		|		state->uei |= state->ferr << BUS_UEI_LSB(4);
		|		if (state->check_exit_ue)
		|			state->uei |= (1<<BUS_UEI_LSB(3));
		|		else
		|			state->uei &= ~(1<<BUS_UEI_LSB(3));
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
		|
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	bool bad_hint = state->bad_hint;
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
		|	case 1: state->uadr_mux = !state->latched_cond; break;
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
		|	unsigned rom = state->pa043[adr];
		|
		|
		|	state->wanna_dispatch = !(((rom >> 5) & 1) && !state->uadr_mux);
		|	state->preturn = !(((rom >> 3) & 1) ||  state->uadr_mux);
		|	state->push_br =    (rom >> 1) & 1;
		|	state->push   = !(((rom >> 0) & 1) ||
		|		        !(((rom >> 2) & 1) || !state->uadr_mux));
		|
		|	if (aclk) {
		|		adr = 0;
		|		if (output.u_eventnot) adr |= 0x02;
		|		if (!macro_event)
		|			adr |= 0x04;
		|		adr |= btimm << 3;
		|		adr |= br_type << 5;
		|		rom = state->pa044[adr];
		|
		|		if (sclke) {
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
		|	output.dbhint = !(!bad_hint || (state->bhreg & 0x08));
		|	bool bhint2 = (!bad_hint || (state->bhreg & 0x08));
		|	output.dmdisp = !(!bad_hint || (state->bhreg & 0x04));
		|	if (!bad_hint) {
		|		state->m_pc_mb = RNDX(RND_M_PC_MD0);
		|	} else {
		|		state->m_pc_mb = !((state->bhreg >> 2) & 1);
		|	}
		|
		|	if (!PIN_TCLR=>) {
		|		state->treg = 0;
		|		state->foo7 = false;
		|	}
		|
		|	if (aclk) {
		|		//state->bad_hint_enable = PIN_BHEN=>;
		|		if (PIN_SSTOP=> && state->bad_hint_enable && bhint2) {
		|			unsigned restrt_rnd = 0;
		|			restrt_rnd |= RNDX(RND_RESTRT0) ? 2 : 0;
		|			restrt_rnd |= RNDX(RND_RESTRT1) ? 1 : 0;
		|			if (!state->wanna_dispatch) {
		|				state->rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->rreg = (restrt_rnd & 0x3) << 1;
		|			} else {
		|				state->rreg &= 0xa;
		|			}
		|			if (macro_event) {
		|				state->rreg &= ~0x2;
		|			}
		|			state->treg = 0x3;
		|			bool dnan0d = !(output.disp && RNDX(RND_PRED_LD));
		|			bool tsnor0b = !(dnan0d || state->tos_vld_cond);
		|			if (tsnor0b)
		|				state->treg |= 0x8;
		|			if (!state->tos_vld_cond)
		|				state->treg |= 0x4;
		|		} else if (PIN_SSTOP=> && state->bad_hint_enable) {
		|			state->rreg <<= 1;
		|			state->rreg &= 0xe;
		|			state->rreg |= 0x1;
		|			state->treg <<= 1;
		|			state->treg &= 0xe;
		|			state->treg |= 0x1;
		|		}
		|		state->rq = state->rreg;
		|		state->foo7 = state->treg >> 3;
		|
		|		unsigned lin;
		|		BUS_LIN_READ(lin);
		|		lin &= 0x7;
		|		lin |= state->latched_cond << 3;
		|
		|		if (!sclke) {
		|			state->lreg = lin;
		|		}
		|
		|		if ((lin & 0x4) && !sclke) {
		|			state->last_late_cond = PIN_COND=>;
		|		}
		|
		|		switch(state->lreg & 0x6) {
		|		case 0x0:
		|		case 0x4:
		|			state->latched_cond = (state->lreg >> 3) & 1;
		|			break;
		|		case 0x2:
		|			state->latched_cond = (state->lreg >> 0) & 1;
		|			break;
		|		case 0x6:
		|			state->latched_cond = state->last_late_cond;
		|			break;
		|		}
		|	}
		|
		|	bool last_cond_late = (state->lreg >> 2) & 1;
		|	if (state->hint_last) {
		|		state->bad_hint = false;
		|	} else if (!last_cond_late && !state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		state->bad_hint = e_or_ml_cond;
		|	} else if (!last_cond_late &&  state->hint_t_last) {
		|		bool e_or_ml_cond = state->lreg & 1;
		|		state->bad_hint = !e_or_ml_cond;
		|	} else if ( last_cond_late && !state->hint_t_last) {
		|		state->bad_hint = state->last_late_cond;
		|	} else if ( last_cond_late &&  state->hint_t_last) {
		|		state->bad_hint = !state->last_late_cond;
		|	}
		|	output.bhn = !state->bad_hint;
		|
		|}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		int_reads(internal_reads, urand);
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
		|	state->field_number_error = tmp != 0x3ff;
		|	state->ferr = !(state->field_number_error && !(RNDX(RND_FLD_CHK) || !PIN_ENFU=>));
		|	// XXX: Necesary for re-triggering :-(
		|	output.ferr = state->ferr;
		|}
		|	if (q4pos) {
		|		if (state->word == 7)
		|			state->display = state->typ >> 48;
		|		else if (state->word == 6)
		|			state->display = state->typ >> 32;
		|		else if (state->word == 5)
		|			state->display = state->typ >> 16;
		|		else if (state->word == 4)
		|			state->display = state->typ >> 0;
		|		else if (state->word == 3)
		|			state->display = state->val >> 48;
		|		else if (state->word == 2)
		|			state->display = state->val >> 32;
		|		else if (state->word == 1)
		|			state->display = state->val >> 16;
		|		else if (state->word == 0)
		|			state->display = state->val >> 0;
		|		else
		|			state->display = 0xffff;
		|		state->display &= 0xffff;
		|		output.disp0 = state->display >> 15;
		|	}
		|	output.z_adr = PIN_ADROE=>;
		|	if (!output.z_adr) {
		|		bool adr_is_code = !((!macro_event) && (pa040d & 0x01));
		|		bool resolve_drive;
		|		if (!macro_event) {
		|			resolve_drive = !((pa040d >> 6) & 1);
		|		} else {
		|			resolve_drive = true;
		|		}
		|		if (!resolve_drive) {
		|			output.adr = state->resolve_offset;
		|		} else if (adr_is_code) {
		|			output.adr = state->coff >> 3;
		|		} else {
		|			output.adr = state->output_ob;
		|		}
		|		output.adr <<= 7;
		|
		|		unsigned branch;
		|		branch = state->boff & 7;
		|		branch ^= 0x7;
		|		output.adr |= branch << 4;
		|		uint64_t cseg;
		|		if (!(urand & 0x2)) {
		|			cseg = state->pcseg;
		|		} else {
		|			cseg = state->retseg;
		|		}
		|
		|		if (adr_is_code) {
		|			output.adr |= cseg << 32;
		|		} else {
		|			output.adr |= (uint64_t)state->name_bus << 32;
		|		}
		|	}
		|
		|	state->cload = !(PIN_COND=> || !(output.bhn && RNDX(RND_CIB_PC_L)));
		|	bool ibuff_ld = !(state->cload || RNDX(RND_IBUFF_LD));
		|	state->ibld = !ibuff_ld;
		|	bool ibemp = !(ibuff_ld || (state->word != 0));
		|	output.mibuf = !(ibemp && state->ibuf_fill);
		|
		|	state->m_tos_invld = !(state->uses_tos && state->tos_vld_cond);
		|
		|	output.qstp7 = output.bhn && state->l_macro_hic;
		|
		|	if (state_clock) {
		|		BUS_CSA_READ(state->n_in_csa);
		|	}
		|{
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|	unsigned dec = state->decode >> 3;
		|	state->m_underflow = csa >= (dec & 7);
		|	state->m_overflow = csa <= ((dec >> 3) | 12);
		|}
		|	seq_cond();
		|	state->tos_vld_cond = !(state->foo7 || RNDX(RND_TOS_VLB));
		|	state->check_exit_ue = !(
		|		PIN_ENFU=> &&
		|		RNDX(RND_CHK_EXIT) &&
		|		state->carry_out
		|	);
		|	output.sfive = (state->check_exit_ue && output.ferr);
		|	state->m_res_ref = !(state->lxval && !output.disp0);
		|
		|	if (PIN_H2=>) {
		|		if (!output.bar8) {
		|			output.abort = false;
		|		} else if (PIN_MCOND=>) {
		|			output.abort = true;
		|		} else if (PIN_MCPOL=> ^ PIN_Q3COND) {
		|			output.abort = true;
		|		} else {
		|			output.abort = false;
		|		}
		|	}
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("SEQ", PartModelDQ("SEQ", SEQ))
