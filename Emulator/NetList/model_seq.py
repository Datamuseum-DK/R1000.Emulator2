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

		|	// R1000_Micro_Arch_Seq.pdf pdf pg 25
		|	//	BRANCH TYPE (4 bits)
		|	//	0000	brf
		|	//	0001	brt
		|	//	0010	push
		|	//	0011	br
		|	//	0100	callf
		|	//	0101	callt
		|	//	0110	cont
		|	//	0111	call
		|	//	1000	returnt
		|	//	1001	returnf
		|	//	1010	return
		|	//	1100	dispt
		|	//	1101	dispf
		|	//	1110	disp
		|	//	1111	case_call
		|	// R1000_Micro_Arch_Seq.pdf pdf pg 26, SEQ.pdf pdf pg 102:
		|	//	LEX LEVEL ADDRESSING MICRO-ORDERS
		|	//	00 CUR_LEX
		|	//	01 INCOMING LEX
		|	//	10 OUTER_FRAME
		|	//	11 IMPORT
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
		|#define RNDX(x) ((rndx & (x)) != 0)
		|''')

    def state(self, file):
        file.fmt('''
		|	uint32_t *seq_top;
		|	uint32_t *seq_bot;
		|	uint32_t seq_cbot, seq_ctop;
		|	unsigned seq_emac;
		|	unsigned seq_curins;
		|	bool seq_topbot;
		|
		|	uint64_t seq_macro_ins_typ, seq_macro_ins_val;
		|	unsigned seq_word;
		|	unsigned seq_macro_pc_offset;
		|	unsigned seq_curr_lex;
		|	unsigned seq_retrn_pc_ofs;
		|	unsigned seq_break_mask;
		|
		|	uint64_t seq_tost, seq_vost, seq_cur_name;
		|	uint64_t seq_namram[1<<4];
		|	uint64_t seq_pcseg, seq_retseg;
		|
		|	uint64_t seq_tosram[1<<4];
		|	uint64_t seq_tosof;
		|	uint32_t seq_savrg;
		|	uint32_t seq_pred;
		|	uint32_t seq_topcnt;
		|
		|	uint16_t seq_ram[16];
		|	uint16_t seq_topu;
		|	uint16_t seq_adr;
		|	unsigned seq_fiu;
		|	unsigned seq_other;
		|	unsigned seq_late_u;
		|	unsigned seq_uev;
		|
		|	uint8_t seq_pa040[512];
		|	uint8_t seq_pa041[512];
		|	uint8_t seq_pa042[512];
		|	uint8_t seq_pa043[512];
		|	uint8_t seq_pa044[512];
		|	uint8_t seq_pa045[512];
		|	uint8_t seq_pa046[512];
		|	uint8_t seq_pa047[512];
		|	uint8_t seq_pa048[512];
		|	uint8_t seq_bhreg;
		|	unsigned seq_rreg;
		|	unsigned seq_lreg;
		|	unsigned seq_treg;
		|	bool seq_hint_last;
		|	bool seq_hint_t_last;
		|	bool seq_last_late_cond;
		|	bool seq_uadr_mux, seq_preturn, seq_push_br, seq_push;
		|	uint64_t seq_typ_bus;
		|	uint64_t seq_val_bus;
		|	uint64_t seq_output_ob;
		|	uint64_t seq_name_bus;
		|	uint64_t seq_coff;
		|	unsigned seq_uadr_decode;
		|	unsigned seq_display;
		|       uint64_t seq_resolve_offset;
		|	bool seq_cload;
		|	bool seq_ibuf_fill;
		|	bool seq_uses_tos;
		|	bool seq_l_macro_hic;
		|	bool seq_m_pc_mb;
		|	unsigned seq_n_in_csa;
		|	unsigned seq_decode;
		|	unsigned seq_wanna_dispatch;
		|	bool seq_ibld;
		|	bool seq_field_number_error;
		|	bool seq_import_condition;
		|	bool seq_m_break_class;
		|	bool seq_latched_cond;
		|	bool seq_saved_latched;
		|	bool seq_stack_size_zero;
		|	unsigned seq_rq;
		|	bool seq_m_tos_invld;
		|	bool seq_tos_vld_cond;
		|	bool seq_foo7;
		|	bool seq_check_exit_ue;
		|	bool seq_carry_out;
		|	bool seq_bad_hint;
		|	bool seq_m_res_ref;
		|	bool seq_bad_hint_enable;
		|	bool seq_ferr;
		|	bool seq_late_macro_event;
		|	bool seq_sf_stop;
		|	bool seq_s_state_stop;
		|	bool seq_clock_stop_1;
		|	bool seq_clock_stop_5;
		|	unsigned seq_diag;
		|	unsigned seq_countdown;
		|
		|	uint16_t seq_lex_valid;
		|	bool seq_lxval;
		|	unsigned seq_resolve_address;
		|	bool seq_m_ibuff_mt;
		|	bool seq_foo9;
		|	bool seq_q3cond;
		|	bool seq_stop;
		|	uint64_t *seq_wcsram;
		|	uint64_t seq_uir;
		|
		|#define UIR_SEQ_BRN	((state->seq_uir >> (41-13)) & 0x3fff)
		|#define UIR_SEQ_LUIR	((state->seq_uir >> (41-15)) & 0x1)
		|#define UIR_SEQ_BRTYP	((state->seq_uir >> (41-19)) & 0xf)
		|#define UIR_SEQ_BRTIM	((state->seq_uir >> (41-21)) & 0x3)
		|#define UIR_SEQ_CSEL	((state->seq_uir >> (41-28)) & 0x7f)
		|#define UIR_SEQ_LAUIR	((state->seq_uir >> (41-30)) & 0x3)
		|#define UIR_SEQ_ENMIC	((state->seq_uir >> (41-31)) & 0x1)
		|#define UIR_SEQ_IRD	((state->seq_uir >> (41-34)) & 0x7)
		|#define UIR_SEQ_URAND	((state->seq_uir >> (41-41)) & 0x7f)
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->seq_pa040, sizeof state->seq_pa040, "PA040-02");
		|	load_programmable(this->name(), state->seq_pa041, sizeof state->seq_pa041, "PA041-01");
		|	load_programmable(this->name(), state->seq_pa042, sizeof state->seq_pa041, "PA042-02");
		|	load_programmable(this->name(), state->seq_pa043, sizeof state->seq_pa043, "PA043-02");
		|	load_programmable(this->name(), state->seq_pa044, sizeof state->seq_pa044, "PA044-01");
		|	load_programmable(this->name(), state->seq_pa045, sizeof state->seq_pa045, "PA045-03");
		|	load_programmable(this->name(), state->seq_pa046, sizeof state->seq_pa046, "PA046-02");
		|	load_programmable(this->name(), state->seq_pa047, sizeof state->seq_pa047, "PA047-02");
		|	load_programmable(this->name(), state->seq_pa048, sizeof state->seq_pa048, "PA048-02");
		|	state->seq_wcsram = (uint64_t*)CTX_GetRaw("SEQ_WCS", sizeof(uint64_t) << UADR_WIDTH);
		|	state->seq_top = (uint32_t*)CTX_GetRaw("SEQ_TOP", sizeof(uint32_t) << 10);
		|	state->seq_bot = (uint32_t*)CTX_GetRaw("SEQ_BOT", sizeof(uint32_t) << 10);
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|	unsigned urand = 0;
		|	unsigned rndx = 0;
		|	unsigned br_type = 0;
		|	unsigned br_tim = 0;
		|	bool macro_event = 0;
		|	unsigned lmp = 0;
		|	bool early_macro_pending = 0;
		|	bool maybe_dispatch = 0;
		|	bool sign_extend = 0;
		|	unsigned intreads = 0;
		|       bool carry_out = 0;
		|	bool uses_tos = 0;
		|	unsigned mem_start = 0;
		|
		|	void int_reads(void);
		|	unsigned group_sel(void);
		|	unsigned late_macro_pending(void);
		|	bool seq_conda(unsigned condsel);
		|	bool seq_cond9(unsigned condsel);
		|	bool seq_cond8(unsigned condsel);
		|       void nxt_lex_valid(void);
		|       bool condition(void);
		|	unsigned branch_offset(void);
		|	void q3clockstop(void);
		|	void seq_q2(void);
		|	void seq_q3(void);
		|	void seq_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|int_reads()
		|{
		|	unsigned internal_reads = UIR_SEQ_IRD;
		|	switch (urand & 3) {
		|	case 3:	state->seq_coff = state->seq_retrn_pc_ofs; break;
		|	case 2: state->seq_coff = branch_offset(); break;
		|	case 1: state->seq_coff = state->seq_macro_pc_offset; break;
		|	case 0: state->seq_coff = branch_offset(); break;
		|	}
		|	state->seq_coff ^= 0x7fff;
		|	if (internal_reads == 0) {
		|		state->seq_typ_bus = ~mp_typ_bus;
		|		state->seq_val_bus = ~mp_val_bus;
		|		return;
		|	}		
		|
		|	state->seq_typ_bus = state->seq_n_in_csa;
		|	state->seq_typ_bus |= state->seq_output_ob << 7;
		|	state->seq_typ_bus ^= 0xffffffff;
		|
		|	switch (internal_reads) {
		|	case 5:
		|		state->seq_typ_bus |= (state->seq_name_bus ^ 0xffffffff) << 32;
		|		break;
		|	default:
		|		state->seq_typ_bus |= (uint64_t)state->seq_cur_name << 32;
		|		break;
		|	}
		|	
		|	if (!(urand & 0x2)) {
		|		state->seq_val_bus = state->seq_pcseg << 32;
		|	} else {
		|		state->seq_val_bus = state->seq_retseg << 32;
		|	}
		|	state->seq_val_bus ^= 0xffffffffULL << 32; 
		|	state->seq_val_bus ^= (state->seq_coff >> 12) << 16;
		|	state->seq_val_bus ^= 0xffffULL << 16; 
		|	switch (internal_reads) {
		|	case 1:
		|		state->seq_val_bus |= state->seq_curins ^ 0xffff;
		|		break;
		|	case 2:
		|		state->seq_val_bus |= state->seq_display;
		|		break;
		|	case 3:
		|		state->seq_val_bus |= state->seq_topu & 0xffff;
		|		break;
		|	default:
		|		state->seq_val_bus |= (state->seq_coff << 4) & 0xffff;
		|		state->seq_val_bus |= (state->seq_curr_lex & 0xf);
		|		state->seq_val_bus ^= 0xffff;
		|		break;
		|	}
		|}
		|
		|unsigned
		|SCM_«mmm» ::
		|group_sel(void)
		|{
		|	static uint8_t tbl[16] = {3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 0, 1, 1, 1, 0};
		|
		|	unsigned retval = tbl[br_type];
		|	if (state->seq_uadr_mux) {
		|		retval |= 4;
		|	}
		|	return (retval);
		|}
		|
		|unsigned
		|SCM_«mmm» ::
		|late_macro_pending(void)
		|{
		|	unsigned csa = mp_csa_nve;
		|	unsigned dec = state->seq_decode >> 3;
		|
		|	if (csa < (dec & 7))
		|		return (0);
		|	if (csa > ((dec >> 3) | 12))
		|		return (1);
		|	if (state->seq_stop)
		|		return (2);
		|	if (!state->seq_m_res_ref)
		|		return (3);
		|	if (!state->seq_m_tos_invld)
		|		return (4);
		|	if (!state->seq_m_break_class)
		|		return (6);
		|	if (!state->seq_m_ibuff_mt)
		|		return (7);
		|	return (8);
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_conda(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x57: // FIELD_NUM_ERR
		|		return (!state->seq_field_number_error);
		|	case 0x56: // LATCHED_COND
		|		return (!state->seq_latched_cond);
		|	case 0x55: // E_MACRO_PEND
		|		return (!early_macro_pending);
		|	case 0x54: // E_MACRO_EVNT~6
		|		return (!((state->seq_emac >> 0) & 1));
		|	case 0x53: // E_MACRO_EVNT~5
		|		return (!((state->seq_emac >> 1) & 1));
		|	case 0x52: // E_MACRO_EVNT~3
		|		return (!((state->seq_emac >> 3) & 1));
		|	case 0x51: // E_MACRO_EVNT~2
		|		return (!((state->seq_emac >> 4) & 1));
		|	case 0x50: // E_MACRO_EVNT~0
		|		return (!((state->seq_emac >> 6) & 1));
		|	default:
		|		return (false);
		|	}
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_cond9(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x4f: // DISP_COND0
		|		return ((state->seq_decode & 0x7) == 0);
		|		break;
		|	case 0x4e: // True
		|		return (true);
		|		break;
		|	case 0x4d: // M_IBUFF_MT
		|		return (state->seq_m_ibuff_mt);
		|		break;
		|	case 0x4c: // M_BRK_CLASS
		|		return (state->seq_m_break_class);
		|		break;
		|	case 0x4b: // M_TOS_INVLD
		|		return (state->seq_m_tos_invld);
		|		break;
		|	case 0x4a: // M_RES_REF
		|		return (state->seq_m_res_ref);
		|		break;
		|	case 0x49: // M_OVERFLOW
		|		{
		|		unsigned csa = mp_csa_nve;
		|		unsigned dec = state->seq_decode >> 3;
		|		return (csa <= ((dec >> 3) | 12));
		|		}
		|		break;
		|	case 0x48: // M_UNDERFLOW
		|		{
		|		unsigned csa = mp_csa_nve;
		|		unsigned dec = state->seq_decode >> 3;
		|		return (csa >= (dec & 7));
		|		}
		|		break;
		|	default:
		|		return (false);
		|	}
		|}
		|
		|bool
		|SCM_«mmm» ::
		|seq_cond8(unsigned condsel)
		|{
		|
		|	switch (condsel) {
		|	case 0x47: // STACK_SIZE
		|		return (state->seq_stack_size_zero);
		|		break;
		|	case 0x46: // LATCHED_COND
		|		return (state->seq_latched_cond);
		|		break;
		|	case 0x45: // SAVED_LATCHED
		|		return (state->seq_saved_latched);
		|		break;
		|	case 0x44: // TOS_VLD.COND
		|		return (state->seq_tos_vld_cond);
		|		break;
		|	case 0x43: // LEX_VLD.COND
		|		return (state->seq_lxval);
		|		break;
		|	case 0x42: // IMPORT.COND
		|		return (state->seq_import_condition);
		|		break;
		|	case 0x41: // REST_PC_DEC
		|		return ((state->seq_rq >> 1) & 1);
		|		break;
		|	case 0x40: // RESTARTABLE
		|		return ((state->seq_rq >> 3) & 1);
		|		break;
		|	default:
		|		return (false);
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|nxt_lex_valid(void)
		|{
		|	unsigned lex_random;
		|	uint16_t dns;
		|	uint16_t dra;
		|	uint16_t dlr;
		|	lex_random = (rndx >> 5) & 0x7;
		|	dra = state->seq_resolve_address & 3;
		|	dlr = lex_random;
		|	if (lex_random & 0x2) {
		|		dns = 0xf;
		|	} else {
		|		dns = 0xf ^ (0x8 >> (state->seq_resolve_address >> 2));
		|	}
		|	unsigned adr;
		|	uint16_t nv = 0;
		|	adr = ((state->seq_lex_valid >> 12) & 0xf) << 5;
		|	adr |= dra << 3;
		|	adr |= ((dlr >> 2) & 1) << 2;
		|	adr |= ((dns >> 3) & 1) << 1;
		|	bool pm3 = !((dns & 0x7) && !(dlr & 1));
		|	adr |= pm3;
		|	nv |= (state->seq_pa041[adr] >> 4) << 12;
		|
		|	adr = ((state->seq_lex_valid >> 8) & 0xf) << 5;
		|	adr |= dra << 3;
		|	adr |= ((dlr >> 2) & 1) << 2;
		|	adr |= ((dns >> 2) & 1) << 1;
		|	bool pm2 = !((dns & 0x3) && !(dlr & 1));
		|	adr |= pm2;
		|	nv |= (state->seq_pa041[adr] >> 4) << 8;
		|
		|	adr = ((state->seq_lex_valid >> 4) & 0xf) << 5;
		|	adr |= dra << 3;
		|	adr |= ((dlr >> 2) & 1) << 2;
		|	adr |= ((dns >> 1) & 1) << 1;
		|	bool pm1 = !((dns & 0x1) && !(dlr & 1));
		|	adr |= pm1;
		|	nv |= (state->seq_pa041[adr] >> 4) << 4;
		|
		|	adr = ((state->seq_lex_valid >> 0) & 0xf) << 5;
		|	adr |= dra << 3;
		|	adr |= ((dlr >> 2) & 1) << 2;
		|	adr |= ((dns >> 0) & 1) << 1;
		|	adr |= (dlr >> 0) & 1;
		|	nv |= (state->seq_pa041[adr] >> 4) << 0;
		|
		|	state->seq_lex_valid = nv;
		|}
		|
		|bool
		|SCM_«mmm» ::
		|condition(void)
		|{
		|	unsigned condsel = UIR_SEQ_CSEL;
		|
		|	switch (condsel >> 3) {
		|	case 0x0: return(mp_condxf);
		|	case 0x1: return(mp_condxe);
		|	case 0x2: return(mp_condxd);
		|	case 0x3: return(mp_condxc);
		|	case 0x4: return(mp_condxb);
		|	case 0x5: return(mp_condxa);
		|	case 0x6: return(mp_condx9);
		|	case 0x7: return(mp_condx8);
		|	case 0x8: return(seq_cond8(condsel));
		|	case 0x9: return(seq_cond9(condsel));
		|	case 0xa: return(seq_conda(condsel));
		|	case 0xb: return(!(mp_condxc && mp_condxf));
		|	case 0xc: return(mp_condx3);
		|	case 0xd: return(mp_condx2);
		|	case 0xf: return(mp_condx0);
		|	default: return(1);
		|	}
		|}
		|
		|unsigned
		|SCM_«mmm» ::
		|branch_offset(void)
		|{
		|	bool oper;
		|	unsigned a;
		|	if (!state->seq_wanna_dispatch && !state->seq_m_ibuff_mt) {
		|		a = 0;
		|		oper = true;
		|	} else if (!state->seq_wanna_dispatch && state->seq_m_ibuff_mt) {
		|		a = state->seq_display;
		|		oper = false;
		|	} else if (state->seq_wanna_dispatch && !state->seq_m_ibuff_mt) {
		|		a = state->seq_curins;
		|		oper = true;
		|	} else {
		|		a = state->seq_curins;
		|		oper = true;
		|	}
		|	a &= 0x7ff;
		|	if (a & 0x400)
		|		a |= 0x7800;
		|	a ^= 0x7fff;
		|	unsigned b = state->seq_macro_pc_offset & 0x7fff;
		|	unsigned retval;
		|	if (oper) {
		|		if (state->seq_wanna_dispatch)
		|			a += 1;
		|		a &= 0x7fff;
		|		retval = a + b;
		|	} else {
		|		if (!state->seq_wanna_dispatch)
		|			a += 1;
		|		retval = b - a;
		|	}
		|	retval &= 0x7fff;
		|	return (retval);
		|}
		|
		|void
		|SCM_«mmm» ::
		|q3clockstop(void)
		|{
		|	bool event = true;
		|	mp_state_clk_stop = true;
		|	state->seq_s_state_stop = true;
		|	mp_clock_stop = true;
		|	mp_ram_stop = true;
		|
		|	if (mp_seq_halted && mp_seq_prepped) {
		|		state->seq_diag |= 0x01;
		|		mp_sync_freeze |= 1;
		|	} else {
		|		state->seq_diag &= ~0x01;
		|		mp_sync_freeze &= ~1;
		|	}
		|
		|	if (mp_fiu_freeze && !(state->seq_diag & 0x2)) {
		|		state->seq_diag |= 0x02;
		|		// output.freze = 1;
		|		mp_sync_freeze |= 2;
		|		ALWAYS_TRACE(<< "THAW1 " << state->seq_diag << " " << mp_sync_freeze);
		|	} else if (!mp_fiu_freeze && (state->seq_diag & 0x2) && !(state->seq_diag & 0x4)) {
		|		state->seq_diag |= 0x04;
		|		// output.sync = 1;
		|		mp_sync_freeze |= 4;
		|		ALWAYS_TRACE(<< "THAW2 " << state->seq_diag << " " << mp_sync_freeze);
		|	} else if (!mp_fiu_freeze && (state->seq_diag & 0x2) && (state->seq_diag & 0x4)) {
		|		state->seq_diag &= ~0x02;
		|		// output.freze = 0;
		|		mp_sync_freeze &= ~2;
		|		state->seq_countdown = 5;
		|		ALWAYS_TRACE(<< "THAW3 " << (state->seq_diag & 0x2) << " " << mp_sync_freeze << " " << state->seq_countdown);
		|	} else if (!mp_fiu_freeze && !(state->seq_diag & 0x2) && (state->seq_diag & 0x4)) {
		|		if (--state->seq_countdown == 0) {
		|			// output.sync = 0;
		|			state->seq_diag &= ~0x04;
		|			mp_sync_freeze &= ~4;
		|		}
		|		ALWAYS_TRACE(<< "THAW4 " <<  state->seq_diag << " " << mp_sync_freeze << " " << state->seq_countdown);
		|	}
		|
		|	state->seq_sf_stop = !(state->seq_diag == 0);
		|	mp_sf_stop = !(state->seq_diag == 0);
		|	mp_freeze = (state->seq_diag & 3) != 0;
		|
		|	unsigned clock_stop = 0;
		|	state->seq_clock_stop_1 = !(mp_clock_stop_6 && mp_clock_stop_7 && mp_below_tcp);
		|	if (    mp_clock_stop_0) { clock_stop |= 0x40; }
		|	if (state->seq_clock_stop_1) { clock_stop |= 0x20; }
		|	if (    mp_clock_stop_3) { clock_stop |= 0x10; }
		|	if (    mp_clock_stop_4) { clock_stop |= 0x08; }
		|	if (state->seq_clock_stop_5) { clock_stop |= 0x04; }
		|	if (mp_clock_stop_6) { clock_stop |= 0x02; }
		|	if (mp_clock_stop_7) { clock_stop |= 0x01; }
		|	
		|	if ((clock_stop | 0x01) != 0x7f) {
		|		mp_state_clk_stop = false;
		|		event = false;
		|	}
		|	if (clock_stop != 0x7f) {
		|		mp_clock_stop = false;
		|		if (!mp_csa_write_enable) {
		|			mp_ram_stop = false;
		|		}
		|	}
		|	if ((clock_stop | 0x03) != 0x7f) {
		|		state->seq_s_state_stop = false;
		|	}
		|
		|	if (state->seq_sf_stop) {
		|		mp_clock_stop = false;
		|		mp_state_clk_stop = false;
		|		state->seq_s_state_stop = false;
		|		if (!mp_csa_write_enable) {
		|			mp_ram_stop = false;
		|		}
		|	}
		|	mp_state_clk_en= !(mp_state_clk_stop && mp_clock_stop_7);
		|	mp_mem_abort_el = event;
		|}
		|
		|void
		|SCM_«mmm» ::
		|seq_q2(void)
		|{
		|	state->seq_tos_vld_cond = !(state->seq_foo7 || RNDX(RND_TOS_VLB));				// cond, q4
		|	state->seq_m_tos_invld = !(state->seq_uses_tos && state->seq_tos_vld_cond);				// lmp, cond
		|
		|	state->seq_check_exit_ue = !(mp_uevent_enable && RNDX(RND_CHK_EXIT) && state->seq_carry_out);	// q4
		|	state->seq_m_res_ref = !(state->seq_lxval && !(state->seq_display >> 15));				// lmp, cond
		|
		|	uint64_t val = state->seq_val_bus >> 32;
		|	val &= 0xffffff;
		|
		|	unsigned tmp = (val >> 7) ^ state->seq_curins;
		|	tmp &= 0x3ff;
		|	state->seq_field_number_error = tmp != 0x3ff;
		|	state->seq_ferr = !(state->seq_field_number_error && !(RNDX(RND_FLD_CHK) || !mp_uevent_enable));
		|
		|	state->seq_ram[(state->seq_adr + 1) & 0xf] = state->seq_topu;
		|
		|	state->seq_l_macro_hic = true;
		|	unsigned nua;
		|	if (state->seq_bad_hint) {
		|		nua = state->seq_other;
		|	} else if (state->seq_late_macro_event) {
		|		// Not tested by expmon_test_seq ?
		|		nua = state->seq_late_u << 3;
		|		nua ^= (7 << 3);
		|		nua |= 0x0140;
		|		state->seq_l_macro_hic = false;
		|	} else if (state->seq_uev != 16) {
		|		nua = state->seq_uev;
		|		nua <<= 3;
		|		nua |= 0x0180;
		|	} else {
		|		unsigned sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|			nua = UIR_SEQ_BRN;
		|			nua += state->seq_fiu;
		|			break;
		|		case 1:
		|			nua = state->seq_uadr_decode >> 3;
		|			nua <<= 1;
		|			break;
		|		case 2:
		|			nua = (state->seq_topu ^ 0xffff) & 0x3fff;
		|			break;
		|		case 3:
		|		case 4:
		|			nua = mp_cur_uadr;
		|			nua += 1;
		|			break;
		|		case 5:
		|		case 6:
		|		case 7:
		|			nua = UIR_SEQ_BRN;
		|			break;
		|		default:
		|			nua = 0;
		|			assert(sel < 8);
		|			break;
		|		}
		|	}
		|	if (!state->seq_sf_stop && mp_seq_prepped) {
		|		mp_nua_bus = nua & 0x3fff;
		|	}
		|	state->seq_clock_stop_5 = (state->seq_check_exit_ue && state->seq_ferr);
		|	mp_clock_stop_6 = !(!state->seq_bad_hint && !state->seq_late_macro_event && state->seq_uev != 16);
		|	mp_clock_stop_7 = !state->seq_bad_hint && state->seq_l_macro_hic;
		|	mp_state_clk_en = !(mp_state_clk_stop && mp_clock_stop_7);
		|}
		|
		|void
		|SCM_«mmm» ::
		|seq_q3(void)
		|{
		|	q3clockstop();
		|	int_reads();
		|	state->seq_q3cond = condition();
		|	state->seq_bad_hint_enable = !((!mp_clock_stop_6) || (state->seq_late_macro_event && !state->seq_bad_hint));
		|	unsigned pa040a = 0;
		|	pa040a |= (state->seq_decode & 0x7) << 6;
		|	if (state->seq_wanna_dispatch) pa040a |= 0x20;
		|	if (RNDX(RND_ADR_SEL)) pa040a |= 0x10;
		|	if (state->seq_import_condition) pa040a |= 0x08;
		|	if (state->seq_stop) pa040a |= 0x04;
		|	if (!maybe_dispatch) pa040a |= 0x02;
		|	if (state->seq_bad_hint) pa040a |= 0x01;
		|	unsigned pa040d = state->seq_pa040[pa040a];
		|
		|	bool bar8;
		|	lmp = late_macro_pending();
		|	macro_event = (!state->seq_wanna_dispatch) && (early_macro_pending || (lmp != 8));
		|	if (macro_event) {
		|		bar8 = (macro_event && !early_macro_pending) && (lmp >= 7);
		|	} else {
		|		bar8 = !((pa040d >> 1) & 1);
		|	}
		|
		|	if (!bar8) {
		|		mp_mem_abort_e = false;
		|	} else if (mp_mem_cond) {
		|		mp_mem_abort_e = true;
		|	} else if (mp_mem_cond_pol ^ state->seq_q3cond) {
		|		mp_mem_abort_e = true;
		|	} else {
		|		mp_mem_abort_e = false;
		|	}
		|
		|	if (RNDX(RND_TOS_VLB) && !state->seq_stop) {
		|		state->seq_tost = state->seq_typ_bus >> 32;
		|		state->seq_vost = state->seq_val_bus >> 32;
		|		state->seq_tosof = (state->seq_typ_bus >> 7) & 0xfffff;
		|	}
		|	if (maybe_dispatch) {
		|		switch (mem_start) {
		|		case 0:
		|		case 1:
		|		case 2:
		|			state->seq_name_bus = state->seq_namram[state->seq_resolve_address] ^ 0xffffffff;
		|			break;
		|		case 3:
		|		case 7:
		|			state->seq_name_bus = state->seq_tost ^ 0xffffffff;
		|			break;
		|		default:
		|			state->seq_name_bus = state->seq_vost ^ 0xffffffff;
		|			break;
		|		}
		|	} else {
		|		state->seq_name_bus = state->seq_namram[state->seq_resolve_address] ^ 0xffffffff;
		|	}
		|	if (!(state->seq_foo9 || mp_clock_stop_6)) {
		|		state->seq_treg = 0;
		|		state->seq_foo7 = false;
		|	}
		|	if (mp_adr_oe & 0x8) {
		|		if (macro_event) {
		|			mp_spc_bus = 0x6;
		|		} else {
		|			mp_spc_bus = (pa040d >> 3) & 0x7;
		|		}
		|		bool adr_is_code = !((!macro_event) && (pa040d & 0x01));
		|		bool resolve_drive;
		|		if (!macro_event) {
		|			resolve_drive = !((pa040d >> 6) & 1);
		|		} else {
		|			resolve_drive = true;
		|		}
		|		if (!resolve_drive) {
		|			mp_adr_bus = state->seq_resolve_offset << 7;
		|		} else if (adr_is_code) {
		|			mp_adr_bus = (state->seq_coff >> 3) << 7;
		|		} else {
		|			mp_adr_bus = state->seq_output_ob << 7;
		|		}
		|
		|		uint64_t branch;
		|		branch = branch_offset() & 7;
		|		branch ^= 0x7;
		|		mp_adr_bus |= branch << 4;
		|		if (!adr_is_code) {
		|			mp_adr_bus |= state->seq_name_bus << 32;
		|		} else if (!(urand & 0x2)) {
		|			mp_adr_bus |= state->seq_pcseg << 32; 
		|		} else {
		|			mp_adr_bus |= state->seq_retseg << 32;
		|		}
		|	}
		|	bool bad_hint_disp = (!state->seq_bad_hint || (state->seq_bhreg & 0x08));
		|	mp_mem_abort_l = bad_hint_disp && !(RNDX(RND_L_ABRT) && !state->seq_stop);
		|}
		|
		|void
		|SCM_«mmm» ::
		|seq_q4(void)
		|{
		|	bool aclk = !state->seq_sf_stop;
		|	bool sclke = !(state->seq_s_state_stop && !state->seq_stop);
		|	bool sclk = aclk && !sclke;
		|	bool state_clock = !sclke;
		|
		|	bool bhen = !((state->seq_late_macro_event && !state->seq_bad_hint) || (!mp_clock_stop_6));
		|	bool bhcke = !(state->seq_s_state_stop && bhen);
		|	if (state_clock) {
		|		nxt_lex_valid();
		|	}
		|	bool dispatch = state->seq_wanna_dispatch || early_macro_pending || (lmp != 8);
		|	if (state_clock && !RNDX(RND_RES_OFFS)) {
		|		state->seq_tosram[state->seq_resolve_address] = (state->seq_typ_bus >> 7) & 0xfffff;
		|	}
		|	if (aclk) {
		|		state->seq_late_macro_event = !(sclke || !(macro_event && !early_macro_pending));
		|		if (!mp_seq_halted) {
		|			mp_seq_halted = !(sclke || RNDX(RND_HALT));
		|			if (mp_seq_halted) ALWAYS_TRACE(<< "THAW HALTED");
		|		}
		|	}
		|	if (state_clock && !state->seq_ibld) {
		|		state->seq_macro_ins_typ = state->seq_typ_bus;
		|		state->seq_macro_ins_val = state->seq_val_bus;
		|	}
		|
		|	if (state_clock && !RNDX(RND_RETRN_LD)) {
		|		state->seq_retrn_pc_ofs = state->seq_macro_pc_offset;
		|	}
		|
		|	if (!bhcke && !macro_event) {
		|		unsigned mode = 0;
		|		unsigned u = 0;
		|		if (state->seq_cload) u |= 1;
		|		if (state->seq_wanna_dispatch) u |= 2;
		|		switch (u) {
		|		case 0: mode = 1; break;
		|		case 1: mode = 1; break;
		|		case 2:
		|			if (!state->seq_bad_hint) {
		|				state->seq_m_pc_mb = RNDX(RND_M_PC_MD0);
		|			} else {
		|				state->seq_m_pc_mb = !((state->seq_bhreg >> 2) & 1);
		|			}
		|
		|			if (state->seq_m_pc_mb) mode |= 2;
		|			if (RNDX(RND_M_PC_MD1)) mode |= 1;
		|			break;
		|		case 3: mode = 0; break;
		|		}
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			if (!RNDX(RND_M_PC_MUX)) {
		|				tmp = state->seq_val_bus;
		|				state->seq_word = tmp >> 4;
		|				state->seq_macro_pc_offset = (tmp >> 4) & 0x7fff;
		|			} else {
		|				state->seq_macro_pc_offset = branch_offset();
		|				state->seq_word = state->seq_macro_pc_offset;
		|			}
		|		} else if (mode == 2) {
		|			state->seq_macro_pc_offset += 1;
		|			state->seq_word += 1;
		|		} else if (mode == 1) {
		|			state->seq_macro_pc_offset -= 1;
		|			state->seq_word += 7;
		|		}
		|		state->seq_word &= 7;
		|	}
		|	if (state_clock && !RNDX(RND_CUR_LEX)) {
		|		state->seq_curr_lex = state->seq_val_bus & 0xf;
		|		state->seq_curr_lex ^= 0xf;
		|	}
		|
		|	if (aclk) {
		|		early_macro_pending = mp_macro_event != 0;
		|		state->seq_emac = mp_macro_event ^ 0x7f;
		|		if (early_macro_pending) {
		|			state->seq_uadr_decode = 0x0400 + 0x20 * fls(mp_macro_event);
		|		}
		|	}
		|	bool crnana = !(RNDX(RND_INSTR_LD) && dispatch);
		|
		|	if (sclk) {
		|		unsigned dsp = 0;
		|		if (!RNDX(RND_INSTR_MX)) {
		|			dsp = state->seq_display;
		|		} else {
		|			uint64_t tval = state->seq_val_bus;
		|			dsp = tval & 0xffff;
		|		}
		|		dsp ^= 0xffff;;
		|			
		|		if (crnana && state->seq_topbot)
		|			state->seq_ctop = dsp;
		|		if (crnana && !state->seq_topbot)
		|			state->seq_cbot = dsp;
		|	}
		|			
		|	if (!bhcke) {
		|		bool dmdisp = !(!state->seq_bad_hint || (state->seq_bhreg & 0x04));
		|		bool crnor0a = !(crnana || dmdisp);
		|		if (!crnor0a)
		|			state->seq_topbot = !state->seq_topbot;
		|	}
		|
		|	if (state->seq_topbot) {
		|		state->seq_curins = state->seq_cbot;
		|	} else {
		|		state->seq_curins = state->seq_ctop;
		|	}
		|
		|	if (sclk && !RNDX(RND_BR_MSK_L)) {
		|		uint64_t tmp = state->seq_val_bus;
		|		state->seq_break_mask = (tmp >> 16) & 0xffff;
		|	}
		|
		|	uint32_t *ciptr;
		|	if (state->seq_curins & 0xfc00) {
		|		ciptr = &state->seq_top[state->seq_curins >> 6];
		|	} else {
		|		ciptr = &state->seq_bot[state->seq_curins & 0x3ff];
		|	}
		|
		|	unsigned ccl = (*ciptr >> 4) & 0xf;
		|
		|	if (ccl == 0) {
		|		state->seq_m_break_class = false;
		|	} else {
		|		state->seq_m_break_class = (state->seq_break_mask >> (15 - ccl)) & 1;
		|	}
		|	state->seq_m_break_class = !state->seq_m_break_class;
		|
		|	if (state_clock) {
		|		if (!RNDX(RND_NAME_LD)) {
		|			state->seq_cur_name = state->seq_typ_bus >> 32;
		|		}
		|			
		|		if (!RNDX(RND_RES_NAME)) {
		|			state->seq_namram[state->seq_resolve_address] = state->seq_typ_bus >> 32;
		|		}
		|
		|		if (!RNDX(RND_RETRN_LD)) {
		|			state->seq_retseg = state->seq_pcseg;
		|		}
		|		if (!RNDX(RND_M_PC_LDH)) {
		|			//unsigned val;
		|			//val = state->seq_val_bus >> 32;
		|			//val ^= 0xffffffff;
		|			state->seq_pcseg = (~state->seq_val_bus >> 32) & 0xffffff;
		|		}
		|		if (!RNDX(RND_SAVE_LD)) {
		|			state->seq_savrg = state->seq_resolve_offset;
		|			state->seq_carry_out = carry_out;
		|		}
		|
		|		uint64_t cnb;
		|		if (!RNDX(RND_CNTL_MUX)) {
		|			cnb = ~state->seq_typ_bus;
		|		} else {
		|			cnb = mp_fiu_bus;
		|		}
		|		//cnb &= 0xffffffffULL;
		|		cnb >>= 7;
		|		cnb &= 0xfffff;
		|
		|		if (!RNDX(RND_PRED_LD)) {
		|			state->seq_pred = cnb;
		|		}
		|		unsigned csa_cntl = mp_csa_cntl;
		|
		|		bool ten = (csa_cntl != 2 && csa_cntl != 3);
		|		bool tud = !(csa_cntl & 1);
		|		if (!RNDX(RND_TOP_LD)) {
		|			state->seq_topcnt = cnb;
		|		} else if (ten) {
		|			// Nothing
		|		} else if (tud) {
		|			state->seq_topcnt += 1;
		|		} else {
		|			state->seq_topcnt += 0xfffff;
		|		}
		|		state->seq_topcnt &= 0xfffff;
		|	}
		|
		|	if (state->seq_s_state_stop && state->seq_l_macro_hic) {
		|		bool xwrite;
		|		bool pop;
		|		unsigned stkinpsel = 0;
		|		if (!mp_clock_stop_6) {
		|			xwrite = true;
		|			pop = true;
		|			stkinpsel = 3;
		|		} else if (!state->seq_push) {
		|			xwrite = true;
		|			pop = false;
		|			if (!state->seq_push_br) stkinpsel |= 2;
		|			if (state->seq_bad_hint) stkinpsel |= 1;
		|		} else {
		|			xwrite = !RNDX(RND_PUSH);
		|			pop = !!(state->seq_preturn || RNDX(RND_POP));
		|			stkinpsel = 0x1;;
		|		}
		|
		|		if (xwrite) {
		|			switch(stkinpsel) {
		|			case 0:
		|				state->seq_topu = UIR_SEQ_BRN;
		|				if (state->seq_q3cond) state->seq_topu |= (1<<15);
		|				if (state->seq_latched_cond) state->seq_topu |= (1<<14);
		|				state->seq_topu ^= 0xffff;
		|				break;
		|			case 1:
		|				state->seq_topu = mp_fiu_bus;
		|				state->seq_topu &= 0xffff;
		|				break;
		|			case 2:
		|				state->seq_topu = mp_cur_uadr;
		|				if (state->seq_q3cond) state->seq_topu |= (1<<15);
		|				if (state->seq_latched_cond) state->seq_topu |= (1<<14);
		|				state->seq_topu += 1;
		|				state->seq_topu ^= 0xffff;
		|				break;
		|			case 3:
		|				state->seq_topu = mp_cur_uadr;
		|				if (state->seq_q3cond) state->seq_topu |= (1<<15);
		|				if (state->seq_latched_cond) state->seq_topu |= (1<<14);
		|				state->seq_topu ^= 0xffff;
		|				break;
		|			}
		|		} else if (pop) {
		|			state->seq_topu = state->seq_ram[state->seq_adr];
		|		}
		|		state->seq_saved_latched = !((state->seq_topu >> 14) & 0x1);
		|
		|		if (RNDX(RND_CLEAR_ST) && !state->seq_stop) {
		|			state->seq_adr = xwrite;
		|		} else if (xwrite || pop) {
		|			if (xwrite) {
		|				state->seq_adr = (state->seq_adr + 1) & 0xf;
		|			} else {
		|				state->seq_adr = (state->seq_adr + 0xf) & 0xf;
		|			}
		|		}
		|		state->seq_stack_size_zero = state->seq_adr == 0;
		|	}
		|
		|	if (sclk) {
		|		state->seq_fiu = mp_fiu_bus;
		|		state->seq_fiu &= 0x3fff;
		|	}
		|
		|	if (aclk) {
		|		if (!maybe_dispatch) {
		|			state->seq_late_u = 7;
		|		} else {
		|			state->seq_late_u = lmp;
		|			if (state->seq_late_u == 8)
		|				state->seq_late_u = 7;
		|		}
		|		unsigned sel = group_sel();
		|		switch (sel) {
		|		case 0:
		|		case 7:
		|			state->seq_other = mp_cur_uadr + 1;
		|			break;
		|		case 1:
		|		case 2:
		|		case 3:
		|			state->seq_other = UIR_SEQ_BRN;
		|			break;
		|		case 4:
		|			state->seq_other = UIR_SEQ_BRN;
		|			state->seq_other += state->seq_fiu;
		|			break;
		|		case 5:
		|			state->seq_other = state->seq_decode >> 3;
		|			state->seq_other <<= 1;
		|			break;
		|		case 6:
		|			state->seq_other = (state->seq_topu ^ 0xffff) & 0x3fff;
		|			break;
		|		default:
		|			assert(sel < 8);
		|			break;
		|		}
		|	}
		|
		|	if (aclk) {
		|		if (state->seq_check_exit_ue) {
		|			mp_seq_uev &= ~UEV_CK_EXIT;
		|		} else {
		|			mp_seq_uev |= UEV_CK_EXIT;
		|		}
		|		if (state->seq_ferr) {
		|			mp_seq_uev &= ~UEV_FLD_ERR;
		|		} else {
		|			mp_seq_uev |= UEV_FLD_ERR;
		|		}
		|		if (state->seq_clock_stop_1) {
		|			mp_seq_uev &= ~UEV_NEW_PAK;
		|		} else {
		|			mp_seq_uev |= UEV_NEW_PAK;
		|		}
		|
		|		state->seq_uev = 16 - fls(mp_seq_uev);
		|
		|		if (state->seq_s_state_stop) {
		|			mp_cur_uadr = mp_nua_bus;
		|		}
		|
		|		unsigned adr = 0;
		|		if (mp_clock_stop_6)
		|			adr |= 0x02;
		|		if (!macro_event)
		|			adr |= 0x04;
		|		adr |= br_tim << 3;
		|		adr |= br_type << 5;
		|		unsigned rom = state->seq_pa044[adr];
		|
		|		if (!state_clock) {
		|			rom |= 0x2;
		|		} else {
		|			rom ^= 0x2;
		|		}
		|		if (!bhcke) {
		|			state->seq_bhreg = rom;
		|		}
		|			
		|		state->seq_hint_last = (state->seq_bhreg >> 1) & 1;
		|		state->seq_hint_t_last = (state->seq_bhreg >> 0) & 1;
		|
		|		bool bad_hint_disp = (!state->seq_bad_hint || (state->seq_bhreg & 0x08));
		|		if (state->seq_s_state_stop && state->seq_bad_hint_enable && bad_hint_disp) {
		|			unsigned restrt_rnd = 0;
		|			restrt_rnd |= RNDX(RND_RESTRT0) ? 2 : 0;
		|			restrt_rnd |= RNDX(RND_RESTRT1) ? 1 : 0;
		|			if (!state->seq_wanna_dispatch) {
		|				state->seq_rreg = 0xa;
		|			} else if (restrt_rnd != 0) {
		|				state->seq_rreg = (restrt_rnd & 0x3) << 1;
		|			} else {
		|				state->seq_rreg &= 0xa;
		|			}
		|			if (macro_event) {
		|				state->seq_rreg &= ~0x2;
		|			}
		|			state->seq_treg = 0x3;
		|			bool dnan0d = !(dispatch && RNDX(RND_PRED_LD));
		|			bool tsnor0b = !(dnan0d || state->seq_tos_vld_cond);
		|			if (tsnor0b)
		|				state->seq_treg |= 0x8;
		|			if (!state->seq_tos_vld_cond)
		|				state->seq_treg |= 0x4;
		|		} else if (state->seq_s_state_stop && state->seq_bad_hint_enable) {
		|			state->seq_rreg <<= 1;
		|			state->seq_rreg &= 0xe;
		|			state->seq_rreg |= 0x1;
		|			state->seq_treg <<= 1;
		|			state->seq_treg &= 0xe;
		|			state->seq_treg |= 0x1;
		|		}
		|		state->seq_rq = state->seq_rreg;
		|		state->seq_foo7 = state->seq_treg >> 3;
		|
		|		unsigned lin = 0;
		|		lin |= state->seq_latched_cond << 3;
		|		unsigned condsel = UIR_SEQ_CSEL;
		|		uint8_t pa042 = state->seq_pa042[condsel << 2];
		|		bool is_e_ml = (pa042 >> 7) & 1;
		|		lin |= is_e_ml << 2;
		|		lin |= UIR_SEQ_LUIR << 1;
		|		lin |= state->seq_q3cond << 0;
		|
		|		if (state_clock) {
		|			state->seq_lreg = lin;
		|			if (lin & 0x4) {
		|				state->seq_last_late_cond = condition();
		|			}
		|		}
		|
		|		switch(state->seq_lreg & 0x6) {
		|		case 0x0:
		|		case 0x4:
		|			state->seq_latched_cond = (state->seq_lreg >> 3) & 1;
		|			break;
		|		case 0x2:
		|			state->seq_latched_cond = (state->seq_lreg >> 0) & 1;
		|			break;
		|		case 0x6:
		|			state->seq_latched_cond = state->seq_last_late_cond;
		|			break;
		|		}
		|	}
		|
		|	bool last_cond_late = (state->seq_lreg >> 2) & 1;
		|	if (state->seq_hint_last) {
		|		state->seq_bad_hint = false;
		|	} else if (!last_cond_late && !state->seq_hint_t_last) {
		|		state->seq_bad_hint = state->seq_lreg & 1;
		|	} else if (!last_cond_late &&  state->seq_hint_t_last) {
		|		state->seq_bad_hint = !(state->seq_lreg & 1);
		|	} else if ( last_cond_late && !state->seq_hint_t_last) {
		|		state->seq_bad_hint = state->seq_last_late_cond;
		|	} else if ( last_cond_late &&  state->seq_hint_t_last) {
		|		state->seq_bad_hint = !state->seq_last_late_cond;
		|	}
		|
		|	switch(state->seq_word) {
		|	case 0x0: state->seq_display = state->seq_macro_ins_val >>  0; break;
		|	case 0x1: state->seq_display = state->seq_macro_ins_val >> 16; break;
		|	case 0x2: state->seq_display = state->seq_macro_ins_val >> 32; break;
		|	case 0x3: state->seq_display = state->seq_macro_ins_val >> 48; break;
		|	case 0x4: state->seq_display = state->seq_macro_ins_typ >>  0; break;
		|	case 0x5: state->seq_display = state->seq_macro_ins_typ >> 16; break;
		|	case 0x6: state->seq_display = state->seq_macro_ins_typ >> 32; break;
		|	case 0x7: state->seq_display = state->seq_macro_ins_typ >> 48; break;
		|	}
		|	state->seq_display &= 0xffff;
		|
		|	if (!early_macro_pending) {
		|		unsigned ai = state->seq_display;
		|		ai ^= 0xffff;
		|		bool top = (state->seq_display >> 10) != 0x3f;
		|		uint32_t *ptr;
		|		if (top)
		|			ptr = &state->seq_top[ai >> 6];
		|		else
		|			ptr = &state->seq_bot[ai & 0x3ff];
		|		state->seq_uadr_decode = (*ptr >> 16);
		|		state->seq_decode = (*ptr >> 8) & 0xff;
		|	}
		|	state->seq_uses_tos = (state->seq_uadr_decode >> 2) & 1;
		|	state->seq_ibuf_fill = (state->seq_uadr_decode >> 1) & 1;
		|	if (state_clock) {
		|		state->seq_n_in_csa = mp_csa_nve;
		|	}
		|	if (aclk) {
		|		state->seq_foo9 = !RNDX(RND_TOS_VLB);
		|	}
		|	mp_clock_stop_7 = !state->seq_bad_hint && state->seq_l_macro_hic;
		|	mp_state_clk_en = !(mp_state_clk_stop && mp_clock_stop_7);
		|	if (!state->seq_sf_stop && mp_seq_prepped) {
		|		state->seq_uir = state->seq_wcsram[mp_nua_bus] ^ (0x7fULL << 13);	// Invert condsel
		|		mp_nxt_cond_sel = UIR_SEQ_CSEL;
		|	}
		|}
		|
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4"
        yield "PIN_H2.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q1pos = PIN_Q2.negedge();
		|	bool h1pos = PIN_H2.negedge();
		|
		|if (h1pos) {
		|
		|	urand = UIR_SEQ_URAND;
		|	rndx = state->seq_pa048[urand | (state->seq_bad_hint ? 0x100 : 0)] << 24;
		|	rndx |= state->seq_pa046[urand | (state->seq_bad_hint ? 0x100 : 0)] << 16;
		|	rndx |=  state->seq_pa045[urand | 0x100] << 8;
		|	rndx |= state->seq_pa047[urand | 0x100];
		|
		|	br_type = UIR_SEQ_BRTYP;
		|	maybe_dispatch = 0xb < br_type && br_type < 0xf;
		|
		|	if (mp_fiu_oe == 0x8)
		|		mp_fiu_bus = state->seq_topu;
		|	if (mp_seqtv_oe) {
		|		h1pos = false;
		|	}
		|}
		|
		|if (h1pos || q1pos) {
		|	int_reads();
		|	unsigned lex_adr = UIR_SEQ_LAUIR;
		|
		|	if (maybe_dispatch && !(state->seq_display >> 15)) {
		|		switch (lex_adr) {
		|		case 0:	state->seq_resolve_address = (state->seq_display >> 9) & 0xf; break;
		|		case 1: state->seq_resolve_address = 0xf; break;
		|		case 2: state->seq_resolve_address = 0xf; break;
		|		case 3: state->seq_resolve_address = 0xe; break;
		|		}
		|	} else {
		|		switch (lex_adr) {
		|		case 0:	state->seq_resolve_address = state->seq_curr_lex ^ 0xf; break;
		|		case 1:
		|			state->seq_resolve_address = (state->seq_val_bus & 0xf) + 1; 
		|			break;
		|		case 2: state->seq_resolve_address = 0xf; break;
		|		case 3: state->seq_resolve_address = 0xe; break;
		|		}
		|	}
		|	
		|	state->seq_resolve_address &= 0xf;
		|	if (lex_adr == 1) {
		|		state->seq_import_condition = true;
		|		sign_extend = true;
		|	} else {
		|		state->seq_import_condition = state->seq_resolve_address != 0xf;
		|		sign_extend = state->seq_resolve_address <= 0xd;
		|	}
		|
		|	state->seq_lxval = !((state->seq_lex_valid >> (15 - state->seq_resolve_address)) & 1);
		|
		|	if (!maybe_dispatch) {
		|		uses_tos = false;
		|		mem_start = 7;
		|		intreads = UIR_SEQ_IRD & 3;
		|	} else {
		|		uses_tos = state->seq_uses_tos;
		|		mem_start = state->seq_decode & 0x7;
		|		if (mem_start == 0 || mem_start == 4) {
		|			intreads = 3;
		|		} else {
		|			intreads = 1;
		|		}
		|	}
		|
		|	unsigned offs;
		|	if (uses_tos) {
		|		if (RNDX(RND_TOS_VLB)) {
		|			offs = (state->seq_typ_bus >> 7) & 0xfffff;
		|		} else {
		|			offs = state->seq_tosof;
		|		}
		|	} else {
		|		offs = state->seq_tosram[state->seq_resolve_address];
		|	}
		|	offs ^= 0xfffff;
		|	offs &= 0xfffff;
		|
		|	bool d7 = (state->seq_display & 0x8100) == 0;
		|	unsigned sgdisp = state->seq_display & 0xff;
		|	if (!d7)
		|		sgdisp |= 0x100;
		|	if (!(sign_extend && d7))
		|		sgdisp |= 0xffe00;
		|
		|	bool acin = ((mem_start & 1) != 0);
		|	sgdisp &= 0xfffff;
		|	state->seq_resolve_offset = 0;
		|
		|	switch(mem_start) {
		|	case 0:
		|	case 2:
		|		state->seq_resolve_offset = offs + sgdisp + 1;
		|		carry_out = (state->seq_resolve_offset >> 20) == 0;
		|		break;
		|	case 1:
		|	case 3:
		|		state->seq_resolve_offset = (1<<20) + offs - (sgdisp + 1);
		|		carry_out = acin && (offs == 0);
		|		break;
		|	case 4:
		|	case 6:
		|		state->seq_resolve_offset = sgdisp ^ 0xfffff;
		|		// Carry is probably "undefined" here.
		|		break;
		|	case 5:
		|	case 7:
		|		state->seq_resolve_offset = offs;
		|		carry_out = acin && (offs == 0);
		|		break;
		|	}
		|
		|	state->seq_resolve_offset &= 0xfffff;
		|
		|	if (intreads == 3) {
		|		state->seq_output_ob = state->seq_pred;
		|	} else if (intreads == 2) {
		|		state->seq_output_ob = state->seq_topcnt;
		|	} else if (intreads == 1) {
		|		state->seq_output_ob = state->seq_resolve_offset;
		|	} else if (intreads == 0) {
		|		state->seq_output_ob = state->seq_savrg;
		|	} else {
		|		state->seq_output_ob = 0xfffff;
		|	}
		|	state->seq_output_ob &= 0xfffff;
		|	if (!maybe_dispatch) {
		|		state->seq_name_bus = state->seq_namram[state->seq_resolve_address] ^ 0xffffffff;
		|	} else {
		|		state->seq_name_bus = 0xffffffff;
		|	}
		|	state->seq_cload = RNDX(RND_CIB_PC_L) && (!state->seq_bad_hint) && (!condition());
		|	bool ibuff_ld = !(state->seq_cload || RNDX(RND_IBUFF_LD));
		|	state->seq_ibld = !ibuff_ld;
		|	bool ibemp = !(ibuff_ld || (state->seq_word != 0));
		|	state->seq_m_ibuff_mt = !(ibemp && state->seq_ibuf_fill);
		|
		|}
		|	if (h1pos) {	// NB See above for early termination of h1pos on no OE signal.
		|		int_reads();	// Necessary
		|
		|		mp_typ_bus = ~state->seq_typ_bus;
		|		mp_val_bus = ~state->seq_val_bus;
		|	}
		|
		|	if (q1pos) {
		|
		|		br_tim = UIR_SEQ_BRTIM;
		|		unsigned bhow;
		|		bool brtm3;
		|		if (state->seq_bad_hint) {
		|			bhow = 2;
		|			brtm3 = ((state->seq_bhreg) >> 5) & 1;
		|		} else {
		|			bhow = br_tim;
		|			brtm3 = br_type & 1;
		|
		|		}
		|
		|		switch (bhow) {
		|		case 0: state->seq_uadr_mux = !condition(); break;
		|		case 1: state->seq_uadr_mux = !state->seq_latched_cond; break;
		|		case 2: state->seq_uadr_mux = false; break;
		|		case 3: state->seq_uadr_mux = true; break;
		|		}
		|		if (brtm3)
		|			state->seq_uadr_mux = !state->seq_uadr_mux;
		|
		|		unsigned adr = 0;
		|		if (state->seq_bad_hint) adr |= 0x01;
		|		adr |= (br_type << 1);
		|		if (state->seq_bhreg & 0x20) adr |= 0x20;
		|		if (state->seq_bhreg & 0x40) adr |= 0x80;
		|		if (state->seq_bhreg & 0x80) adr |= 0x100;
		|		unsigned rom = state->seq_pa043[adr];
		|		state->seq_wanna_dispatch = !(((rom >> 5) & 1) && !state->seq_uadr_mux);	// Changes @15, 20, 60ns
		|		state->seq_preturn = !(((rom >> 3) & 1) ||  state->seq_uadr_mux);
		|		state->seq_push_br =    (rom >> 1) & 1;
		|		state->seq_push   = !(((rom >> 0) & 1) || !(((rom >> 2) & 1) || !state->seq_uadr_mux));
		|		state->seq_stop = !(!state->seq_bad_hint && (state->seq_uev == 16) && !state->seq_late_macro_event);
		|		bool evnan0d = !(UIR_SEQ_ENMIC && (state->seq_uev == 16));
		|		mp_uevent_enable = !(evnan0d || state->seq_stop);
		|	}
		|
		|	if (PIN_Q2.posedge()) {
		|		seq_q2();
		|	} else if (PIN_Q4.negedge()) {
		|		seq_q3();
		|	} else if (PIN_Q4.posedge()) {
		|		seq_q4();
		|	}
		|
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("SEQ", PartModelDQ("SEQ", SEQ))
