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
		|	uint64_t macro_ins_typ, macro_ins_val;
		|	unsigned word;
		|	unsigned macro_pc_offset;
		|	unsigned curr_lex;
		|	unsigned retrn_pc_ofs;
		|	unsigned branch_offset;
		|	unsigned break_mask;
		|
		|	// SEQNAM
		|	uint64_t tost, vost, cur_name;
		|	uint64_t namram[1<<4];
		|	uint64_t pcseg, retseg;
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
		|	uint8_t pa041[512];
		|	uint8_t pa042[512];
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
		|	uint64_t coff;
		|	unsigned uadr_decode;
		|	unsigned display;
		|       uint64_t resolve_offset;
		|       unsigned rndx;
		|	bool cload;
		|	bool ibuf_fill;
		|	bool uses_tos;
		|	bool l_macro_hic;
		|	bool m_pc_mb;
		|	unsigned n_in_csa;
		|	unsigned decode;
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
		|	uint16_t lex_valid;
		|	uint16_t dns;
		|	uint16_t dra;
		|	uint16_t dlr;
		|	bool lxval;
		|	unsigned resolve_address;
		|	bool bar8;
		|	bool m_ibuff_mt;
		|	bool foo9;
		|	bool q3cond;
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->pa040, sizeof state->pa040, "PA040-02");
		|	load_programmable(this->name(), state->pa041, sizeof state->pa041, "PA041-01");
		|	load_programmable(this->name(), state->pa042, sizeof state->pa041, "PA042-02");
		|	load_programmable(this->name(), state->pa043, sizeof state->pa043, "PA043-02");
		|	load_programmable(this->name(), state->pa044, sizeof state->pa044, "PA044-01");
		|	load_programmable(this->name(), state->pa045, sizeof state->pa045, "PA045-03");
		|	load_programmable(this->name(), state->pa046, sizeof state->pa046, "PA046-02");
		|	load_programmable(this->name(), state->pa047, sizeof state->pa047, "PA047-02");
		|	load_programmable(this->name(), state->pa048, sizeof state->pa048, "PA048-02");
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "PIN_H2"

        yield "PIN_ACLK"
        yield "PIN_LCLK"
        #yield "PIN_TOSCLK"

        # yield "PIN_SCLKE"

        yield "PIN_BHEN"
        yield "BUS_CSA"
        yield "PIN_DMODE"
        yield "PIN_DV_U"
        yield "PIN_ENFU"
        # yield "PIN_Q3COND"

    def priv_decl(self, file):
        file.fmt('''
		|	void int_reads(unsigned ir, unsigned urand);
		|	unsigned group_sel(void);
		|	unsigned late_macro_pending(void);
		|	bool seq_cond5(unsigned condsel);
		|	bool seq_cond6(unsigned condsel);
		|	bool seq_cond7(unsigned condsel);
		|       unsigned nxt_lex_valid(void);
		|       bool condition(void);
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
		|		state->typ_bus |= (state->name_bus ^ 0xffffffff) << 32;
		|		break;
		|	default:
		|		state->typ_bus |= (uint64_t)state->cur_name << 32;
		|		break;
		|	}
		|	
		|	if (!(urand & 0x2)) {
		|		state->val_bus = state->pcseg << 32;
		|	} else {
		|		state->val_bus = state->retseg << 32;
		|	}
		|	state->val_bus ^= 0xffffffffULL << 32; 
		|	state->val_bus ^= (state->coff >> 12) << 16;
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
		|	if (!state->m_ibuff_mt)
		|		return (7);
		|	return (8);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_cond5(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x28: // FIELD_NUM_ERR
		|		return ( !state->field_number_error);
		|	case 0x29: // LATCHED_COND
		|		return ( !state->latched_cond);
		|	case 0x2a: // E_MACRO_PEND
		|		return ( state->emac == 0x7f);
		|	case 0x2b: // E_MACRO_EVNT~6
		|		return ( !((state->emac >> 0) & 1));
		|	case 0x2c: // E_MACRO_EVNT~5
		|		return ( !((state->emac >> 1) & 1));
		|	case 0x2d: // E_MACRO_EVNT~3
		|		return ( !((state->emac >> 3) & 1));
		|	case 0x2e: // E_MACRO_EVNT~2
		|		return ( !((state->emac >> 4) & 1));
		|	case 0x2f: // E_MACRO_EVNT~0
		|		return ( !((state->emac >> 6) & 1));
		|	default:
		|		return (false);
		|	}
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_cond6(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x30: // DISP_COND0
		|		return ( (state->decode & 0x7) == 0);
		|		break;
		|	case 0x31: // True
		|		return ( true);
		|		break;
		|	case 0x32: // M_IBUFF_MT
		|		return ( state->m_ibuff_mt);
		|		break;
		|	case 0x33: // M_BRK_CLASS
		|		return ( state->m_break_class);
		|		break;
		|	case 0x34: // M_TOS_INVLD
		|		return ( state->m_tos_invld);
		|		break;
		|	case 0x35: // M_RES_REF
		|		return ( state->m_res_ref);
		|		break;
		|	case 0x36: // M_OVERFLOW
		|		{
		|		unsigned csa;
		|		BUS_CSA_READ(csa);
		|		unsigned dec = state->decode >> 3;
		|		return ( csa <= ((dec >> 3) | 12));
		|		}
		|		break;
		|	case 0x37: // M_UNDERFLOW
		|		{
		|		unsigned csa;
		|		BUS_CSA_READ(csa);
		|		unsigned dec = state->decode >> 3;
		|		return ( csa >= (dec & 7));
		|		}
		|		break;
		|	default:
		|		return (false);
		|	}
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_cond7(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x38: // STACK_SIZE
		|		return ( state->stack_size_zero);
		|		break;
		|	case 0x39: // LATCHED_COND
		|		return ( state->latched_cond);
		|		break;
		|	case 0x3a: // SAVED_LATCHED
		|		return ( state->saved_latched);
		|		break;
		|	case 0x3b: // TOS_VLD.COND
		|		return ( state->tos_vld_cond);
		|		break;
		|	case 0x3c: // LEX_VLD.COND
		|		return ( state->lxval);
		|		break;
		|	case 0x3d: // IMPORT.COND
		|		return ( state->import_condition);
		|		break;
		|	case 0x3e: // REST_PC_DEC
		|		return ( ((state->rq >> 1) & 1));
		|		break;
		|	case 0x3f: // RESTARTABLE
		|		return ( ((state->rq >> 3) & 1));
		|		break;
		|	default:
		|		return (false);
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
		|
		|bool
		|SCM_«mmm» ::
		|condition(void)
		|{
		|	unsigned condsel;
		|	BUS_CSEL_READ(condsel);
		|	condsel ^= BUS_CSEL_MASK;
		|	switch (condsel >> 3) {
		|	case 0x0: return(PIN_CNDX0=>);
		|	case 0x2: return(PIN_CNDX2=>);
		|	case 0x3: return(PIN_CNDX3=>);
		|	case 0x4: return(!(PIN_CNDXC=> && PIN_CNDXF=>));
		|	case 0x5: return(seq_cond5(condsel));
		|	case 0x6: return(seq_cond6(condsel));
		|	case 0x7: return(seq_cond7(condsel));
		|	case 0x8: return(PIN_CNDX8=>);
		|	case 0x9: return(PIN_CNDX9=>);
		|	case 0xa: return(PIN_CNDXA=>);
		|	case 0xb: return(PIN_CNDXB=>);
		|	case 0xc: return(PIN_CNDXC=>);
		|	case 0xd: return(PIN_CNDXD=>);
		|	case 0xe: return(PIN_CNDXE=>);
		|	case 0xf: return(PIN_CNDXF=>);
		|	default: return(1);
		|	}
		|}
		|''')


    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|	//bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q3pos = PIN_Q4.negedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	//bool h1pos = PIN_H2.negedge();
		|	//bool h2pos = PIN_H2.posedge();
		|	bool aclk = PIN_ACLK.posedge();
		|	bool sclke = PIN_SCLKE=>;
		|	bool sclk = aclk && !sclke;
		|	bool state_clock = q4pos && !sclke;
		|	bool sign_extend;
		|
		|																							if (q3pos) {
		|																								state->q3cond = condition();
		|																								state->bad_hint_enable = !(
		|																									output.u_event ||
		|																									(PIN_LMAC=> && output.bhn)
		|																								);
		|																							}
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
		|																											if (state_clock) {
		|																												unsigned lex_random;
		|																												BUS_LRN_READ(lex_random);
		|																												state->dra = state->resolve_address & 3;
		|																												state->dlr = lex_random;
		|																												if (lex_random & 0x2) {
		|																													state->dns = 0xf;
		|																												} else {
		|																													state->dns = 0xf ^ (0x8 >> (state->resolve_address >> 2));
		|																												}
		|																											}
		|
		|																											if (PIN_Q4.posedge()) {
		|																												state->lex_valid = nxt_lex_valid();
		|																											}
		|
		|	state->lxval = !((nxt_lex_valid() >> (15 - state->resolve_address)) & 1);
		|}
		|
		|	unsigned pa040d;
		|{
		|	unsigned pa040a = 0;
		|	pa040a |= (state->decode & 0x7) << 6;
		|	if (state->wanna_dispatch) pa040a |= 0x20;
		|	if (RNDX(RND_ADR_SEL)) pa040a |= 0x10;
		|	if (state->import_condition) pa040a |= 0x08;
		|	if (PIN_STOP=>) pa040a |= 0x04;
		|	if (PIN_MD=>) pa040a |= 0x02;
		|	if (state->bad_hint) pa040a |= 0x01;
		|	pa040d = state->pa040[pa040a];
		|}
		|
		|	unsigned internal_reads;
		|	BUS_IRD_READ(internal_reads);
		|
		|	int_reads(internal_reads, urand);
		|
		|	unsigned lmp = late_macro_pending();
		|	bool early_macro_pending = state->emac != 0x7f;
		|	bool macro_event = (!state->wanna_dispatch) && (early_macro_pending || (lmp != 8));
		|	bool dispatch = state->wanna_dispatch || early_macro_pending || (lmp != 8);
		|
		|	if (macro_event) {
		|		state->bar8 = (macro_event && !early_macro_pending) && (lmp >= 7);
		|	} else {
		|		state->bar8 = !((pa040d >> 1) & 1);
		|	}
		|	output.lmaco = macro_event && !early_macro_pending;
		|{
		|																											if (q4pos && !sclke && !state->ibld) {
		|																												state->macro_ins_typ = state->typ_bus;
		|																												state->macro_ins_val = state->val_bus;
		|																											}
		|
		|																											if (q4pos && !sclke && !RNDX(RND_RETRN_LD)) {
		|																												state->retrn_pc_ofs = state->macro_pc_offset;
		|																											}
		|
		|{
		|	bool oper;
		|	unsigned a;
		|	if (!state->wanna_dispatch && !state->m_ibuff_mt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!state->wanna_dispatch && state->m_ibuff_mt) {
		|		a = state->display;
		|		oper = false;
		|	} else if (state->wanna_dispatch && !state->m_ibuff_mt) {
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
		|	unsigned b = state->macro_pc_offset & 0x7fff;
		|	if (oper) {
		|		if (state->wanna_dispatch)
		|			a += 1;
		|		a &= 0x7fff;
		|		state->branch_offset = a + b;
		|	} else {
		|		if (!state->wanna_dispatch)
		|			a += 1;
		|		state->branch_offset = b - a;
		|	}
		|	state->branch_offset &= 0x7fff;
		|}
		|
		|																											if (q4pos && !PIN_BHCKE=> && !macro_event) {
		|																												unsigned mode = 0;
		|																												unsigned u = 0;
		|																												if (state->cload) u |= 1;
		|																												if (state->wanna_dispatch) u |= 2;
		|																												switch (u) {
		|																												case 0: mode = 1; break;
		|																												case 1: mode = 1; break;
		|																												case 2:
		|																													if (!state->bad_hint) {
		|																														state->m_pc_mb = RNDX(RND_M_PC_MD0);
		|																													} else {
		|																														state->m_pc_mb = !((state->bhreg >> 2) & 1);
		|																													}
		|																										
		|																													if (state->m_pc_mb) mode |= 2;
		|																													if (RNDX(RND_M_PC_MD1)) mode |= 1;
		|																													break;
		|																												case 3: mode = 0; break;
		|																												}
		|																												if (mode == 3) {
		|																													uint64_t tmp;
		|																													if (!RNDX(RND_M_PC_MUX)) {
		|																														tmp = state->val_bus;
		|																														state->word = tmp >> 4;
		|																														state->macro_pc_offset = (tmp >> 4) & 0x7fff;
		|																													} else {
		|																														state->macro_pc_offset = state->branch_offset;
		|																														state->word = state->branch_offset;
		|																													}
		|																												} else if (mode == 2) {
		|																													state->macro_pc_offset += 1;
		|																													state->word += 1;
		|																												} else if (mode == 1) {
		|																													state->macro_pc_offset -= 1;
		|																													state->word += 7;
		|																												}
		|																												state->word &= 7;
		|																											}
		|
		|	switch (urand & 3) {
		|	case 3:	state->coff = state->retrn_pc_ofs; break;
		|	case 2: state->coff = state->branch_offset; break;
		|	case 1: state->coff = state->macro_pc_offset; break;
		|	case 0: state->coff = state->branch_offset; break;
		|	}
		|	state->coff ^= 0x7fff;
		|
		|																											if (q4pos && !sclke && !RNDX(RND_CUR_LEX)) {
		|																												state->curr_lex = state->val_bus & 0xf;
		|																												state->curr_lex ^= 0xf;
		|																											}
		|{
		|	unsigned sel;
		|	BUS_RASEL_READ(sel);
		|	switch (sel) {
		|	case 0:
		|		if (PIN_LAUIR0=> && PIN_LAUIR1=>)
		|			state->resolve_address = 0xe;
		|		else
		|			state->resolve_address = 0xf;
		|		break;
		|	case 1:
		|		state->resolve_address = (state->display >> 9) & 0xf;
		|		break;
		|	case 2:
		|		state->resolve_address = (state->val_bus & 0xf) + 1;
		|		break;
		|	case 3:
		|		state->resolve_address = state->curr_lex ^ 0xf;
		|		break;
		|	default:
		|		assert(sel < 4);
		|	}
		|	state->resolve_address &= 0xf;
		|}
		|	if (PIN_LINC=>) {
		|		state->import_condition = true;
		|		sign_extend = true;
		|	} else {
		|		state->import_condition = !(state->resolve_address == 0xf);
		|		sign_extend = !((state->resolve_address > 0xd));
		|	}
		|
		|																											if (aclk) {
		|																												BUS_EMAC_READ(state->emac);
		|																											}
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
		|																											if (sclk) {
		|																												unsigned dsp = 0;
		|																												if (!RNDX(RND_INSTR_MX)) {
		|																													dsp = state->display;
		|																												} else {
		|																													uint64_t tval = state->val_bus;
		|																													dsp = tval & 0xffff;
		|																												}
		|																												dsp ^= 0xffff;;
		|																										
		|																												bool gate = !(RNDX(RND_INSTR_LD) && dispatch);
		|																												if (gate && state->topbot)
		|																													state->ctop = dsp;
		|																												if (gate && !state->topbot)
		|																													state->cbot = dsp;
		|																											}
		|																										
		|																											//if (PIN_FLIP.posedge()) {
		|																											if (q4pos && !PIN_BHCKE=>) {
		|																												bool crnana = !(RNDX(RND_INSTR_LD) && dispatch);
		|																												bool dmdisp = !(!state->bad_hint || (state->bhreg & 0x04));
		|																												bool crnor0a = !(crnana || dmdisp);
		|																												if (!crnor0a)
		|																													state->topbot = !state->topbot;
		|																											}
		|
		|	if (state->topbot)
		|		state->curins = state->cbot;
		|	else
		|		state->curins = state->ctop;
		|
		|																											if (sclk && !RNDX(RND_BR_MSK_L)) {
		|																												uint64_t tmp = state->val_bus;
		|																												state->break_mask = (tmp >> 16) & 0xffff;
		|																											}
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
		|		uses_tos = state->uses_tos;
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
		|
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|
		|																							if (q3pos && RNDX(RND_TOS_VLB) && !PIN_STOP=>) {
		|																								state->tost = state->typ_bus >> 32;
		|																								state->vost = state->val_bus >> 32;
		|																								state->tosof = (state->typ_bus >> 7) & 0xfffff;
		|																							}
		|
		|																											if (q4pos && !sclke && !RNDX(RND_NAME_LD)) {
		|																												state->cur_name = state->typ_bus >> 32;
		|																											}
		|																										
		|																											if (q4pos && !sclke && !RNDX(RND_RES_NAME)) {
		|																												state->namram[state->resolve_address] = state->typ_bus >> 32;
		|																											}
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
		|																											if (q4pos && !sclke && !RNDX(RND_RETRN_LD)) {
		|																												state->retseg = state->pcseg;
		|																											}
		|																											if (q4pos && !sclke && !RNDX(RND_M_PC_LDH)) {
		|																												unsigned val;
		|																												val = state->val_bus >> 32;
		|																												val ^= 0xffffffff;
		|																												state->pcseg = val;
		|																												state->pcseg &= 0xffffff;
		|																											}
		|
		|
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (RNDX(RND_TOS_VLB)) {
		|			offs = (state->typ_bus >> 7) & 0xfffff;
		|		} else {
		|			offs = state->tosof;
		|		}
		|	} else {
		|		if (q4pos && !sclke && !RNDX(RND_RES_OFFS)) {
		|			state->tosram[state->resolve_address] = (state->typ_bus >> 7) & 0xfffff;
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
		|       if (!(sign_extend && d7))
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
		|																											if (state_clock && !RNDX(RND_SAVE_LD)) {
		|																												state->savrg = state->resolve_offset;
		|																												state->carry_out = co;
		|																											}
		|																										
		|																											if (state_clock) {
		|																												uint64_t cnb;
		|																												if (!RNDX(RND_CNTL_MUX)) {
		|																													cnb = state->typ_bus ^ 0xffffffffULL;
		|																												} else {
		|																													BUS_DF_READ(cnb);
		|																												}
		|																												cnb &= 0xffffffffULL;
		|																												cnb >>= 7;
		|																												cnb &= 0xfffff;
		|																										
		|																												if (!RNDX(RND_PRED_LD)) {
		|																													state->pred = cnb;
		|																												}
		|																												unsigned csa_cntl;
		|																												BUS_CTL_READ(csa_cntl);
		|																										
		|																												bool ten = (csa_cntl != 2 && csa_cntl != 3);
		|																												bool tud = !(csa_cntl & 1);
		|																												if (!RNDX(RND_TOP_LD)) {
		|																													state->topcnt = cnb;
		|																												} else if (ten) {
		|																													// Nothing
		|																												} else if (tud) {
		|																													state->topcnt += 1;
		|																												} else {
		|																													state->topcnt += 0xfffff;
		|																												}
		|																												state->topcnt &= 0xfffff;
		|																											}
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
		|
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|															if (q2pos) {
		|																state->ram[(state->adr + 1) & 0xf] = state->topu;
		|
		|																state->l_macro_hic = true;
		|																unsigned nua;
		|																if (!PIN_DV_U=>) {
		|																	nua = state->nxtuadr;
		|																} else if (state->bad_hint) {
		|																	nua = state->other;
		|																} else if (PIN_LMAC=>) {
		|																	// Not tested by expmon_test_seq ?
		|																	nua = state->late_u << 3;
		|																	nua ^= (7 << 3);
		|																	nua |= 0x0140;
		|																	state->l_macro_hic = false;
		|																} else if (state->uei != 0) {
		|																	nua = state->uev;
		|																	nua <<= 3;
		|																	nua |= 0x0180;
		|																} else {
		|																	unsigned sel = group_sel();
		|																	switch (sel) {
		|																	case 0:
		|																		BUS_BRN_READ(nua);
		|																		nua += state->fiu;
		|																		break;
		|																	case 1:
		|																		nua = state->uadr_decode >> 3;
		|																		nua <<= 1;
		|																		break;
		|																	case 2:
		|																		nua = (state->topu ^ 0xffff) & 0x3fff;
		|																		break;
		|																	case 3:
		|																	case 4:
		|																		nua = state->curuadr;
		|																		nua += 1;
		|																		break;
		|																	case 5:
		|																	case 6:
		|																	case 7:
		|																		BUS_BRN_READ(nua);
		|																		break;
		|																	default:
		|																		abort();
		|																	}
		|																}
		|																output.nu = nua;
		|															}
		|
		|
		|
		|																											if (q4pos && PIN_SSTOP=> && state->l_macro_hic) {
		|																												bool xwrite;
		|																												bool pop;
		|																												bool stkinpsel_0;
		|																												bool stkinpsel_1;
		|																												if (output.u_event) {
		|																													xwrite = true;
		|																													pop = true;
		|																													stkinpsel_0 = true;
		|																													stkinpsel_1 = true;
		|																												} else if (!state->push) {
		|																													xwrite = true;
		|																													pop = false;
		|																													stkinpsel_0 = !state->push_br;
		|																													stkinpsel_1 = state->bad_hint;
		|																												} else {
		|																													xwrite = !RNDX(RND_PUSH);
		|																													pop = !!(state->preturn || RNDX(RND_POP));
		|																													stkinpsel_0 = false;
		|																													stkinpsel_1 = true;
		|																												}
		|																										
		|																												unsigned stkinpsel = 0;
		|																												if (stkinpsel_0) stkinpsel |= 2;
		|																												if (stkinpsel_1) stkinpsel |= 1;
		|																										
		|																												if (xwrite) {
		|																													switch(stkinpsel) {
		|																													case 0:
		|																														BUS_BRN_READ(state->topu);
		|																														if (state->q3cond)	 state->topu |= (1<<15);
		|																														if (state->latched_cond) state->topu |= (1<<14);
		|																														state->topu ^= 0xffff;
		|																														break;
		|																													case 1:
		|																														BUS_DF_READ(state->topu);
		|																														state->topu &= 0xffff;
		|																														break;
		|																													case 2:
		|																														state->topu = state->curuadr;
		|																														if (state->q3cond)	 state->topu |= (1<<15);
		|																														if (state->latched_cond) state->topu |= (1<<14);
		|																														state->topu += 1;
		|																														state->topu ^= 0xffff;
		|																														break;
		|																													case 3:
		|																														state->topu = state->curuadr;
		|																														if (state->q3cond)	 state->topu |= (1<<15);
		|																														if (state->latched_cond) state->topu |= (1<<14);
		|																														state->topu ^= 0xffff;;
		|																														break;
		|																													}
		|																												} else if (pop) {
		|																													state->topu = state->ram[state->adr];
		|																												}
		|																												state->saved_latched = !((state->topu >> 14) & 0x1);
		|																										
		|																												if (RNDX(RND_CLEAR_ST) && !PIN_STOP=>) {
		|																													state->adr = xwrite;
		|																												} else if (xwrite || pop) {
		|																													if (xwrite) {
		|																														state->adr = (state->adr + 1) & 0xf;
		|																													} else {
		|																														state->adr = (state->adr + 0xf) & 0xf;
		|																													}
		|																												}
		|																												state->stack_size_zero = state->adr == 0;
		|																											}
		|
		|
		|																											if (sclk && aclk) {
		|																												BUS_DF_READ(state->fiu);
		|																												state->fiu &= 0x3fff;
		|																											}
		|																										
		|																											if (PIN_LCLK.posedge()) {
		|																												if (PIN_MD=>) {
		|																													state->late_u = 7;
		|																												} else {
		|																													state->late_u = late_macro_pending();
		|																													if (state->late_u == 8)
		|																														state->late_u = 7;
		|																												}
		|																												unsigned sel = group_sel();
		|																												switch (sel) {
		|																												case 0:
		|																												case 7:
		|																													state->other = state->curuadr + 1;
		|																													break;
		|																												case 1:
		|																												case 2:
		|																												case 3:
		|																													BUS_BRN_READ(state->other);
		|																													break;
		|																												case 4:
		|																													BUS_BRN_READ(state->other);
		|																													state->other += state->fiu;
		|																													break;
		|																												case 5:
		|																													state->other = state->decode >> 3;
		|																													state->other <<= 1;
		|																													break;
		|																												case 6:
		|																													state->other = (state->topu ^ 0xffff) & 0x3fff;
		|																													break;
		|																												default:
		|																													abort();
		|																												}
		|																											}
		|
		|	output.u_event = (PIN_DV_U=> && !state->bad_hint && !PIN_LMAC=> && state->uei != 0);
		|																											if (aclk) {
		|																												BUS_UEI_READ(state->uei);
		|																												state->uei &= ~(1 << BUS_UEI_LSB(4));
		|																												state->uei |= state->ferr << BUS_UEI_LSB(4);
		|																												if (state->check_exit_ue)
		|																													state->uei |= (1<<BUS_UEI_LSB(3));
		|																												else
		|																													state->uei &= ~(1<<BUS_UEI_LSB(3));
		|																												state->uei <<= 1;
		|																												state->uei |= 1;
		|																												state->uei ^= 0xffff;
		|																												state->uev = 16 - fls(state->uei);
		|																												output.uevp = state->uei == 0;
		|																										
		|																												if (PIN_SSTOP=> && PIN_DMODE=>) {
		|																													state->curuadr = output.nu;
		|																												}
		|																											}
		|}
		|
		|{
		|	unsigned br_type;
		|	BUS_BRTYP_READ(br_type);
		|
		|	bool brtm3;
		|	unsigned btimm;
		|	if (state->bad_hint) {
		|		btimm = 2;
		|		brtm3 = ((state->bhreg) >> 5) & 1;
		|	} else {
		|		BUS_BRTIM_READ(btimm);
		|		brtm3 = br_type & 1;
		|	}
		|
		|	switch (btimm) {
		|	case 0: state->uadr_mux = !condition(); break;
		|	case 1: state->uadr_mux = !state->latched_cond; break;
		|	case 2: state->uadr_mux = false; break;
		|	case 3: state->uadr_mux = true; break;
		|	}
		|	if (brtm3)
		|		state->uadr_mux = !state->uadr_mux;
		|
		|	unsigned adr = 0;
		|	if (state->bad_hint) adr |= 0x01;
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
		|																											if (aclk) {
		|																												adr = 0;
		|																												if (!output.u_event)
		|																													adr |= 0x02;
		|																												if (!macro_event)
		|																													adr |= 0x04;
		|																												adr |= btimm << 3;
		|																												adr |= br_type << 5;
		|																												rom = state->pa044[adr];
		|																										
		|																												if (sclke) {
		|																													rom |= 0x2;
		|																												} else {
		|																													rom ^= 0x2;
		|																												}
		|																												unsigned mode = 3;
		|																												if (!PIN_BHCKE=>) {
		|																													mode = 0;
		|																													state->bhreg = rom;
		|																												}
		|																										
		|																												state->hint_last = (state->bhreg >> 1) & 1;
		|																												state->hint_t_last = (state->bhreg >> 0) & 1;
		|																											}
		|	bool bhint2 = (!state->bad_hint || (state->bhreg & 0x08));
		|	output.dbhint = bhint2;
		|																							if (q3pos && !(state->foo9 || !output.u_event)) {
		|																								state->treg = 0;
		|																								state->foo7 = false;
		|																							}
		|
		|																											if (aclk) {
		|																												//state->bad_hint_enable = PIN_BHEN=>;
		|																												if (PIN_SSTOP=> && state->bad_hint_enable && bhint2) {
		|																													unsigned restrt_rnd = 0;
		|																													restrt_rnd |= RNDX(RND_RESTRT0) ? 2 : 0;
		|																													restrt_rnd |= RNDX(RND_RESTRT1) ? 1 : 0;
		|																													if (!state->wanna_dispatch) {
		|																														state->rreg = 0xa;
		|																													} else if (restrt_rnd != 0) {
		|																														state->rreg = (restrt_rnd & 0x3) << 1;
		|																													} else {
		|																														state->rreg &= 0xa;
		|																													}
		|																													if (macro_event) {
		|																														state->rreg &= ~0x2;
		|																													}
		|																													state->treg = 0x3;
		|																													bool dnan0d = !(dispatch && RNDX(RND_PRED_LD));
		|																													bool tsnor0b = !(dnan0d || state->tos_vld_cond);
		|																													if (tsnor0b)
		|																														state->treg |= 0x8;
		|																													if (!state->tos_vld_cond)
		|																														state->treg |= 0x4;
		|																												} else if (PIN_SSTOP=> && state->bad_hint_enable) {
		|																													state->rreg <<= 1;
		|																													state->rreg &= 0xe;
		|																													state->rreg |= 0x1;
		|																													state->treg <<= 1;
		|																													state->treg &= 0xe;
		|																													state->treg |= 0x1;
		|																												}
		|																												state->rq = state->rreg;
		|																												state->foo7 = state->treg >> 3;
		|																										
		|																												unsigned lin = 0;
		|																												lin |= state->latched_cond << 3;
		|																												unsigned condsel;
		|																												BUS_CSEL_READ(condsel);
		|																												uint8_t pa042 = state->pa042[condsel << 2];
		|																												bool is_e_ml = (pa042 >> 7) & 1;
		|																												lin |= is_e_ml << 2;
		|																												lin |= PIN_LUIR=> << 1;
		|																												lin |= state->q3cond << 0;
		|																										
		|																												if (!sclke) {
		|																													state->lreg = lin;
		|																												}
		|																										
		|																												if ((lin & 0x4) && !sclke) {
		|																													state->last_late_cond = condition();
		|																												}
		|																										
		|																												switch(state->lreg & 0x6) {
		|																												case 0x0:
		|																												case 0x4:
		|																													state->latched_cond = (state->lreg >> 3) & 1;
		|																													break;
		|																												case 0x2:
		|																													state->latched_cond = (state->lreg >> 0) & 1;
		|																													break;
		|																												case 0x6:
		|																													state->latched_cond = state->last_late_cond;
		|																													break;
		|																												}
		|																											}
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
		|
		|{
		|	uint64_t val = state->val_bus >> 32;
		|	val &= 0xffffff;
		|
		|	unsigned tmp = (val >> 7) ^ state->curins;
		|	tmp &= 0x3ff;
		|	state->field_number_error = tmp != 0x3ff;
		|	state->ferr = !(state->field_number_error && !(RNDX(RND_FLD_CHK) || !PIN_ENFU=>));
		|}
		|																											if (q4pos) {
		|																												switch(state->word) {
		|																												case 0x0: state->display = state->macro_ins_val >>  0; break;
		|																												case 0x1: state->display = state->macro_ins_val >> 16; break;
		|																												case 0x2: state->display = state->macro_ins_val >> 32; break;
		|																												case 0x3: state->display = state->macro_ins_val >> 48; break;
		|																												case 0x4: state->display = state->macro_ins_typ >>  0; break;
		|																												case 0x5: state->display = state->macro_ins_typ >> 16; break;
		|																												case 0x6: state->display = state->macro_ins_typ >> 32; break;
		|																												case 0x7: state->display = state->macro_ins_typ >> 48; break;
		|																												}
		|																												state->display &= 0xffff;
		|																												output.disp0 = state->display >> 15;
		|																											}
		|
		|	state->cload = !(condition() || !(output.bhn && RNDX(RND_CIB_PC_L)));
		|	bool ibuff_ld = !(state->cload || RNDX(RND_IBUFF_LD));
		|	state->ibld = !ibuff_ld;
		|	bool ibemp = !(ibuff_ld || (state->word != 0));
		|	state->m_ibuff_mt = !(ibemp && state->ibuf_fill);
		|
		|	state->m_tos_invld = !(state->uses_tos && state->tos_vld_cond);
		|
		|	output.qstp7 = output.bhn && state->l_macro_hic;
		|
		|																											if (state_clock) {
		|																												BUS_CSA_READ(state->n_in_csa);
		|																											}
		|																										
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|	state->tos_vld_cond = !(state->foo7 || RNDX(RND_TOS_VLB));
		|	state->check_exit_ue = !(
		|		PIN_ENFU=> &&
		|		RNDX(RND_CHK_EXIT) &&
		|		state->carry_out
		|	);
		|	output.sfive = (state->check_exit_ue && state->ferr);
		|	state->m_res_ref = !(state->lxval && !output.disp0);
		|
		|																			if (q3pos) {
		|																				if (!state->bar8) {
		|																					output.abort = false;
		|																				} else if (PIN_MCOND=>) {
		|																					output.abort = true;
		|																				} else if (PIN_MCPOL=> ^ state->q3cond) {
		|																					output.abort = true;
		|																				} else {
		|																					output.abort = false;
		|																				}
		|																			}
		|																											if (PIN_LCLK.posedge()) {
		|																												state->foo9 = !RNDX(RND_TOS_VLB);
		|																											}
		|//	ALWAYS						H1				Q1				Q2				H2				Q3				Q4
		|	output.z_qf = PIN_QFOE=>;
		|	if (!output.z_qf) {
		|		output.qf = state->topu ^ 0xffff;
		|		output.qf ^= 0xffff;
		|	}
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
		|	output.z_adr = PIN_ADROE=>;
		|	output.z_ospc = PIN_OSPCOE=>;
		|																							if (q3pos && !output.z_ospc) {
		|																								if (macro_event) {
		|																									output.ospc = 0x6;
		|																								} else {
		|																									output.ospc = (pa040d >> 3) & 0x7;
		|																								}
		|																							}
		|																							if (q3pos && !output.z_adr) {
		|																								bool adr_is_code = !((!macro_event) && (pa040d & 0x01));
		|																								bool resolve_drive;
		|																								if (!macro_event) {
		|																									resolve_drive = !((pa040d >> 6) & 1);
		|																								} else {
		|																									resolve_drive = true;
		|																								}
		|																								if (!resolve_drive) {
		|																									output.adr = state->resolve_offset << 7;
		|																								} else if (adr_is_code) {
		|																									output.adr = (state->coff >> 3) << 7;
		|																								} else {
		|																									output.adr = state->output_ob << 7;
		|																								}
		|															
		|																								uint64_t branch;
		|																								branch = state->branch_offset & 7;
		|																								branch ^= 0x7;
		|																								output.adr |= branch << 4;
		|																								if (!adr_is_code) {
		|																									output.adr |= state->name_bus << 32;
		|																								} else if (!(urand & 0x2)) {
		|																									output.adr |= state->pcseg << 32; 
		|																								} else {
		|																									output.adr |= state->retseg << 32;
		|																								}
		|																							}
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("SEQ", PartModelDQ("SEQ", SEQ))
