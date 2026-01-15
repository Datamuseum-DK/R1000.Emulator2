/*-
 * Copyright (c) 2021 Poul-Henning Kamp
 * All rights reserved.
 *
 * Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
 *
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 */

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <strings.h>
#include <stdbool.h>
#include <pthread.h>

#include "Infra/r1000.h"
#include "Infra/context.h"

#include "Chassis/r1000_arch.h"

#include "Infra/cache_line.h"
#include "Iop/iop.h"
#include "Infra/vend.h"

#define UEV_MEMEX	(1<<(15-0))
//#define UEV_ECC		(1<<(15-1))
//#define UEV_BKPT	(1<<(15-2))
#define UEV_CK_EXIT	(1<<(15-3))
#define UEV_FLD_ERR	(1<<(15-4))
#define UEV_CLASS	(1<<(15-5))
#define UEV_BIN_EQ	(1<<(15-6))
#define UEV_BIN_OP	(1<<(15-7))
#define UEV_TOS_OP	(1<<(15-8))
#define UEV_TOS1_OP	(1<<(15-9))
#define UEV_PAGE_X	(1<<(15-10))
#define UEV_CHK_SYS	(1<<(15-11))
#define UEV_NEW_PAK	(1<<(15-12))
//#define UEV_NEW_STS	(1<<(15-13))
//#define UEV_XFER_CP	(1<<(15-14))

#define MIDPLANE(macro) \
	macro(uint64_t, adr_bus, ~0ULL) \
	macro(uint64_t, fiu_bus, ~0ULL) \
	macro(unsigned, ioc_trace, 0) \
	macro(unsigned, nua_bus, 0x3fff) \
	macro(uint64_t, spc_bus, ~0ULL) \
	macro(uint64_t, typ_bus, ~0ULL) \
	macro(uint64_t, val_bus, ~0ULL) \
	macro(unsigned, seq_prepped, 0) \
	macro(unsigned, seq_halted, 0) \
	macro(unsigned, seq_uev, 0) \
	macro(unsigned, fiu_freeze, 0) \
	macro(unsigned, fiu_unfreeze, 0) \
	macro(unsigned, key_switch, 1) \
	macro(unsigned, csa_this_offs, 0) \
	macro(unsigned, csa_nve, 0) \
	macro(unsigned, csa_hit, 0) \
	macro(unsigned, csa_wr, 0) \
	macro(unsigned, load_top, 0) \
	macro(unsigned, load_bot, 0) \
	macro(unsigned, pop_down, 0) \
	macro(unsigned, load_wdr, 0) \
	macro(unsigned, mem_ctl, 0) \
	macro(unsigned, mem_continue, 0) \
	macro(unsigned, macro_event, 0) \
	macro(unsigned, uevent_enable, 0) \
	macro(unsigned, mem_set, 0) \
	macro(unsigned, mem_hit, 0) \
	macro(unsigned, dummy_next, 0) \
	macro(unsigned, restore_rdr, 0) \
	macro(unsigned, mem_cond, 0) \
	macro(unsigned, mem_cond_pol, 0) \
	macro(unsigned, mem_abort_e, 0) \
	macro(unsigned, mem_abort_el, 0) \
	macro(unsigned, mem_abort_l, 0) \
	macro(unsigned, clock_stop_0, 0) \
	macro(unsigned, clock_stop_3, 0) \
	macro(unsigned, clock_stop_4, 0) \
	macro(unsigned, clock_stop_6, 0) \
	macro(unsigned, clock_stop_7, 0) \
	macro(unsigned, sf_stop, 0) \
	macro(unsigned, freeze, 0) \
	macro(unsigned, clock_stop, 0) \
	macro(unsigned, ram_stop, 0) \
	macro(unsigned, state_clk_stop, 0) \
	macro(unsigned, state_clk_en, 0) \
	macro(unsigned, below_tcp, 0) \
	macro(unsigned, sync_freeze, 0) \
	macro(uint16_t, refresh_count, 0) \
	macro(uint16_t, cur_uadr, 0) \

#define MIDSTATE(macro) \
	macro(unsigned, cond_sel, 0) \
	macro(unsigned, csa_cntl, 0) \
	macro(unsigned, mar_cntl, 0) \
	macro(unsigned, adr_oe, 0) \
	macro(unsigned, fiu_oe, 0) \
	macro(unsigned, tv_oe, 0) \
	macro(unsigned, q_bit, 0) \
	macro(unsigned, csa_write_enable, 0) \
	macro(unsigned, csa_offset, 0) \

#define DMACRO(typ, nam, val) extern typ mp_##nam;
MIDPLANE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) extern typ mp_##nam;
MIDSTATE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) extern typ mp_nxt_##nam;
MIDSTATE(DMACRO)
#undef DMACRO

//#define UADR_MASK 0x3fff
#define UADR_WIDTH 14

#define BUS64_LSB(lsb) (63 - (lsb))


#define DMACRO(typ, nam, val) typ mp_##nam = val;
MIDPLANE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) typ mp_##nam = val;
MIDSTATE(DMACRO)
#undef DMACRO

#define DMACRO(typ, nam, val) typ mp_nxt_##nam = val;
MIDSTATE(DMACRO)
#undef DMACRO

static void
update_state(void)
{

#define DMACRO(typ, nam, val) mp_##nam = mp_nxt_##nam;
MIDSTATE(DMACRO)
#undef DMACRO
}

static void csa_q4(void);

static bool mem_is_hit(unsigned adr, unsigned set);
static void mem_load_mar(void);
static void mem_h1(void);
static void mem_q4(void);

static bool fiu_conditions(void);
static void fiu_do_tivi(void);
static void fiu_rotator(bool sclk);
static uint64_t fiu_frame(void);
static void fiu_q1(void);
static void fiu_q2(void);
static void fiu_q4(void);

static void seq_int_reads(void);
static bool seq_conda(unsigned condsel);
static bool seq_cond9(unsigned condsel);
static bool seq_cond8(unsigned condsel);
static void seq_nxt_lex_valid(void);
static bool seq_condition(void);
static unsigned seq_branch_offset(void);
static void seq_q3clockstop(void);
static void seq_p1(void);
static void seq_h1(void);
static void seq_q1(void);
static void seq_q3(void);
static void seq_q4(void);

static unsigned tv_cadr(unsigned uirc, unsigned frame, unsigned count);
static uint64_t tv_find_ab(unsigned uir, unsigned frame, bool a, bool t, const uint64_t *rfram);

static bool typ_bin_op_pass(void);
static bool typ_priv_path_eq(void);
static bool typ_a_op_pass(void);
static bool typ_b_op_pass(void);
static bool typ_clev(void);
static bool typ_cond(void);
static void typ_h1(void);
static void typ_q2(void);
static void typ_q4(void);

static bool val_ovrsgn(void);
static bool val_cond(void);
static bool val_fiu_cond(void);
static uint64_t val_find_b(unsigned uir);
static void val_h1(void);
static void val_q2(void);
static void val_q4(void);

static void ioc_h1(void);
static void ioc_q2(void);
static void ioc_q4(void);
static void ioc_do_xact(void);
static bool ioc_cond(void);


static uint8_t fiu_pa025[512];
static uint8_t fiu_pa026[512];
static uint8_t fiu_pa027[512];
static uint8_t fiu_pa028[512];
static uint8_t fiu_pa060[512];
static uint8_t seq_pa040[512];
static uint8_t seq_pa042[512];
static uint8_t seq_pa043[512];
static uint8_t seq_pa044[512];
static uint8_t seq_pa045[512];
static uint8_t seq_pa046[512];
static uint8_t seq_pa047[512];
static uint8_t seq_pa048[512];
static uint8_t typ_pa068[512];
static uint8_t typ_pa059[512];
static uint8_t val_pa011[512];
static uint8_t ioc_pb011[32];
static uint8_t tv_pa010[512];

#define F181_ALU(ctrl, a, b, ci, o, co)			\
do {							\
	uint32_t aa = (a), bb = (b);			\
	uint64_t c;					\
	switch ((ctrl) & 0x30) {			\
	case 0x30: c = aa; break;			\
	case 0x20: c = aa | bb; break;			\
	case 0x10: c = aa | (bb^0xffffffff); break;	\
	case 0x00: c = 0xffffffff; break;		\
	default: assert(0);				\
	}						\
	c ^= 0xffffffff;				\
							\
	uint64_t d;					\
	switch((ctrl) & 0xc0) {				\
	case 0xc0: d = 0; break;			\
	case 0x80: d = aa & (bb^0xffffffff); break;	\
	case 0x40: d = aa & bb; break;			\
	case 0x00: d = aa; break;			\
	default: assert(0);				\
	}						\
	d ^= 0xffffffff;				\
							\
	uint64_t y = c + d + (ci);			\
	co = (y >> 32) & 1;				\
							\
	if ((ctrl) & 0x08) {				\
		o = c ^ d;				\
	} else {					\
		o = y;					\
	}						\
	o &= 0xffffffff;				\
} while (0)

#define VAL_V_OE	((1<<0)	      |(1<<2)						  )
#define TYP_T_OE	((1<<0)|(1<<1)				   |(3<<8)		  )
#define FIU_V_OE	(       (1<<1)       |(1<<3)					  )
#define FIU_T_OE	(	       (1<<2)|(1<<3)			 |(3<<10)	  )
#define IOC_TV_OE	(			     (1<<4)				  )
#define SEQ_TV_OE	(				    (1<<5)			  )
#define MEM_V_OE	(					   (3<<8)|(3<<10)	  )
#define MEM_TV_OE	(							  (15<<12))

// -------------------- MEM --------------------

#define CMD_PMW	(1<<0xf)	// PHYSICAL_MEM_WRITE
#define CMD_PMR	(1<<0xe)	// PHYSICAL_MEM_READ
#define CMD_LMW	(1<<0xd)	// LOGICAL_MEM_WRITE
#define CMD_LMR	(1<<0xc)	// LOGICAL_MEM_READ
//#define CMD_C01	(1<<0xb)	// COPY 0 TO 1
//#define CMD_MTT	(1<<0xa)	// MEMORY_TO_TAGSTORE
//#define CMD_C10	(1<<0x9)	// COPY 1 TO 0
//#define CMD_SFF	(1<<0x8)	// SET HIT FLIP FLOPS
#define CMD_PTW	(1<<0x7)	// PHYSICAL TAG WRITE
#define CMD_PTR	(1<<0x6)	// PHYSICAL TAG READ
//#define CMD_INI	(1<<0x5)	// INITIALIZE MRU
#define CMD_LTR	(1<<0x4)	// LOGICAL TAG READ
#define CMD_NMQ	(1<<0x3)	// NAME QUERY
#define CMD_LRQ	(1<<0x2)	// LRU QUERY
#define CMD_AVQ	(1<<0x1)	// AVAILABLE QUERY
#define CMD_IDL	(1<<0x0)	// IDLE
#define CMDS(x) ((r1k->mem_bcmd & (x)) != 0)

#define BSET_0	0x01
#define BSET_1	0x02
#define BSET_2	0x04
#define BSET_3	0x08
#define BSET_4	0x10
#define BSET_5	0x20
#define BSET_6	0x40
#define BSET_7	0x80


// -------------------- SEQ --------------------

#define RND_PUSH		(1<<31) // SEQ MicroArch pdf 32 Push_stack
#define RND_POP			(1<<30)	// SEQ MicroArch pdf 32 Pop_stack
#define RND_CLEAR_ST		(1<<29)	// SEQ MicroArch pdf 32 Clear_stack
#define RND_RESTRT0		(1<<28)
#define RND_RESTRT1		(1<<27)
#define RND_FLD_CHK		(1<<26)
#define RND_TOP_LD		(1<<25) // SEQ MicroArch pdf 32 Load_control_top
#define RND_HALT		(1<<24) // SEQ MicroArch pdf 33 Halt

#define RND_CNTL_MUX		(1<<23)
#define RND_CHK_EXIT		(1<<22)
#define RND_RETRN_LD		(1<<21)
#define RND_M_PC_MUX		(1<<20)
#define RND_M_PC_MD0		(1<<19)
#define RND_M_PC_MD1		(1<<18)
#define RND_M_PC_LDH		(1<<17)
#define RND_ADR_SEL		(1<<16)

#define RND_TOS_VLB		(1<<15) // SEQ MicroArch pdf 33 Validate_tos_optimizer
#define RND_RES_OFFS		(1<<14)
#define RND_RES_NAME		(1<<13)
#define RND_CUR_LEX		(1<<12) // SEQ MicroArch pdf 32 Load_current_lex
#define RND_NAME_LD		(1<<11) // SEQ MicroArch pdf 32 Load_curr_name
#define RND_SAVE_LD		(1<<10) // SEQ MicroArch pdf 32 Load_save_offset
#define RND_PRED_LD		(1<< 9) // SEQ MicroArch pdf 32 Load_control_pred
#define RND_L_ABRT		(1<< 8)

//#define RND_LEX_COMM0		(1<< 7)
//#define RND_LEX_COMM1		(1<< 6)
//#define RND_LEX_COMM2		(1<< 5)
#define RND_CIB_PC_L		(1<< 4)
#define RND_INSTR_MX		(1<< 3)	// SEQ MicroArch pdf 32 Load_current_instr
#define RND_IBUFF_LD		(1<< 2)	// SEQ MicroArch pdf 31 Load_ibuff
#define RND_BR_MSK_L		(1<< 1) // SEQ MicroArch pdf 31 Load_break_mask
#define RND_INSTR_LD		(1<< 0)
#define RNDX(x) ((r1k->seq_rndx & (x)) != 0)


// -------------------- TYP --------------------

#define TYP_A_LSB BUS64_LSB
#define TYP_B_LSB BUS64_LSB
#define TYP_A_BITS(n) (r1k->typ_a >> TYP_A_LSB(n))
#define TYP_B_BITS(n) (r1k->typ_b >> TYP_B_LSB(n))
#define TYP_A_BIT(n) (TYP_A_BITS(n) & 1)
#define TYP_B_BIT(n) (TYP_B_BITS(n) & 1)
#define TYP_A_LIT() (r1k->typ_a & 0x7f)
#define TYP_B_LIT() (r1k->typ_b & 0x7f)


struct r1000_arch_state {

	// -------------------- IOC --------------------

	unsigned pit;

	// -------------------- MEM --------------------

	uint64_t *mem_ram;
	uint64_t *mem_bitt;
	unsigned mem_cl, mem_wd;
	uint64_t mem_tdreg, mem_tqreg;
	uint64_t mem_vdreg, mem_vqreg;

	unsigned mem_word;
	uint64_t mem_qreg;
	unsigned mem_hash;
	uint64_t mem_mar, mem_mar_space;
	bool mem_cstop;
	unsigned mem_hit_lru;
	bool mem_eabort, mem_labort;
	bool mem_p_mcyc2_next;
	unsigned mem_q4cmd;
	unsigned mem_q4cont;
	unsigned mem_hits;
	unsigned mem_hit_set;
	bool mem_cyo, mem_cyt;
	unsigned mem_cmd, mem_bcmd;
	unsigned mem_mar_set;

	// -------------------- FIU --------------------

	unsigned fiu_oreg;
	uint64_t fiu_mdreg;
	uint64_t fiu_treg;
	uint64_t fiu_vreg;
	uint64_t fiu_refresh_reg;
	uint64_t fiu_marh;
	uint64_t fiu_ti_bus, fiu_vi_bus;
	unsigned fiu_lfreg;

	uint32_t fiu_srn, fiu_sro, fiu_ctopn, fiu_ctopo;
	unsigned fiu_nve, fiu_pdreg;
	unsigned fiu_moff;
	bool fiu_pdt;

	bool fiu_state0, fiu_state1, fiu_labort, fiu_e_abort_dly;
	uint8_t fiu_pcntl_d;
	uint8_t fiu_lcntl;
	uint8_t fiu_mcntl;
	bool fiu_scav_trap;
	bool fiu_cache_miss;
	bool fiu_csa_oor;
	bool fiu_page_xing;
	bool fiu_init_mru_d;
	bool fiu_drive_mru;
	bool fiu_memcnd;
	bool fiu_cndtru;
	bool fiu_incmplt_mcyc;
	bool fiu_mar_modified;
	bool fiu_write_last;
	bool fiu_phys_ref;
	bool fiu_phys_last;
	bool fiu_log_query;
	bool fiu_mctl_is_read;
	bool fiu_logrw;
	bool fiu_logrw_d;
	bool fiu_omf20;
	bool fiu_nmatch;
	bool fiu_in_range;
	unsigned fiu_setq;
	unsigned fiu_omq;
	unsigned fiu_prmt;
	bool fiu_dumon;
	bool fiu_memex;
	bool fiu_logrwn;
	bool fiu_page_crossing_next;
	bool fiu_miss;
	bool fiu_csaht;
	bool fiu_csa_oor_next;

	unsigned fiu_tcsa_sr;
	unsigned fiu_tcsa_inval_csa;
	unsigned fiu_tcsa_tf_pred;

	uint64_t *fiu_wcsram;
	uint64_t *fiu_typwcsram;
	uint64_t fiu_uir;
	uint64_t fiu_typuir;

	unsigned fiu_hit_offset;
	bool fiu_tmp_csa_oor_next;
	bool fiu_scav_trap_next;
	bool fiu_memcyc1;
	bool fiu_uev10_page_x;
	bool fiu_uev0_memex;
	unsigned fiu_mem_start;
	bool fiu_memstart;
	unsigned fiu_pa025d, fiu_pa026d, fiu_pa027d;

	#define UIR_FIU_OL	((r1k->fiu_uir >> 40) & 0x7f)
	#define UIR_FIU_LFL	((r1k->fiu_uir >> 32) & 0x7f)
	#define UIR_FIU_LFRC	((r1k->fiu_uir >> 30) & 0x3)
	#define UIR_FIU_OP	((r1k->fiu_uir >> 28) & 0x3)
	#define UIR_FIU_SEL	((r1k->fiu_uir >> 26) & 0x3)
	#define UIR_FIU_FSRC	((r1k->fiu_uir >> 25) & 1)
	#define UIR_FIU_ORSR	((r1k->fiu_uir >> 24) & 1)
	#define UIR_FIU_TIVI	((r1k->fiu_uir >> 20) & 0xf)
	#define UIR_FIU_OCLK	((r1k->fiu_uir >> 19) & 1)
	#define UIR_FIU_VCLK	((r1k->fiu_uir >> 18) & 1)
	#define UIR_FIU_TCLK	((r1k->fiu_uir >> 17) & 1)
	#define UIR_FIU_LDMDR	((r1k->fiu_uir >> 16) & 1)
	#define UIR_FIU_MSTRT	((r1k->fiu_uir >> 10) & 0x1f)
	#define UIR_FIU_RDSRC	((r1k->fiu_uir >> 9) & 1)
	#define UIR_FIU_LSRC	((r1k->fiu_uir >> 1) & 1)
	#define UIR_FIU_OSRC	((r1k->fiu_uir >> 0) & 1)

	// -------------------- SEQ --------------------

	uint32_t *seq_top;
	uint32_t *seq_bot;
	uint32_t seq_cbot, seq_ctop;
	unsigned seq_emac;
	unsigned seq_curins;
	bool seq_topbot;

	uint64_t seq_macro_ins_typ, seq_macro_ins_val;
	unsigned seq_macro_pc_offset;
	unsigned seq_curr_lex;
	unsigned seq_retrn_pc_ofs;
	unsigned seq_break_mask;

	uint64_t seq_tost, seq_vost, seq_cur_name;
	uint64_t seq_namram[1<<4];
	uint64_t seq_pcseg, seq_retseg;

	uint64_t seq_tosram[1<<4];
	uint64_t seq_tosof;
	uint32_t seq_savrg;
	uint32_t seq_pred;
	uint32_t seq_topcnt;

	uint16_t seq_ram[16];
	uint16_t seq_topu;
	uint16_t seq_adr;
	unsigned seq_fiu;
	unsigned seq_other;
	unsigned seq_late_u;
	unsigned seq_uev;

	uint8_t seq_bhreg;
	unsigned seq_rreg;
	unsigned seq_lreg;
	unsigned seq_treg;
	bool seq_hint_last;
	bool seq_hint_t_last;
	bool seq_last_late_cond;
	bool seq_preturn, seq_push_br, seq_push;
	uint64_t seq_typ_bus;
	uint64_t seq_val_bus;
	uint64_t seq_output_ob;
	uint64_t seq_name_bus;
	uint64_t seq_code_offset;
	unsigned seq_uadr_decode;
	unsigned seq_display;
	unsigned seq_decram;
	uint64_t seq_resolve_offset;
	bool seq_cload;
	bool seq_ibuf_fill;
	bool seq_uses_tos;
	bool seq_l_macro_hic;
	unsigned seq_n_in_csa;
	unsigned seq_decode;
	unsigned seq_wanna_dispatch;
	unsigned seq_branch_offset;
	bool seq_ibld;
	bool seq_field_number_error;
	bool seq_m_break_class;
	bool seq_latched_cond;
	bool seq_saved_latched;
	bool seq_stack_size_zero;
	unsigned seq_rq;
	bool seq_m_tos_invld;
	bool seq_tos_vld_cond;
	bool seq_foo7;
	bool seq_check_exit_ue;
	bool seq_carry_out;
	bool seq_bad_hint;
	bool seq_m_res_ref;
	bool seq_bad_hint_enable;
	bool seq_ferr;
	bool seq_late_macro_event;
	bool seq_s_state_stop;
	bool seq_clock_stop_1;
	bool seq_clock_stop_5;
	unsigned seq_diag;
	unsigned seq_countdown;

	uint16_t seq_lex_valid;
	bool seq_lxval;
	unsigned seq_resolve_address;
	bool seq_m_ibuff_mt;
	bool seq_foo9;
	bool seq_q3cond;
	bool seq_stop;
	uint64_t *seq_wcsram;
	uint64_t seq_uir;

	unsigned seq_urand;
	unsigned seq_rndx;
	unsigned seq_br_typ;
	unsigned seq_br_typb;
	unsigned seq_br_tim;
	bool seq_macro_event;
	unsigned seq_late_macro_pending;
	bool seq_early_macro_pending;
	bool seq_maybe_dispatch;
	unsigned seq_intreads;
	bool seq_tmp_carry_out;
	unsigned seq_mem_start;

	#define BRANCH_FALSE	(1<<0x0)
	#define BRANCH_TRUE	(1<<0x1)
	#define PUSH		(1<<0x2)
	#define BRANCH		(1<<0x3)
	#define CALL_FALSE	(1<<0x4)
	#define CALL_TRUE	(1<<0x5)
	#define CONTINUE	(1<<0x6)
	#define CALL		(1<<0x7)
	#define RETURN_TRUE	(1<<0x8)
	#define RETURN_FALSE	(1<<0x9)
	#define RETURN		(1<<0xa)
	#define CASE_FALSE	(1<<0xb)
	#define DISPATCH_TRUE	(1<<0xc)
	#define DISPATCH_FALSE	(1<<0xd)
	#define DISPATCH	(1<<0xe)
	#define CASE_CALL	(1<<0xf)
	#define A_BRANCH (BRANCH_FALSE|BRANCH_TRUE|BRANCH)
	#define A_CALL (CALL_FALSE|CALL_TRUE|CALL)
	#define A_RETURN (RETURN_TRUE|RETURN_FALSE|RETURN)
	#define A_DISPATCH (DISPATCH_TRUE|DISPATCH_FALSE|DISPATCH)
	#define BRTYPE(x) (r1k->seq_br_typb & (x))

	#define UIR_SEQ_BRN	((r1k->seq_uir >> (41-13)) & 0x3fff)
	#define UIR_SEQ_LUIR	((r1k->seq_uir >> (41-15)) & 0x1)
	#define UIR_SEQ_BRTYP	((r1k->seq_uir >> (41-19)) & 0xf)
	#define UIR_SEQ_BRTIM	((r1k->seq_uir >> (41-21)) & 0x3)
	#define UIR_SEQ_CSEL	((r1k->seq_uir >> (41-28)) & 0x7f)
	#define UIR_SEQ_LAUIR	((r1k->seq_uir >> (41-30)) & 0x3)
	#define UIR_SEQ_ENMIC	((r1k->seq_uir >> (41-31)) & 0x1)
	#define UIR_SEQ_IRD	((r1k->seq_uir >> (41-34)) & 0x7)
	#define UIR_SEQ_URAND	((r1k->seq_uir >> (41-41)) & 0x7f)

	// -------------------- TYP --------------------

	uint64_t *typ_rfram;
	uint64_t typ_a, typ_b, typ_nalu, typ_alu;
	uint64_t typ_wdr;
	unsigned typ_count;
	bool typ_cond;
	bool typ_almsb;
	bool typ_coh;
	bool typ_com;
	uint32_t typ_ofreg;
	bool typ_pass_priv;
	bool typ_last_cond;
	bool typ_is_binary;
	bool typ_sub_else_add;
	bool typ_ovr_en;
	uint64_t *typ_wcsram;
	uint64_t typ_uir;
	unsigned typ_rand;

	#define UIR_TYP_A	((r1k->typ_uir >> 41) & 0x3f)
	#define UIR_TYP_B	((r1k->typ_uir >> 35) & 0x3f)
	#define UIR_TYP_FRM	((r1k->typ_uir >> 30) & 0x1f)
	#define UIR_TYP_RAND	((r1k->typ_uir >> 24) & 0xf)
	#define UIR_TYP_C	((r1k->typ_uir >> 18) & 0x3f)
	#define UIR_TYP_CLIT	(((r1k->typ_uir >> (46-16)) & 0x1f) | (((r1k->typ_uir >> (46-18) & 0x3)<<5)))
	#define UIR_TYP_UPVC	((r1k->typ_uir >> 15) & 0x7)
	#define UIR_TYP_SEL	((r1k->typ_uir >> 14) & 0x1)
	#define UIR_TYP_AFNC	((r1k->typ_uir >> 9) & 0x1f)
	#define UIR_TYP_CSRC	((r1k->typ_uir >> 8) & 0x1)
	#define UIR_TYP_MCTL	((r1k->typ_uir >> 4) & 0xf)
	#define UIR_TYP_CCTL	((r1k->typ_uir >> 1) & 0x7)

	// -------------------- VAL --------------------

	uint64_t *val_rfram;
	uint64_t val_a, val_b;
	uint64_t val_wdr;
	uint64_t val_zerocnt;
	uint64_t val_malat, val_mblat, val_mprod;
	uint64_t val_nalu, val_alu;
	unsigned val_count;
	bool val_amsb, val_bmsb, val_cmsb, val_mbit, val_last_cond;
	bool val_isbin, val_sub_else_add, val_ovren, val_carry_middle;
	bool val_coh;
	uint64_t *val_wcsram;
	uint64_t val_uir;
	unsigned val_rand;
	bool val_thiscond;

	#define UIR_VAL_A	((r1k->val_uir >> (39-5)) & 0x3f)
	#define UIR_VAL_B	((r1k->val_uir >> (39-11)) & 0x3f)
	#define UIR_VAL_FRM	((r1k->val_uir >> (39-16)) & 0x1f)
	#define UIR_VAL_SEL	((r1k->val_uir >> (39-18)) & 0x3)
	#define UIR_VAL_RAND	((r1k->val_uir >> (39-22)) & 0xf)
	#define UIR_VAL_C	((r1k->val_uir >> (39-28)) & 0x3f)
	#define UIR_VAL_MSRC	((r1k->val_uir >> (39-32)) & 0xf)
	#define UIR_VAL_AFNC	((r1k->val_uir >> (39-37)) & 0x1f)
	#define UIR_VAL_CSRC	((r1k->val_uir >> (39-38)) & 0x1)

	// -------------------- IOC --------------------

	uint64_t ioc_dummy_typ, ioc_dummy_val;

	unsigned ioc_iack;
	struct ioc_sc_bus_xact *ioc_xact;
	unsigned ioc_fffff400;
	bool ioc_request_int_en;
	bool ioc_response_int_en;
	unsigned ioc_reqfifo[1024], ioc_reqwrp, ioc_reqrdp, ioc_reqreg;
	unsigned ioc_rspfifo[1024], ioc_rspwrp, ioc_rsprdp;
	bool ioc_cpu_running;
	uint8_t *ioc_ram;
	unsigned ioc_acnt;
	unsigned ioc_areg;
	unsigned ioc_rdata;
	unsigned ioc_rtc;

	unsigned ioc_prescaler;
	uint16_t ioc_delay, ioc_slice;
	bool ioc_slice_ev, ioc_delay_ev;
	bool ioc_sen, ioc_den, ioc_ten;
	bool ioc_dumen;
	bool ioc_csa_hit;
	uint16_t *ioc_tram;
	uint64_t *ioc_wcsram;
	uint64_t ioc_uir;
	bool ioc_is_tracing;

	#define UIR_IOC_ULWDR	((r1k->ioc_uir >> 13) & 0x1)
	#define UIR_IOC_RAND	((r1k->ioc_uir >>  8) & 0x1f)
	#define UIR_IOC_AEN	((r1k->ioc_uir >>  6) & 0x3)
	#define UIR_IOC_FEN	((r1k->ioc_uir >>  4) & 0x3)
	#define UIR_IOC_TVBS	((r1k->ioc_uir >>  0) & 0xf)

	// -------------------- CSA --------------------

	unsigned csa_topreg;
	unsigned csa_botreg;
};

static struct r1000_arch_state *r1k;

void
r1000_arch_new(void)
{
	struct r1000_arch_state *state;

	state = (struct r1000_arch_state *)CTX_GetRaw("R1000", sizeof *state);
	r1k = state;

	// -------------------- MEM --------------------

	r1k->mem_bcmd = 1U << r1k->mem_cmd;
	r1k->mem_bitt = (uint64_t*)CTX_GetRaw("MEM.bitt", sizeof(*r1k->mem_bitt) << 22);
			// 12 bit line, 3 bit set, 6 bit word, 1 bit T/V
	r1k->mem_ram = (uint64_t*)CTX_GetRaw("MEM.ram", sizeof(*r1k->mem_ram) << 15);
			// 12 bit line, 3 bit set

	// -------------------- FIU --------------------

	Firmware_Copy(fiu_pa025, sizeof fiu_pa025, "PA025-03");
	Firmware_Copy(fiu_pa026, sizeof fiu_pa026, "PA026-02");
	Firmware_Copy(fiu_pa027, sizeof fiu_pa027, "PA027-01");
	Firmware_Copy(fiu_pa028, sizeof fiu_pa028, "PA028-02");
	Firmware_Copy(fiu_pa060, sizeof fiu_pa060, "PA060-01");
	r1k->fiu_wcsram = (uint64_t*)CTX_GetRaw("FIU_WCS", sizeof(uint64_t) << 14);
	r1k->fiu_typwcsram = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);

	// -------------------- SEQ --------------------

	Firmware_Copy(seq_pa040, sizeof seq_pa040, "PA040-02");
	Firmware_Copy(seq_pa042, sizeof seq_pa042, "PA042-02");
	Firmware_Copy(seq_pa043, sizeof seq_pa043, "PA043-02");
	Firmware_Copy(seq_pa044, sizeof seq_pa044, "PA044-01");
	Firmware_Copy(seq_pa045, sizeof seq_pa045, "PA045-03");
	Firmware_Copy(seq_pa046, sizeof seq_pa046, "PA046-02");
	Firmware_Copy(seq_pa047, sizeof seq_pa047, "PA047-02");
	Firmware_Copy(seq_pa048, sizeof seq_pa048, "PA048-02");
	r1k->seq_wcsram = (uint64_t*)CTX_GetRaw("SEQ_WCS", sizeof(uint64_t) << UADR_WIDTH);
	r1k->seq_top = (uint32_t*)CTX_GetRaw("SEQ_TOP", sizeof(uint32_t) << 10);
	r1k->seq_bot = (uint32_t*)CTX_GetRaw("SEQ_BOT", sizeof(uint32_t) << 10);

	// -------------------- TYP --------------------

	Firmware_Copy(tv_pa010, sizeof tv_pa010, "PA010-02");
	Firmware_Copy(typ_pa068, sizeof typ_pa068, "PA068-01");
	Firmware_Copy(typ_pa059, sizeof typ_pa059, "PA059-01");
	r1k->typ_wcsram = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);
	r1k->typ_rfram = (uint64_t*)CTX_GetRaw("TYP_RF", sizeof(uint64_t) << 10);

	// -------------------- VAL --------------------

	Firmware_Copy(val_pa011, sizeof val_pa011, "PA011-02");
	r1k->val_wcsram = (uint64_t*)CTX_GetRaw("VAL_WCS", sizeof(uint64_t) << 14);
	r1k->val_rfram = (uint64_t*)CTX_GetRaw("VAL_RF", sizeof(uint64_t) << 10);

	// -------------------- IOC --------------------

	Firmware_Copy(ioc_pb011, sizeof ioc_pb011, "PB011-01");
	r1k->ioc_wcsram = (uint64_t*)CTX_GetRaw("IOC_WCS", sizeof(uint64_t) << 14);
	r1k->ioc_tram = (uint16_t*)CTX_GetRaw("IOC_TRAM", sizeof(uint16_t) * 2049);

	r1k->ioc_ram = (uint8_t *)CTX_GetRaw("IOP.ram_space", 512<<10);
	r1k->ioc_is_tracing = false;
}

// ----------- One Micro Cycle -----------------

void
r1000_arch_micro_cycle(void)
{
	mem_q4();
	fiu_q4();
	typ_q4();
	val_q4();
	csa_q4();
	ioc_q4();
	seq_q4();

	if (++r1k->pit == 256) {
		pit_clock();
		r1k->pit = 0;
	}
	update_state();

	mem_h1();
	typ_h1();
	val_h1();
	ioc_h1();
	seq_h1();

	fiu_q1();
	seq_q1();

	fiu_q2();
	typ_q2();
	val_q2();
	ioc_q2();

	seq_q3();
}

// -------------------- MEM --------------------

static bool
mem_is_hit(unsigned adr, unsigned set)
{
	(void)set;
	uint64_t data = r1k->mem_ram[adr];
	if (CMDS(CMD_LMR|CMD_LMW|CMD_LTR) && ((r1k->mem_mar ^ data) & ~0x1fffULL)) {
		return (false);
	}

	unsigned page_state = (r1k->mem_ram[adr]>>6) & 3;

	// R1000_Micro_Arch_Mem.pdf p19:
	//    00: Loading, 01: Read-only, 10: Read-Write, 11: Invalid

	bool ts = (data & 0x7) == r1k->mem_mar_space;

	if (CMDS(CMD_LMR))
		return (ts && (page_state == 1 || page_state == 2));

	if (CMDS(CMD_LMW))
		return (ts && page_state == 1);

	if (CMDS(CMD_LRQ))
		return ((r1k->mem_ram[adr] & 0xf00) == 0);

	if (CMDS(CMD_AVQ))
		return (page_state == 0);

	if (CMDS(CMD_LTR))
		return (ts && page_state != 0);

	bool name = !((r1k->mem_mar ^ data) >> 32);
	if (CMDS(CMD_NMQ))
		return (name && (page_state != 0));

	if (CMDS(CMD_IDL))
		return (true);

	assert(0);
}

static void
mem_load_mar(void)
{
	uint64_t a;
	uint32_t s;

	s = mp_spc_bus;
	a = mp_adr_bus;
	r1k->mem_mar = a;
	r1k->mem_mar_space = s;
	r1k->mem_mar_set = (a>>BUS64_LSB(27)) & 0xf;

	r1k->mem_word = (a >> 7) & 0x3f;
	r1k->mem_hash = 0;
	r1k->mem_hash ^= cache_line_tbl_h[(a >> 42) & 0x3ff];
	r1k->mem_hash ^= cache_line_tbl_l[(a >> 13) & 0xfff];
	r1k->mem_hash ^= cache_line_tbl_s[r1k->mem_mar_space & 0x7];
}

static void
mem_h1(void)
{
	bool labort = !(mp_mem_abort_l && mp_mem_abort_el);
	bool p_early_abort = r1k->mem_eabort;
	bool p_mcyc2_next_hd = r1k->mem_p_mcyc2_next;
	if (p_early_abort && p_mcyc2_next_hd) {
		r1k->mem_cmd = 0;
	} else {
		r1k->mem_cmd = r1k->mem_q4cmd ^ 0xf;
	}
	r1k->mem_bcmd = 1U << r1k->mem_cmd;
	r1k->mem_p_mcyc2_next =
		!(
			((r1k->mem_q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd) ||
			((!r1k->mem_q4cont) && (!p_early_abort) && (!p_mcyc2_next_hd))
		);
	r1k->mem_cyo = !((r1k->mem_q4cmd != 0xf) && (!p_early_abort) && p_mcyc2_next_hd);
	r1k->mem_cyt = p_mcyc2_next_hd;

	if (r1k->mem_cyo && !mp_freeze && !CMDS(CMD_IDL)) {
		if (CMDS(CMD_AVQ)) {
			if	  (r1k->mem_hits & BSET_4) { mp_mem_set = 0;
			} else if (r1k->mem_hits & BSET_5) { mp_mem_set = 1;
			} else if (r1k->mem_hits & BSET_6) { mp_mem_set = 2;
			} else if (r1k->mem_hits & BSET_7) { mp_mem_set = 3;
			} else if (r1k->mem_hits & BSET_0) { mp_mem_set = 0;
			} else if (r1k->mem_hits & BSET_1) { mp_mem_set = 1;
			} else if (r1k->mem_hits & BSET_2) { mp_mem_set = 2;
			} else				     { mp_mem_set = 3;
			}
		} else if (r1k->mem_hits != 0xff && mp_mem_set != (r1k->mem_hit_set & 3)) {
			mp_mem_set = r1k->mem_hit_set & 3;
		}

		mp_mem_hit = 0xf;
		if (r1k->mem_hits & (BSET_0|BSET_1|BSET_2|BSET_3))
			mp_mem_hit &= ~1;
		if (r1k->mem_hits & (BSET_4|BSET_5|BSET_6|BSET_7))
			mp_mem_hit &= ~8;
		if (r1k->mem_hits) {
			unsigned tadr = r1k->mem_hash << 3;
			if      (r1k->mem_hits & BSET_0)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 0] & 0xf00;
			else if (r1k->mem_hits & BSET_1)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 1] & 0xf00;
			else if (r1k->mem_hits & BSET_2)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 2] & 0xf00;
			else if (r1k->mem_hits & BSET_3)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 3] & 0xf00;
			else if (r1k->mem_hits & BSET_4)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 4] & 0xf00;
			else if (r1k->mem_hits & BSET_5)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 5] & 0xf00;
			else if (r1k->mem_hits & BSET_6)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 6] & 0xf00;
			else if (r1k->mem_hits & BSET_7)	r1k->mem_hit_lru = r1k->mem_ram[tadr | 7] & 0xf00;
		} else {
			r1k->mem_hit_lru = 0xf00;
		}
	}
	if (!r1k->mem_cyt && !mp_freeze && !CMDS(CMD_IDL)) {
		if (CMDS(CMD_PTR)) {
			unsigned padr = (r1k->mem_hash << 3) | (r1k->mem_mar_set & 0x7);
			r1k->mem_qreg = r1k->mem_ram[padr];
		}

		if (CMDS(CMD_LMR|CMD_PMR) && !labort) {
			uint32_t radr =	(r1k->mem_hit_set << 18) | (r1k->mem_cl << 6) | r1k->mem_wd;
			assert(radr < (1U << 21));
			r1k->mem_tqreg = r1k->mem_bitt[radr+radr];
			r1k->mem_vqreg = r1k->mem_bitt[radr+radr+1];
		}

		bool ihit = mp_mem_hit == 0xf;
		if (CMDS(CMD_LMW|CMD_PMW) && !ihit && !r1k->mem_labort) {
			uint32_t radr = (r1k->mem_hit_set << 18) | (r1k->mem_cl << 6) | r1k->mem_wd;
			assert(radr < (1U << 21));
			r1k->mem_bitt[radr+radr] = r1k->mem_tdreg;
			r1k->mem_bitt[radr+radr+1] = r1k->mem_vdreg;
		}

		if (CMDS(CMD_PTW)) {
			bool my_board = false;
			bool which_board = r1k->mem_mar_set >> 3;
			if (which_board == my_board) {
				unsigned padr = (r1k->mem_hash << 3) | (r1k->mem_mar_set & 0x7);
				r1k->mem_ram[padr] = r1k->mem_vdreg;
			}
		} else if (!r1k->mem_labort && CMDS(CMD_LRQ|CMD_LMW|CMD_LMR)) {
			unsigned padr = r1k->mem_hash << 3;
			for (unsigned u = 0; u < 8; u++) {
				unsigned then = r1k->mem_ram[padr] & 0xf00;
				if (then == r1k->mem_hit_lru) {
					r1k->mem_ram[padr] |= 0x700;
					if (CMDS(CMD_LMW))
						r1k->mem_ram[padr] |= 0x1000;
				} else if (then > r1k->mem_hit_lru) {
					r1k->mem_ram[padr] -= 0x100;
				}
				padr += 1;
			}
		}
	}

	bool not_me = mp_mem_hit == 0xf;

	if (mp_tv_oe & MEM_V_OE) {
		if (not_me) {
			mp_val_bus = ~0ULL;
		} else {
			mp_val_bus = r1k->mem_qreg;
		}
	} else if (mp_tv_oe & MEM_TV_OE) {
		if (not_me) {
			mp_typ_bus = ~0ULL;
			mp_val_bus = ~0ULL;
		} else {
			mp_typ_bus = r1k->mem_tqreg;
			mp_val_bus = r1k->mem_vqreg;
		}
	}
}

static void
mem_q4(void)
{
	r1k->mem_cl = r1k->mem_hash;
	r1k->mem_wd = r1k->mem_word;

	r1k->mem_cstop = mp_sync_freeze == 0;

	if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
		r1k->mem_tdreg = mp_typ_bus;
		r1k->mem_vdreg = mp_val_bus;
	}
	bool loadmar = !((mp_mar_cntl >= 4) && mp_clock_stop_7);
	if (!loadmar && r1k->mem_cstop) {
		mem_load_mar();
	}

	if (!r1k->mem_cyo) {
		r1k->mem_hit_set = 0x03;
		r1k->mem_hits = 0;
		if (r1k->mem_labort) {
			// nothing
		} else if (CMDS(CMD_LMR|CMD_LMW|CMD_LTR)) {
			// These create at most a single hit
			unsigned badr = r1k->mem_hash << 3;
			do {
				if (mem_is_hit(badr | 4, 4)) {
					r1k->mem_hits |= BSET_4;
					r1k->mem_hit_set = 4;
					break;
				}
				if (mem_is_hit(badr | 5, 5)) {
					r1k->mem_hits |= BSET_5;
					r1k->mem_hit_set = 5;
					break;
				}
				if (mem_is_hit(badr | 6, 6)) {
					r1k->mem_hits |= BSET_6;
					r1k->mem_hit_set = 6;
					break;
				}
				if (mem_is_hit(badr | 7, 7)) {
					r1k->mem_hits |= BSET_7;
					r1k->mem_hit_set = 7;
					break;
				}
				if (mem_is_hit(badr | 0, 0)) {
					r1k->mem_hits |= BSET_0;
					r1k->mem_hit_set = 0;
					break;
				}
				if (mem_is_hit(badr | 1, 1)) {
					r1k->mem_hits |= BSET_1;
					r1k->mem_hit_set = 1;
					break;
				}
				if (mem_is_hit(badr | 2, 2)) {
					r1k->mem_hits |= BSET_2;
					r1k->mem_hit_set = 2;
					break;
				}
				if (mem_is_hit(badr | 3, 3)) {
					r1k->mem_hits |= BSET_3;
					r1k->mem_hit_set = 3;
					break;
				}
			} while (0);
		} else if (CMDS(CMD_PMR|CMD_PMW|CMD_PTW|CMD_PTR)) {
			if (r1k->mem_mar_set < 8) {
				r1k->mem_hits = 1U << r1k->mem_mar_set;
				r1k->mem_hit_set = r1k->mem_mar_set;
			}
		} else {
			unsigned badr = r1k->mem_hash << 3;
			if (mem_is_hit(badr | 0, 0)) { r1k->mem_hits |= BSET_0; r1k->mem_hit_set = 0; }
			if (mem_is_hit(badr | 1, 1)) { r1k->mem_hits |= BSET_1; r1k->mem_hit_set = 1; }
			if (mem_is_hit(badr | 2, 2)) { r1k->mem_hits |= BSET_2; r1k->mem_hit_set = 2; }
			if (mem_is_hit(badr | 3, 3)) { r1k->mem_hits |= BSET_3; r1k->mem_hit_set = 3; }
			if (mem_is_hit(badr | 4, 4)) { r1k->mem_hits |= BSET_4; r1k->mem_hit_set = 4; }
			if (mem_is_hit(badr | 5, 5)) { r1k->mem_hits |= BSET_5; r1k->mem_hit_set = 5; }
			if (mem_is_hit(badr | 6, 6)) { r1k->mem_hits |= BSET_6; r1k->mem_hit_set = 6; }
			if (mem_is_hit(badr | 7, 7)) { r1k->mem_hits |= BSET_7; r1k->mem_hit_set = 7; }
		}
	}
	r1k->mem_q4cmd = mp_mem_ctl;
	r1k->mem_q4cont = mp_mem_continue;
	r1k->mem_labort = !(mp_mem_abort_l && mp_mem_abort_el);
	r1k->mem_eabort = !(mp_mem_abort_e && mp_mem_abort_el);
}

// -------------------- FIU --------------------

static bool
fiu_conditions(void)
{

	switch(mp_cond_sel) {
	case 0x60: return(!r1k->fiu_memex);
	case 0x61: return(!r1k->fiu_phys_last);
	case 0x62: return(!r1k->fiu_write_last);
	case 0x63: return(!mp_csa_hit);
	case 0x64: return(!((r1k->fiu_oreg >> 6) & 1));
	case 0x65: // Cross word shift
		return((r1k->fiu_oreg + (r1k->fiu_lfreg & 0x3f) + (r1k->fiu_lfreg & 0x80)) <= 255);
	case 0x66: return((r1k->fiu_moff & 0x3f) > 0x30);
	case 0x67: return(!(mp_refresh_count != 0xffff));
	case 0x68: return(!r1k->fiu_csa_oor_next);
	case 0x69: return(!false);			// SCAV_HIT
	case 0x6a: return(!r1k->fiu_page_xing);
	case 0x6b: return(!r1k->fiu_miss);
	case 0x6c: return(!r1k->fiu_incmplt_mcyc);
	case 0x6d: return(!r1k->fiu_mar_modified);
	case 0x6e: return(!r1k->fiu_incmplt_mcyc);
	case 0x6f: return((r1k->fiu_moff & 0x3f) != 0);
	default: assert(0);
	}
}

static uint64_t
fiu_frame(void)
{
	uint64_t u = 0;

	uint64_t line = 0;
	line ^= cache_line_tbl_h[(r1k->fiu_srn >> 10) & 0x3ff];
	line ^= cache_line_tbl_l[(r1k->fiu_moff >> (13 - 7)) & 0xfff];
	line ^= cache_line_tbl_s[(r1k->fiu_sro >> 4) & 0x7];

	u |= (uint64_t)mp_mem_cond_pol << BUS64_LSB(9);
	u |= (uint64_t)mp_mem_cond << BUS64_LSB(10);
	u |= line << BUS64_LSB(23);
	u |= (uint64_t)r1k->fiu_setq << BUS64_LSB(25);
	u |= (uint64_t)mp_mem_set << BUS64_LSB(27);
	u |= (uint64_t)((r1k->fiu_omq >> 2) & 0x3) << BUS64_LSB(29);
	u |= 0x3ULL << BUS64_LSB(31);
	u |= (uint64_t)(r1k->fiu_uev10_page_x) << BUS64_LSB(32);
	u |= (uint64_t)((r1k->fiu_prmt >> 1) & 1) << BUS64_LSB(33);
	u |= (uint64_t)(mp_refresh_count != 0xffff) << BUS64_LSB(34);
	u |= (uint64_t)(r1k->fiu_uev0_memex) << BUS64_LSB(35);
	u |= ((line >> 0) & 1) << BUS64_LSB(48);
	u |= ((line >> 1) & 1) << BUS64_LSB(50);
	u |= (uint64_t)r1k->fiu_nmatch << BUS64_LSB(56);
	u |= (uint64_t)r1k->fiu_in_range << BUS64_LSB(57);
	u |= (uint64_t)r1k->fiu_csa_oor_next << BUS64_LSB(58);
	u |= (uint64_t)mp_csa_hit << BUS64_LSB(59);
	u |= (uint64_t)r1k->fiu_hit_offset;
	return (u);
}

static void
fiu_do_tivi(void)
{

	unsigned tivi = UIR_FIU_TIVI;

	uint64_t vi;
	switch (tivi) {
	case 0x00: case 0x04: case 0x08:
		vi = r1k->fiu_vreg;
		break;
	case 0x01: case 0x05: case 0x09:
		vi = ~mp_val_bus;
		break;
	case 0x02: case 0x06: case 0x0a:
		vi = ~mp_fiu_bus;
		break;
	case 0x03: case 0x07: case 0x0b:
		vi = fiu_frame() ^ ~0ULL;
		break;
	default:
		vi = (uint64_t)r1k->fiu_srn << 32;
		vi |= r1k->fiu_sro & 0xffffff80;
		vi |= r1k->fiu_oreg;
		vi = ~vi;
		break;
	}
	uint64_t ti;
	switch (tivi) {
	case 0x00: case 0x01: case 0x02: case 0x03:
		ti = r1k->fiu_treg;
		break;
	case 0x04: case 0x05: case 0x06: case 0x07:
		ti = ~mp_fiu_bus;
		break;
	case 0x08: case 0x09: case 0x0a: case 0x0b:
		ti = ~mp_typ_bus;
		break;
	default:
		{
		uint64_t tmp;
		tmp = (r1k->fiu_sro >> 4) & 0x7;
		r1k->fiu_marh &= ~0x07;
		r1k->fiu_marh |= tmp;
		r1k->fiu_marh &= ~(0x1efULL << 23ULL);
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_incmplt_mcyc) << 23;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_mar_modified) << 24;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_write_last) << 25;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_phys_last) << 26;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_cache_miss) << 28;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_page_xing) << 29;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_csa_oor) << 30;
		r1k->fiu_marh |= (uint64_t)(!r1k->fiu_scav_trap) << 31;
		ti = ~r1k->fiu_marh;
		}
		break;
	}
	r1k->fiu_ti_bus = ti;
	r1k->fiu_vi_bus = vi;
}

static void
fiu_rotator(bool sclk)
{
	uint64_t vmsk = 0, tmsk = 0;
	bool sgnbit = 0;
	uint64_t ft, tir, vir;
	unsigned s, fs, sgn;
	bool zero_length;

	unsigned lfl = UIR_FIU_LFL;

	bool fill_mode = false;
	if (UIR_FIU_FSRC) {				// UCODE
		fill_mode = lfl >> 6;
	} else {
		fill_mode = (r1k->fiu_lfreg >> 6) & 1;
	}

	unsigned lenone;
	if (UIR_FIU_LSRC) {				// UCODE
		lenone = lfl & 0x3f;
	} else {
		lenone = r1k->fiu_lfreg & 0x3f;
	}

	zero_length = !(fill_mode & (lenone == 0x3f));

	unsigned offset;
	if (UIR_FIU_OSRC) {				// UCODE
		offset = UIR_FIU_OL;
	} else {
		offset = r1k->fiu_oreg;
	}


	unsigned op, sbit, ebit;
	op = UIR_FIU_OP;				// UCODE
	switch (op) {
	case 0:
		sbit = (lenone ^ 0x3f) | (1<<6);
		ebit = 0x7f;
		break;
	case 1:
		sbit = 0;
		ebit = (lenone & 0x3f) + (offset & 0x7f);
		break;
	case 2:
		sbit = offset;
		ebit = 0x7f;
		break;
	case 3:
		sbit = offset;
		ebit = (lenone & 0x3f) + (offset & 0x7f);
		break;
	default:
		assert(0);
	}
	sbit &= 0x7f;
	ebit &= 0x7f;

	uint64_t msk6;
	if (op != 0) {
		msk6 = ~0ULL;
		if (((offset + lenone) & 3) != 3) {
			msk6 >>= 4;
		}
	} else {
		unsigned sx = (offset + (lenone & 3)) & ~0x3;
		if (sx == 0 || sx == 0x80) {
			msk6 = 0;
		} else if (sx < 0x40) {
			msk6 = ~0ULL << (64 - sx);
		} else {
			msk6 = ~0ULL >> (sx - 64);
		}
	}

	// The actual rotation
	if (op == 0) {
		s = (lenone ^ 0x3f) + 0xc0 - offset;
	} else {
		s = lenone + offset + 1;
	}
	s &= 0x3f;

	fs = s & 3;
	if (fs == 0) {
		tir = r1k->fiu_ti_bus;
		vir = r1k->fiu_vi_bus;
	} else {
		tir = r1k->fiu_ti_bus >> fs;
		tir |= r1k->fiu_vi_bus << (64 - fs);
		vir = r1k->fiu_vi_bus >> fs;
		vir |= r1k->fiu_ti_bus << (64 - fs);
	}

	ft = msk6 & vir;
	ft |= (~msk6) & tir;

	if (fill_mode) {
		sgnbit = true;
	} else {
		sgn = offset & 0x3c;
		if ((offset & 3) + (lenone & 3) > 3)
			sgn += 4;
		sgn |= (lenone & 3) ^ 3;

		sgnbit = (ft >> (63 - sgn)) & 1;
	}

	uint64_t rot;
	{
		fs = s & ~3;
		uint64_t yl = ft >> fs;
		uint64_t yh = ft << (64 - fs);
		rot = yh | yl;
	}

	if (zero_length) {
		if (ebit == sbit) {
			if (ebit < 64) {
				tmsk = 1ULL << (63 - ebit);
				vmsk = 0;
			} else {
				tmsk = 0;
				vmsk = 1ULL << (127 - ebit);
			}
		} else {
			uint64_t inv = 0;
			unsigned sb = sbit, eb = ebit;
			if (eb < sb) {
				sb = ebit + 1;
				eb = sbit - 1;
				inv = ~(uint64_t)0;
			}
			if (sb < 64)
				tmsk = (~(uint64_t)0) >> sb;
			if (eb < 63)
				tmsk ^= (~(uint64_t)0) >> (eb + 1);
			if (eb > 63)
				vmsk = (~(uint64_t)0) << (127 - eb);
			if (sb > 64)
				vmsk ^= (~(uint64_t)0) << (128 - sb);
			tmsk ^= inv;
			vmsk ^= inv;
		}
	}

	unsigned sel = UIR_FIU_SEL;

	uint64_t tii = 0;
	switch(sel) {
	case 0:
	case 1:
		if (sgnbit)
			tii = ~0ULL;
		break;
	case 2:
		tii = r1k->fiu_vi_bus;
		break;
	case 3:
		tii = ~mp_fiu_bus;
		break;
	default:
		assert(0);
	}

	uint64_t rdq;
	if (UIR_FIU_RDSRC) {				// UCODE
		rdq = r1k->fiu_mdreg;
	} else {
		rdq = rot;
	}

	uint64_t vout = rdq & vmsk;
	vout |= tii & ~vmsk;

	if (mp_fiu_oe == 0x1) {
		mp_fiu_bus = ~vout;
	}

	if (sclk && UIR_FIU_LDMDR) {			// (UCODE)
		r1k->fiu_mdreg = rot;
	}

	if (sclk && !UIR_FIU_TCLK) {			// Q4~^
		r1k->fiu_treg = rdq & tmsk;
		r1k->fiu_treg |= r1k->fiu_ti_bus & ~tmsk;
	}

	if (sclk && !UIR_FIU_VCLK) {			// Q4~^
		r1k->fiu_vreg = vout;
	}
}

static void
fiu_q1(void)
{
	bool sclk = false;
	bool carry, name_match;

	unsigned pa028a = mp_mar_cntl << 5;
	pa028a |= r1k->fiu_incmplt_mcyc << 4;
	pa028a |= r1k->fiu_e_abort_dly << 3;
	pa028a |= r1k->fiu_state1 << 2;
	pa028a |= r1k->fiu_mctl_is_read << 1;
	pa028a |= r1k->fiu_dumon;
	r1k->fiu_prmt = fiu_pa028[pa028a];
	r1k->fiu_prmt ^= 0x02;
	r1k->fiu_prmt &= 0x7b;

	bool rmarp = (mp_mar_cntl & 0xe) == 0x4;
	r1k->fiu_mem_start = UIR_FIU_MSTRT ^ 0x1e;

	fiu_do_tivi();
	if (mp_fiu_oe == 0x1) {
		fiu_rotator(sclk);
	}
	unsigned dif;

	if (r1k->fiu_pdt) {
		carry = r1k->fiu_ctopo <= r1k->fiu_pdreg;
		dif = ~0xfffff + r1k->fiu_pdreg - r1k->fiu_ctopo;
	} else {
		carry = r1k->fiu_moff <= r1k->fiu_ctopo;
		dif = ~0xfffff + r1k->fiu_ctopo - r1k->fiu_moff;
	}
	dif &= 0xfffff;

	name_match =
		    (r1k->fiu_ctopn != r1k->fiu_srn) ||
		    ((r1k->fiu_sro & 0xf8000070 ) != 0x10);

	r1k->fiu_in_range = (!r1k->fiu_pdt && name_match) || (dif & 0xffff0);

	r1k->fiu_hit_offset = (0xf + r1k->fiu_nve - (dif & 0xf)) & 0xf;

	mp_csa_hit = (bool)!(carry && !(r1k->fiu_in_range || ((dif & 0xf) >= r1k->fiu_nve)));

	unsigned pa025a = 0;
	pa025a |= r1k->fiu_mem_start;
	pa025a |= r1k->fiu_state0 << 8;
	pa025a |= r1k->fiu_state1 << 7;
	pa025a |= r1k->fiu_labort << 6;
	pa025a |= r1k->fiu_e_abort_dly << 5;
	r1k->fiu_pa025d = fiu_pa025[pa025a];
	r1k->fiu_memcyc1 = (r1k->fiu_pa025d >> 1) & 1;
	r1k->fiu_memstart = (r1k->fiu_pa025d >> 0) & 1;

	if (r1k->fiu_memstart) {
		r1k->fiu_mcntl = r1k->fiu_lcntl;
	} else {
		r1k->fiu_mcntl = r1k->fiu_pcntl_d;
	}
	r1k->fiu_phys_ref = !(r1k->fiu_mcntl & 0x6);
	r1k->fiu_logrwn = !(r1k->fiu_logrw && r1k->fiu_memcyc1);
	r1k->fiu_logrw = !(r1k->fiu_phys_ref || ((r1k->fiu_mcntl >> 3) & 1));

	r1k->fiu_scav_trap_next = r1k->fiu_scav_trap;
	if (mp_cond_sel == 0x69) {		// SCAVENGER_HIT
		r1k->fiu_scav_trap_next = false;
	} else if (rmarp) {
		r1k->fiu_scav_trap_next = (r1k->fiu_ti_bus >> BUS64_LSB(32)) & 1;
	} else if (r1k->fiu_log_query) {
		r1k->fiu_scav_trap_next = false;
	}


	r1k->fiu_tmp_csa_oor_next = r1k->fiu_csa_oor;
	if (mp_cond_sel == 0x68) {		// CSA_OUT_OF_RANGE
		r1k->fiu_tmp_csa_oor_next = false;
	} else if (rmarp) {
		r1k->fiu_tmp_csa_oor_next = (r1k->fiu_ti_bus >> BUS64_LSB(33)) & 1;
	} else if (r1k->fiu_log_query) {
		r1k->fiu_tmp_csa_oor_next = r1k->fiu_csa_oor_next;
	}

	bool pgmod = (r1k->fiu_omq >> 1) & 1;
	unsigned pa027a = 0;
	pa027a |= mp_mem_hit << 5;
	pa027a |= r1k->fiu_init_mru_d << 4;
	pa027a |= (r1k->fiu_omq & 0xc);
	pa027a |= 1U << 1;
	pa027a |= pgmod << 0;
	r1k->fiu_pa027d = fiu_pa027[pa027a];
	r1k->fiu_setq = (r1k->fiu_pa027d >> 3) & 3;

	bool mnor0b = r1k->fiu_drive_mru || ((r1k->fiu_pa027d & 3) == 0);
	bool mnan2a = !(mnor0b && r1k->fiu_logrw_d);
	r1k->fiu_miss = !(
		((mp_mem_hit != 0xf) && mnan2a) ||
		(r1k->fiu_logrw_d && r1k->fiu_csaht)
	);
	if (mp_refresh_count == 0xffff) {
		mp_macro_event |= 0x40;
	} else {
		mp_macro_event &= ~0x40;
	}

	if (mp_tv_oe & (FIU_T_OE|FIU_V_OE)) {
		fiu_do_tivi();
		if (mp_tv_oe & FIU_T_OE) {
			mp_typ_bus = ~r1k->fiu_ti_bus;
		}
		if (mp_tv_oe & FIU_V_OE) {
			mp_val_bus = ~r1k->fiu_vi_bus;
		}
	}
}

static void
fiu_q2(void)
{
	unsigned pa028a = mp_mar_cntl << 5;
	pa028a |= r1k->fiu_incmplt_mcyc << 4;
	pa028a |= r1k->fiu_e_abort_dly << 3;
	pa028a |= r1k->fiu_state1 << 2;
	pa028a |= r1k->fiu_mctl_is_read << 1;
	pa028a |= r1k->fiu_dumon;
	r1k->fiu_prmt = fiu_pa028[pa028a];
	r1k->fiu_prmt ^= 0x02;
	r1k->fiu_prmt &= 0x7b;

	fiu_do_tivi();
	unsigned pa025a = 0;
	pa025a |= r1k->fiu_mem_start;
	pa025a |= r1k->fiu_state0 << 8;
	pa025a |= r1k->fiu_state1 << 7;
	pa025a |= r1k->fiu_labort << 6;
	pa025a |= r1k->fiu_e_abort_dly << 5;
	r1k->fiu_pa025d = fiu_pa025[pa025a];
	r1k->fiu_memcyc1 = (r1k->fiu_pa025d >> 1) & 1;
	r1k->fiu_memstart = (r1k->fiu_pa025d >> 0) & 1;

	if (r1k->fiu_memstart) {
		r1k->fiu_mcntl = r1k->fiu_lcntl;
	} else {
		r1k->fiu_mcntl = r1k->fiu_pcntl_d;
	}
	r1k->fiu_phys_ref = !(r1k->fiu_mcntl & 0x6);
	r1k->fiu_logrwn = !(r1k->fiu_logrw && r1k->fiu_memcyc1);
	r1k->fiu_logrw = !(r1k->fiu_phys_ref || ((r1k->fiu_mcntl >> 3) & 1));

	unsigned mar_cntl = mp_mar_cntl;
	bool rmarp = (mar_cntl & 0xe) == 0x4;

	r1k->fiu_scav_trap_next = r1k->fiu_scav_trap;
	if (mp_cond_sel == 0x69) {		// SCAVENGER_HIT
		r1k->fiu_scav_trap_next = false;
	} else if (rmarp) {
		r1k->fiu_scav_trap_next = (r1k->fiu_ti_bus >> BUS64_LSB(32)) & 1;
	} else if (r1k->fiu_log_query) {
		r1k->fiu_scav_trap_next = false;
	}


	r1k->fiu_tmp_csa_oor_next = r1k->fiu_csa_oor;
	if (mp_cond_sel == 0x68) {		// CSA_OUT_OF_RANGE
		r1k->fiu_tmp_csa_oor_next = false;
	} else if (rmarp) {
		r1k->fiu_tmp_csa_oor_next = (r1k->fiu_ti_bus >> BUS64_LSB(33)) & 1;
	} else if (r1k->fiu_log_query) {
		r1k->fiu_tmp_csa_oor_next = r1k->fiu_csa_oor_next;
	}

	unsigned pa026a = r1k->fiu_mem_start;
	if (r1k->fiu_omq & 0x02)	// INIT_MRU_D
		pa026a |= 0x20;
	if (r1k->fiu_phys_last)
		pa026a |= 0x40;
	if (r1k->fiu_write_last)
		pa026a |= 0x80;
	r1k->fiu_pa026d = fiu_pa026[pa026a];
	// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3

	if (r1k->fiu_log_query) {
		// PIN_MISS instead of cache_miss_next looks suspicious
		// but confirmed on both /200 and /400 FIU boards.
		// 20230910/phk
		r1k->fiu_memex = !(!r1k->fiu_miss && !r1k->fiu_tmp_csa_oor_next && !r1k->fiu_scav_trap_next);
	} else {
		r1k->fiu_memex = !(!r1k->fiu_cache_miss && !r1k->fiu_csa_oor && !r1k->fiu_scav_trap);
	}
	mp_restore_rdr = (r1k->fiu_prmt >> 1) & 1;
	bool sel = !((!mp_state_clk_stop && r1k->fiu_memcyc1) || (mp_state_clk_en && !r1k->fiu_memcyc1));
	if (sel) {
		mp_dummy_next = !((r1k->fiu_prmt >> 0) & 1);
	} else {
		mp_dummy_next = !r1k->fiu_dumon;
	}

	mp_csa_wr = !(mp_mem_abort_l && mp_mem_abort_el && !(r1k->fiu_logrwn || (r1k->fiu_mcntl & 1)));
	if (mp_adr_oe & 0x1) {
		bool inc_mar = (r1k->fiu_prmt >> 3) & 1;
		unsigned inco = r1k->fiu_moff & 0x1f;
		if (inc_mar && inco != 0x1f)
			inco += 1;

		mp_adr_bus = (uint64_t)r1k->fiu_srn << 32;
		mp_adr_bus |= r1k->fiu_sro & 0xfffff000;
		mp_adr_bus |= (inco & 0x1f) << 7;
		mp_adr_bus |= r1k->fiu_oreg;
		mp_spc_bus = (r1k->fiu_sro >> 4) & 7;
	}

	r1k->fiu_lcntl = r1k->fiu_mcntl;
	r1k->fiu_drive_mru = r1k->fiu_init_mru_d;
	r1k->fiu_memcnd = (r1k->fiu_pa025d >> 4) & 1;	// CM_CTL0
	r1k->fiu_cndtru = (r1k->fiu_pa025d >> 3) & 1;	// CM_CTL1
	mp_mem_cond= !(r1k->fiu_memcnd);
	mp_mem_cond_pol = !(r1k->fiu_cndtru);

	if (r1k->fiu_memcyc1) {
		mp_mem_ctl= r1k->fiu_lcntl;
	} else {
		mp_mem_ctl= r1k->fiu_pa026d & 0xf;
	}
	bool inc_mar = (r1k->fiu_prmt >> 3) & 1;
	r1k->fiu_page_crossing_next = (
		mp_cond_sel != 0x6a) && (// sel_pg_xing
		mp_cond_sel != 0x6e) && (// sel_incyc_px
		(
			(r1k->fiu_page_xing) ||
			(!r1k->fiu_page_xing && inc_mar && (r1k->fiu_moff & 0x1f) == 0x1f)
		)
	);
	mp_mem_continue= !((r1k->fiu_pa025d >> 5) & 1);
	r1k->fiu_uev10_page_x = !(mp_uevent_enable && r1k->fiu_page_xing);
	if (mp_uevent_enable && r1k->fiu_page_xing) {
		mp_seq_uev |= UEV_PAGE_X;
	} else {
		mp_seq_uev &= ~UEV_PAGE_X;
	}
	r1k->fiu_uev0_memex = !(mp_uevent_enable && r1k->fiu_memex);
	if (mp_uevent_enable && r1k->fiu_memex) {
		mp_seq_uev |= UEV_MEMEX;
	} else {
		mp_seq_uev &= ~UEV_MEMEX;
	}
	mp_clock_stop_0 = r1k->fiu_uev10_page_x && r1k->fiu_uev0_memex;
	{
	bool invalidate_csa = !(mp_csa_hit && !r1k->fiu_tcsa_tf_pred);
	unsigned hit_offs = r1k->fiu_hit_offset;

	unsigned adr;
	if (r1k->fiu_tcsa_tf_pred) {
		adr = r1k->fiu_tcsa_sr;
		adr |= 0x100;
	} else {
		adr = hit_offs;
	}
	adr ^= 0xf;
	unsigned csacntl = mp_csa_cntl;
	adr |= csacntl << 4;

	if (r1k->fiu_tcsa_inval_csa)
		adr |= (1<<7);

	unsigned q = fiu_pa060[adr];
	bool load_ctl_top = (q >> 3) & 0x1;
	bool load_top_bot = (q >> 2) & 0x1;
	bool sel_constant = (q >> 1) & 0x1;
	bool minus_one = (q >> 0) & 0x1;

	mp_load_top = !(load_top_bot && ((csacntl >> 1) & 1));
	mp_load_bot = !(load_top_bot && ((csacntl >> 2) & 1));
	mp_pop_down = load_ctl_top && r1k->fiu_tcsa_tf_pred;

	if (!invalidate_csa) {
		mp_csa_this_offs = 0xf;
	} else if (!sel_constant && !minus_one) {
		mp_csa_this_offs = 0x1;
	} else if (!sel_constant && minus_one) {
		mp_csa_this_offs = 0xf;
	} else {
		mp_csa_this_offs = hit_offs;
	}
	mp_csa_this_offs ^= 0xf;

	mp_csa_nve = q >> 4;
	}
	if (mp_tv_oe & (FIU_T_OE|FIU_V_OE)) {
		if (mp_tv_oe & FIU_T_OE) {
			mp_typ_bus = ~r1k->fiu_ti_bus;
		}
		if (mp_tv_oe & FIU_V_OE) {
			mp_val_bus = ~r1k->fiu_vi_bus;
		}
	}
}

static void
fiu_q4(void)
{
	bool sclk = !mp_state_clk_en;
	bool tcsa_clk = (mp_clock_stop && mp_ram_stop && !mp_freeze);
	unsigned mar_cntl = mp_mar_cntl;
	bool rmarp = (mar_cntl & 0xe) == 0x4;
	bool carry, name_match;

	unsigned csa = mp_csa_cntl;
	unsigned pa028a = mp_mar_cntl << 5;
	pa028a |= r1k->fiu_incmplt_mcyc << 4;
	pa028a |= r1k->fiu_e_abort_dly << 3;
	pa028a |= r1k->fiu_state1 << 2;
	pa028a |= r1k->fiu_mctl_is_read << 1;
	pa028a |= r1k->fiu_dumon;
	r1k->fiu_prmt = fiu_pa028[pa028a];
	r1k->fiu_prmt ^= 0x02;
	r1k->fiu_prmt &= 0x7b;

	if (tcsa_clk) {
		bool invalidate_csa = !(mp_csa_hit && !r1k->fiu_tcsa_tf_pred);
		r1k->fiu_tcsa_inval_csa = invalidate_csa;
		unsigned csacntl0 = (r1k->fiu_typwcsram[mp_nua_bus] >> 1) & 7;
		unsigned csacntl1 = (r1k->fiu_typuir >> 1) & 6;
		r1k->fiu_tcsa_tf_pred = !((csacntl0 == 7) && (csacntl1 == 0));
		r1k->fiu_tcsa_sr = mp_csa_nve;
	}
	if (sclk) {
		if (UIR_FIU_LDMDR || !UIR_FIU_TCLK || !UIR_FIU_VCLK) {
			fiu_rotator(sclk);
		}

		if (!UIR_FIU_OCLK) {			// Q4~^
			if (UIR_FIU_ORSR) {			// UCODE
				r1k->fiu_oreg = UIR_FIU_OL;
			} else {
				r1k->fiu_oreg = mp_adr_bus & 0x7f;
			}
		}

		if (mar_cntl == 5) {
			r1k->fiu_refresh_reg = r1k->fiu_ti_bus;
			r1k->fiu_marh &= 0xffffffffULL;
			r1k->fiu_marh |= (r1k->fiu_refresh_reg & 0xffffffff00000000ULL);
			r1k->fiu_marh ^= 0xffffffff00000000ULL;
		}

		unsigned lfrc;
		lfrc = UIR_FIU_LFRC;

		switch(lfrc) {
		case 0:
			r1k->fiu_lfreg = (((r1k->fiu_vi_bus >> BUS64_LSB(31)) & 0x3f) + 1) & 0x3f;
			if ((r1k->fiu_ti_bus >> BUS64_LSB(36)) & 1)
				r1k->fiu_lfreg |= (1U << 6);
			else if (!((r1k->fiu_vi_bus >> BUS64_LSB(25)) & 1))
				r1k->fiu_lfreg |= (1U << 6);
			r1k->fiu_lfreg ^= 0x7f;
			break;
		case 1:
			r1k->fiu_lfreg = UIR_FIU_LFL;
			break;
		case 2:
			r1k->fiu_lfreg = (r1k->fiu_ti_bus >> BUS64_LSB(48)) & 0x3f;
			if ((r1k->fiu_ti_bus >> BUS64_LSB(36)) & 1)
				r1k->fiu_lfreg |= (1U << 6);
			r1k->fiu_lfreg = r1k->fiu_lfreg ^ 0x7f;
			break;
		case 3:	// No load
			break;
		default: assert(0);
		}

		r1k->fiu_marh &= ~(0x3fULL << 15);
		r1k->fiu_marh |= (r1k->fiu_lfreg & 0x3f) << 15;
		r1k->fiu_marh &= ~(1ULL << 27);
		r1k->fiu_marh |= ((r1k->fiu_lfreg >> 6) & 1) << 27;
		if (r1k->fiu_lfreg != 0x7f)
			r1k->fiu_lfreg |= 1<<7;

		unsigned csacntl0 = (r1k->fiu_typwcsram[mp_nua_bus] >> 1) & 7;
		unsigned csacntl1 = (r1k->fiu_typuir >> 1) & 6;
		r1k->fiu_pdt = (csacntl0 == 7) && (csacntl1 == 0);
		r1k->fiu_nve = mp_csa_nve;
		if (!(csa >> 2)) {
			r1k->fiu_pdreg = r1k->fiu_ctopo;
		}
	}

	unsigned dif;

	if (r1k->fiu_pdt) {
		carry = r1k->fiu_ctopo <= r1k->fiu_pdreg;
		dif = ~0xfffff + r1k->fiu_pdreg - r1k->fiu_ctopo;
	} else {
		carry = r1k->fiu_moff <= r1k->fiu_ctopo;
		dif = ~0xfffff + r1k->fiu_ctopo - r1k->fiu_moff;
	}
	dif &= 0xfffff;

	name_match =
		    (r1k->fiu_ctopn != r1k->fiu_srn) ||
		    ((r1k->fiu_sro & 0xf8000070 ) != 0x10);

	r1k->fiu_in_range = (!r1k->fiu_pdt && name_match) || (dif & 0xffff0);

	r1k->fiu_hit_offset = (0xf + r1k->fiu_nve - (dif & 0xf)) & 0xf;

	if (sclk) {
		if ((r1k->fiu_prmt >> 4) & 1) { // load_mar
			r1k->fiu_srn = mp_adr_bus >> 32;
			r1k->fiu_sro = mp_adr_bus & 0xffffff80;
			r1k->fiu_sro |= mp_spc_bus << 4;
			r1k->fiu_sro |= 0xf;
			r1k->fiu_moff = (r1k->fiu_sro >> 7) & 0xffffff;
		}

		if (csa == 0) {
			r1k->fiu_ctopn = mp_adr_bus >> 32;
		}

		r1k->fiu_nmatch =
		    (r1k->fiu_ctopn != r1k->fiu_srn) ||
		    ((r1k->fiu_sro & 0xf8000070 ) != 0x10);

		if (!(csa >> 2)) {
			if (csa <= 1) {
				r1k->fiu_ctopo = mp_adr_bus >> 7;
			} else if (!(csa & 1)) {
				r1k->fiu_ctopo += 1;
			} else {
				r1k->fiu_ctopo += 0xfffff;
			}
			r1k->fiu_ctopo &= 0xfffff;
		}
	}

	if (r1k->fiu_mem_start == 0x06) {
		mp_refresh_count = r1k->fiu_ti_bus >> 48;
	} else if (mp_refresh_count != 0xffff) {
		mp_refresh_count++;
	}

	if (!((!mp_state_clk_stop && r1k->fiu_memcyc1) || (mp_state_clk_en && !r1k->fiu_memcyc1))) {
		r1k->fiu_dumon = (r1k->fiu_prmt >> 5) & 1;
	} else {
		r1k->fiu_dumon = r1k->fiu_dumon;
	}
	r1k->fiu_state0 = (r1k->fiu_pa025d >> 7) & 1;
	r1k->fiu_state1 = (r1k->fiu_pa025d >> 6) & 1;
	r1k->fiu_labort = !(mp_mem_abort_l && mp_mem_abort_el);
	r1k->fiu_e_abort_dly = !(mp_mem_abort_e && mp_mem_abort_el);
	r1k->fiu_pcntl_d = r1k->fiu_pa026d & 0xf;
	r1k->fiu_csaht = !mp_csa_hit;

	if (!mp_sf_stop) {
		bool cache_miss_next = r1k->fiu_cache_miss;
		if (mp_cond_sel == 0x6b) {		// CACHE_MISS
			cache_miss_next = false;
		} else if (rmarp) {
			cache_miss_next = (r1k->fiu_ti_bus >> BUS64_LSB(35)) & 1;
		} else if (r1k->fiu_log_query) {
			cache_miss_next = r1k->fiu_miss;
		}
		r1k->fiu_scav_trap = r1k->fiu_scav_trap_next;
		r1k->fiu_cache_miss = cache_miss_next;
		r1k->fiu_csa_oor = r1k->fiu_tmp_csa_oor_next;

		if (rmarp) {
			r1k->fiu_mar_modified = (r1k->fiu_ti_bus >> BUS64_LSB(39)) & 1;
		} else if (mp_cond_sel == 0x6d) {
			r1k->fiu_mar_modified = 1;
		} else if (r1k->fiu_omf20) {
			r1k->fiu_mar_modified = mp_mem_abort_el;
		} else if (!r1k->fiu_memstart && mp_mem_abort_el) {
			r1k->fiu_mar_modified = mp_mem_abort_el;
		}
		if (rmarp) {
			r1k->fiu_incmplt_mcyc = (r1k->fiu_ti_bus >> BUS64_LSB(40)) & 1;
		} else if (r1k->fiu_mem_start == 0x12) {
			r1k->fiu_incmplt_mcyc = true;
		} else if (r1k->fiu_memcyc1) {
			r1k->fiu_incmplt_mcyc = mp_mem_abort_el;
		}
		if (rmarp) {
			r1k->fiu_phys_last = (r1k->fiu_ti_bus >> BUS64_LSB(37)) & 1;
			r1k->fiu_write_last = (r1k->fiu_ti_bus >> BUS64_LSB(38)) & 1;
		} else if (r1k->fiu_memcyc1) {
			r1k->fiu_phys_last = r1k->fiu_phys_ref;
			r1k->fiu_write_last = (r1k->fiu_mcntl & 1);
		}

		r1k->fiu_log_query = !(r1k->fiu_labort || r1k->fiu_logrwn);

		r1k->fiu_omf20 = (r1k->fiu_memcyc1 && ((r1k->fiu_prmt >> 3) & 1) && !mp_state_clk_en);

		if (r1k->fiu_memcyc1)
			r1k->fiu_mctl_is_read = !(r1k->fiu_lcntl & 1);
		else
			r1k->fiu_mctl_is_read = !(r1k->fiu_pa026d & 1);

		r1k->fiu_logrw_d = r1k->fiu_logrw;
	}

	if (!mp_state_clk_en) {
		r1k->fiu_omq = 0;
		r1k->fiu_omq |= (r1k->fiu_pa027d & 3) << 2;
		r1k->fiu_omq |= ((r1k->fiu_pa027d >> 5) & 1) << 1;
		if (rmarp) {
			r1k->fiu_page_xing = (r1k->fiu_ti_bus >> BUS64_LSB(34)) & 1;
		} else {
			r1k->fiu_page_xing = (r1k->fiu_page_crossing_next);
		}
		r1k->fiu_init_mru_d = (r1k->fiu_pa026d >> 7) & 1;
	}
	r1k->fiu_csa_oor_next = !(carry || name_match);

	if (!mp_sf_stop) {
		r1k->fiu_uir = r1k->fiu_wcsram[mp_nua_bus];
		r1k->fiu_typuir = r1k->fiu_typwcsram[mp_nua_bus];
	}
}

// -------------------- SEQ --------------------

static void
seq_int_reads(void)
{
	unsigned internal_reads = UIR_SEQ_IRD;
	switch (r1k->seq_urand & 3) {
	case 3:	r1k->seq_code_offset = r1k->seq_retrn_pc_ofs; break;
	case 2: r1k->seq_code_offset = r1k->seq_branch_offset; break;
	case 1: r1k->seq_code_offset = r1k->seq_macro_pc_offset; break;
	case 0: r1k->seq_code_offset = r1k->seq_branch_offset; break;
	default: assert(0);
	}
	r1k->seq_code_offset ^= 0x7fff;
	if (internal_reads == 0) {
		r1k->seq_typ_bus = ~mp_typ_bus;
		r1k->seq_val_bus = ~mp_val_bus;
		return;
	}

	r1k->seq_typ_bus = r1k->seq_n_in_csa;
	r1k->seq_typ_bus |= r1k->seq_output_ob << 7;
	r1k->seq_typ_bus ^= 0xffffffff;

	switch (internal_reads) {
	case 5:
		r1k->seq_typ_bus |= (r1k->seq_name_bus ^ 0xffffffff) << 32;
		break;
	default:
		r1k->seq_typ_bus |= (uint64_t)r1k->seq_cur_name << 32;
		break;
	}

	if (r1k->seq_urand & 0x2) {
		r1k->seq_val_bus = r1k->seq_retseg << 32;
	} else {
		r1k->seq_val_bus = r1k->seq_pcseg << 32;
	}

	switch (internal_reads) {
	case 1:
		r1k->seq_val_bus |= r1k->seq_curins;
		break;
	case 2:
		r1k->seq_val_bus |= r1k->seq_display ^ 0xffff;
		break;
	case 3:
		r1k->seq_val_bus |= r1k->seq_topu ^ 0xffff;
		break;
	default:
		// This is a variance from the schematics, which drive
		// the top three bits of seq_code_offset in all cases.
		// (See: SEQ.p29)
		r1k->seq_val_bus |= (r1k->seq_code_offset << 4);
		r1k->seq_val_bus |= r1k->seq_curr_lex & 0xf;
		break;
	}
	r1k->seq_val_bus = ~r1k->seq_val_bus;
}

static bool
seq_conda(unsigned condsel)
{

	switch (condsel) {
	case 0x57: // FIELD_NUM_ERR
		return (!r1k->seq_field_number_error);
	case 0x56: // LATCHED_COND
		return (!r1k->seq_latched_cond);
	case 0x55: // E_MACRO_PEND
		return (!r1k->seq_early_macro_pending);
	case 0x54: // E_MACRO_EVNT~6
		return (!((r1k->seq_emac >> 0) & 1));
	case 0x53: // E_MACRO_EVNT~5
		return (!((r1k->seq_emac >> 1) & 1));
	case 0x52: // E_MACRO_EVNT~3
		return (!((r1k->seq_emac >> 3) & 1));
	case 0x51: // E_MACRO_EVNT~2
		return (!((r1k->seq_emac >> 4) & 1));
	case 0x50: // E_MACRO_EVNT~0
		return (!((r1k->seq_emac >> 6) & 1));
	default:
		return (false);
	}
}

static bool
seq_cond9(unsigned condsel)
{

	switch (condsel) {
	case 0x4f: // DISP_COND0
		return ((r1k->seq_decode & 0x7) == 0);
	case 0x4e: // True
		return (true);
	case 0x4d: // M_IBUFF_MT
		return (r1k->seq_m_ibuff_mt);
	case 0x4c: // M_BRK_CLASS
		return (!r1k->seq_m_break_class);
	case 0x4b: // M_TOS_INVLD
		return (r1k->seq_m_tos_invld);
	case 0x4a: // M_RES_REF
		return (r1k->seq_m_res_ref);
	case 0x49: // M_OVERFLOW
		{
		unsigned csa = mp_csa_nve;
		unsigned dec = r1k->seq_decode >> 3;
		return (csa <= ((dec >> 3) | 12));
		}
	case 0x48: // M_UNDERFLOW
		{
		unsigned csa = mp_csa_nve;
		unsigned dec = r1k->seq_decode >> 3;
		return (csa >= (dec & 7));
		}
	default:
		return (false);
	}
}

static bool
seq_cond8(unsigned condsel)
{

	switch (condsel) {
	case 0x47: // E STACK_SIZE
		return (r1k->seq_stack_size_zero);
	case 0x46: // E LATCHED_COND
		return (r1k->seq_latched_cond);
	case 0x45: // L SAVED_LATCHED
		return (r1k->seq_saved_latched);
	case 0x44: // L TOS_VLD.COND
		return (r1k->seq_tos_vld_cond);
	case 0x43: // L LEX_VLD.COND
		return (r1k->seq_lxval);
	case 0x42: // E IMPORT.COND
		return (r1k->seq_resolve_address != 0xf);
	case 0x41: // E REST_PC_DEC
		return ((r1k->seq_rq >> 1) & 1);
	case 0x40: // E RESTARTABLE
		return ((r1k->seq_rq >> 3) & 1);
	default:
		return (false);
	}
}

static void
seq_nxt_lex_valid(void)
{

	switch((r1k->seq_rndx >> 5) & 0x7) {	// SEQ microarch pdf pg 33
	case 0:	// Clear Lex Level
		r1k->seq_lex_valid &= ~(1 << (15 - r1k->seq_resolve_address));
		break;
	case 1: // Set Lex Level
		r1k->seq_lex_valid |= (1 << (15 - r1k->seq_resolve_address));
		break;
	case 4: // Clear Greater Than Lex Level
		r1k->seq_lex_valid &= ~(0xfffe << (15 - r1k->seq_resolve_address));
		break;
	case 7: // Clear all Lex Levels
		r1k->seq_lex_valid = 0;
		break;
	default:
		break;
	}
}

static bool
seq_condition(void)
{
	unsigned condsel = UIR_SEQ_CSEL;

	switch (condsel >> 3) {
	case 0x0: return(val_cond());
	case 0x1: return(val_cond());
	case 0x2: return(val_cond());
	case 0x3: return(typ_cond());
	case 0x4: return(typ_cond());
	case 0x5: return(typ_cond());
	case 0x6: return(typ_cond());
	case 0x7: return(typ_cond());
	case 0x8: return(seq_cond8(condsel));
	case 0x9: return(seq_cond9(condsel));
	case 0xa: return(seq_conda(condsel));
	case 0xb:
		{
		bool tc = typ_cond();
		bool vc = val_cond();
		return(!(tc && vc));
		}
	case 0xc: return(fiu_conditions());
	case 0xd: return(fiu_conditions());
	case 0xf: return(ioc_cond());
	default: return(1);
	}
}

static unsigned
seq_branch_offset(void)
{
	unsigned retval = r1k->seq_macro_pc_offset;
	assert(!(retval & ~0x7fff));

	if (r1k->seq_wanna_dispatch) {
		unsigned a = r1k->seq_curins & 0x7ff;
		if (a & 0x400)
			a |= 0x7800;
		a ^= 0x7fff;
		a += 1;
		retval += a;
	} else if (!r1k->seq_m_ibuff_mt) {
		retval += 0x7fff;
	} else {
		unsigned a = r1k->seq_display & 0x7ff;
		if (a & 0x400)
			a |= 0x7800;
		a ^= 0x7fff;
		a += 1;
		retval -= a;
	}
	return (retval & 0x7fff);
}

static void
seq_q3clockstop(void)
{
	bool event = true;
	mp_state_clk_stop = true;
	r1k->seq_s_state_stop = true;
	mp_clock_stop = true;
	mp_ram_stop = true;

	if (mp_seq_halted && mp_seq_prepped) {
		r1k->seq_diag |= 0x01;
		mp_sync_freeze |= 1;
	} else {
		r1k->seq_diag &= ~0x01;
		mp_sync_freeze &= ~1;
	}

	if (mp_fiu_freeze && !(r1k->seq_diag & 0x2)) {
		r1k->seq_diag |= 0x02;
		mp_sync_freeze |= 2;
	} else if (!mp_fiu_freeze && (r1k->seq_diag & 0x2) && !(r1k->seq_diag & 0x4)) {
		r1k->seq_diag |= 0x04;
		mp_sync_freeze |= 4;
	} else if (!mp_fiu_freeze && (r1k->seq_diag & 0x2) && (r1k->seq_diag & 0x4)) {
		r1k->seq_diag &= ~0x02;
		mp_sync_freeze &= ~2;
		r1k->seq_countdown = 5;
	} else if (!mp_fiu_freeze && !(r1k->seq_diag & 0x2) && (r1k->seq_diag & 0x4)) {
		if (--r1k->seq_countdown == 0) {
			r1k->seq_diag &= ~0x04;
			mp_sync_freeze &= ~4;
		}
	}

	mp_sf_stop = r1k->seq_diag != 0;
	mp_freeze = (r1k->seq_diag & 3) != 0;

	unsigned clock_stop = 0;
	r1k->seq_clock_stop_1 = !(mp_clock_stop_6 && mp_clock_stop_7 && mp_below_tcp);
	if (mp_clock_stop_0) { clock_stop |= 0x40; }
	if (r1k->seq_clock_stop_1) { clock_stop |= 0x20; }
	if (mp_clock_stop_3) { clock_stop |= 0x10; }
	if (mp_clock_stop_4) { clock_stop |= 0x08; }
	if (r1k->seq_clock_stop_5) { clock_stop |= 0x04; }
	if (mp_clock_stop_6) { clock_stop |= 0x02; }
	if (mp_clock_stop_7) { clock_stop |= 0x01; }

	if ((clock_stop | 0x01) != 0x7f) {
		mp_state_clk_stop = false;
		event = false;
	}
	if (clock_stop != 0x7f) {
		mp_clock_stop = false;
		if (!mp_csa_write_enable) {
			mp_ram_stop = false;
		}
	}
	if ((clock_stop | 0x03) != 0x7f) {
		r1k->seq_s_state_stop = false;
	}

	if (mp_sf_stop) {
		mp_clock_stop = false;
		mp_state_clk_stop = false;
		r1k->seq_s_state_stop = false;
		if (!mp_csa_write_enable) {
			mp_ram_stop = false;
		}
	}
	mp_state_clk_en= !(mp_state_clk_stop && mp_clock_stop_7);
	mp_mem_abort_el = event;
}

static void
seq_p1(void)
{
	if (r1k->seq_maybe_dispatch && !(r1k->seq_display >> 15)) {
		r1k->seq_resolve_address = r1k->seq_display >> 9;
	} else {
		switch (UIR_SEQ_LAUIR) {
		case 0:
			r1k->seq_resolve_address = ~r1k->seq_curr_lex;
			break;
		case 1:
			switch (UIR_SEQ_IRD) {
			case 0x0:
				r1k->seq_resolve_address = ~mp_val_bus + 1;
				break;
			case 0x1:
			case 0x2:
			case 0x3:
				assert(0);
				break;
			default:
				r1k->seq_resolve_address = ~r1k->seq_curr_lex + 1;
				break;
			}
			break;
		case 2: r1k->seq_resolve_address = 0xf; break;
		case 3: r1k->seq_resolve_address = 0xe; break;
		default: assert(0);
		}
	}
	r1k->seq_resolve_address &= 0xf;

	unsigned offs;
	if (r1k->seq_maybe_dispatch && r1k->seq_uses_tos) {
		if (RNDX(RND_TOS_VLB)) {
			assert (UIR_SEQ_IRD == 0);
			offs = ((~mp_typ_bus) >> 7) & 0xfffff;
		} else {
			offs = r1k->seq_tosof;
		}
	} else {
		offs = r1k->seq_tosram[r1k->seq_resolve_address];
	}

	offs ^= 0xfffff;
	offs &= 0xfffff;

	bool d7 = (r1k->seq_display & 0x8100) == 0;
	unsigned sgdisp = r1k->seq_display & 0xff;
	if (!d7)
		sgdisp |= 0x100;
	if (!((r1k->seq_resolve_address <= 0xd) && d7))
		sgdisp |= 0xffe00;

	bool acin = r1k->seq_mem_start & 1;

	switch(r1k->seq_mem_start) {
	case 0:
	case 2:
		r1k->seq_resolve_offset = offs + sgdisp + 1;
		r1k->seq_tmp_carry_out = (r1k->seq_resolve_offset >> 20) == 0;
		break;
	case 1:
	case 3:
		r1k->seq_resolve_offset = (1<<20) + offs - (sgdisp + 1);
		r1k->seq_tmp_carry_out = acin && (offs == 0);
		break;
	case 4:
	case 6:
		r1k->seq_resolve_offset = sgdisp ^ 0xfffff;
		// Carry is probably "undefined" here.
		break;
	case 5:
	case 7:
		r1k->seq_resolve_offset = offs;
		r1k->seq_tmp_carry_out = acin && (offs == 0);
		break;
	default:
		assert(0);
	}

	r1k->seq_resolve_offset &= 0xfffff;

	if (r1k->seq_intreads == 3) {
		r1k->seq_output_ob = r1k->seq_pred & 0xfffff;
	} else if (r1k->seq_intreads == 2) {
		r1k->seq_output_ob = r1k->seq_topcnt & 0xfffff;
	} else if (r1k->seq_intreads == 1) {
		r1k->seq_output_ob = r1k->seq_resolve_offset & 0xfffff;
	} else if (r1k->seq_intreads == 0) {
		r1k->seq_output_ob = r1k->seq_savrg & 0xfffff;
	} else {
		r1k->seq_output_ob = 0xfffff;
	}

	if (!r1k->seq_maybe_dispatch) {
		r1k->seq_name_bus = r1k->seq_namram[r1k->seq_resolve_address] ^ 0xffffffff;
	} else {
		r1k->seq_name_bus = 0xffffffff;
	}
}

static void
seq_h1(void)
{

	r1k->seq_urand = UIR_SEQ_URAND;
	r1k->seq_rndx = seq_pa048[r1k->seq_urand | (r1k->seq_bad_hint ? 0x100 : 0)] << 24;
	r1k->seq_rndx |= seq_pa046[r1k->seq_urand | (r1k->seq_bad_hint ? 0x100 : 0)] << 16;
	r1k->seq_rndx |=  seq_pa045[r1k->seq_urand | 0x100] << 8;
	r1k->seq_rndx |= seq_pa047[r1k->seq_urand | 0x100];

	r1k->seq_br_typ = UIR_SEQ_BRTYP;
	r1k->seq_br_typb = 1U << r1k->seq_br_typ;

	r1k->seq_maybe_dispatch = BRTYPE(A_DISPATCH);

	if (!r1k->seq_maybe_dispatch) {
		r1k->seq_mem_start = 7;
		r1k->seq_intreads = UIR_SEQ_IRD & 3;
	} else {
		r1k->seq_mem_start = r1k->seq_decode & 0x7;
		if (r1k->seq_mem_start == 0 || r1k->seq_mem_start == 4) {
			r1k->seq_intreads = 3;
		} else {
			r1k->seq_intreads = 1;
		}
	}

	if (mp_fiu_oe == 0x8)
		mp_fiu_bus = r1k->seq_topu;
	if (mp_tv_oe & SEQ_TV_OE) {
		seq_p1();
		r1k->seq_branch_offset = seq_branch_offset();
		seq_int_reads();	// Necessary
		mp_typ_bus = ~r1k->seq_typ_bus;
		mp_val_bus = ~r1k->seq_val_bus;
	}
}

/*
 * Seq schematic page 62:
 * BRANCH TIMING
 * ------ ------
 * 00 EARLY CONDITION
 * 01 LATCH CONDITION
 * 10 HINT TRUE (OR UNCONDITIONAL)
 * 11 HINT FALSE
 */

static void
seq_q1(void)
{

	r1k->seq_stop = !(!r1k->seq_bad_hint && (r1k->seq_uev == 16) && !r1k->seq_late_macro_event);
	bool evnan0d = !(UIR_SEQ_ENMIC && (r1k->seq_uev == 16));
	mp_uevent_enable = !(evnan0d || r1k->seq_stop);

	if (!(mp_tv_oe & SEQ_TV_OE)) {
		seq_p1();
		r1k->seq_branch_offset = seq_branch_offset();
		seq_int_reads();
	}
}

static void
seq_q3(void)
{
	// These are necessary for conditions
	r1k->seq_lxval = !((r1k->seq_lex_valid >> (15 - r1k->seq_resolve_address)) & 1);
	r1k->seq_m_res_ref = !(r1k->seq_lxval && !(r1k->seq_display >> 15));
	r1k->seq_field_number_error = (((r1k->seq_val_bus >> 39) ^ r1k->seq_curins) & 0x3ff) != 0x3ff;
	r1k->seq_tos_vld_cond = !(r1k->seq_foo7 || RNDX(RND_TOS_VLB));
	r1k->seq_m_tos_invld = !(r1k->seq_uses_tos && r1k->seq_tos_vld_cond);

	bool precond = seq_condition();
	r1k->seq_br_tim = UIR_SEQ_BRTIM;

	// SEQ micro arch doc, pg 29 says this can only be early cond, so there is no recursion on seq_m_ibuff_mt
	r1k->seq_cload = RNDX(RND_CIB_PC_L) && (!r1k->seq_bad_hint) && (!precond);

	r1k->seq_ibld = r1k->seq_cload || RNDX(RND_IBUFF_LD);
	r1k->seq_m_ibuff_mt = !(r1k->seq_ibuf_fill && r1k->seq_ibld && !(r1k->seq_macro_pc_offset & 7));

	r1k->seq_l_macro_hic = true;
	unsigned nua;

	if (r1k->seq_bad_hint) {
		unsigned adr = 0;
		if (r1k->seq_bad_hint) adr |= 0x01;
		adr |= (r1k->seq_br_typ << 1);
		if (r1k->seq_bhreg & 0x20) adr |= 0x20;
		if (r1k->seq_bhreg & 0x40) adr |= 0x80;
		if (r1k->seq_bhreg & 0x80) adr |= 0x100;
		unsigned rom = seq_pa043[adr];

		bool seq_uadr_mux = ((r1k->seq_bhreg) >> 5) & 1;
		r1k->seq_push_br = false;
		r1k->seq_push   = !(((rom >> 0) & 1) || !(((rom >> 2) & 1) || !seq_uadr_mux));
		r1k->seq_wanna_dispatch = !(((rom >> 5) & 1) && !seq_uadr_mux);
		r1k->seq_branch_offset = seq_branch_offset();
		r1k->seq_preturn = !(((rom >> 3) & 1) ||  seq_uadr_mux);
		nua = r1k->seq_other;
		mp_clock_stop_6 = true;
		r1k->seq_bad_hint_enable = true;
		mp_clock_stop_7 = false;
	} else if (r1k->seq_late_macro_event) {
		// Not tested by expmon_test_seq ?
		nua = 0x140 | ((r1k->seq_late_u ^ 0x7) << 3);
		r1k->seq_l_macro_hic = false;
		mp_clock_stop_6 = true;
		r1k->seq_bad_hint_enable = false;
		mp_clock_stop_7 = false;
	} else if (r1k->seq_uev != 16) {
		nua = 0x180 | (r1k->seq_uev << 3);
		mp_clock_stop_6 = false;
		r1k->seq_bad_hint_enable = false;
		mp_clock_stop_7 = true;
	} else {
		bool uadr_mux;
		if (BRTYPE(BRANCH_TRUE|BRANCH|CALL_TRUE|CALL|RETURN_FALSE|CASE_FALSE|DISPATCH_FALSE|CASE_CALL)) {
			switch (r1k->seq_br_tim) {
			case 0: uadr_mux = precond; break;
			case 1: uadr_mux = r1k->seq_latched_cond; break;
			case 2: uadr_mux = true; break;
			case 3: uadr_mux = false; break;
			default: assert(0);
			}
		} else { // BRANCH_FALSE|PUSH|CALL_FALSE|CONTINUE|RETURN_TRUE|RETURN|DISPATCH_TRUE|DISPATCH
			switch (r1k->seq_br_tim) {
			case 0: uadr_mux = !precond; break;
			case 1: uadr_mux = !r1k->seq_latched_cond; break;
			case 2: uadr_mux = false; break;
			case 3: uadr_mux = true; break;
			default: assert(0);
			}
		}
		r1k->seq_push_br = BRTYPE(PUSH);
		r1k->seq_push = !(BRTYPE(PUSH|CASE_CALL) || (BRTYPE(A_CALL) && uadr_mux));
		r1k->seq_wanna_dispatch = !(BRTYPE(A_DISPATCH) && !uadr_mux);
		r1k->seq_branch_offset = seq_branch_offset();
		r1k->seq_preturn = BRTYPE(A_RETURN) && !uadr_mux;
		unsigned one, two;
		if (BRTYPE(A_BRANCH|PUSH|A_CALL|CONTINUE)) {
			one = UIR_SEQ_BRN;
			two = mp_cur_uadr + 1;
		} else if (BRTYPE(A_RETURN)) {
			one = UIR_SEQ_BRN;
			two = (r1k->seq_topu ^ 0xffff) & 0x3fff;
		} else if (BRTYPE(A_DISPATCH)) {
			one = UIR_SEQ_BRN;
			two = (r1k->seq_uadr_decode >> 2) & ~1;
		} else { // CASE|CASE_CALL
			one = mp_cur_uadr + 1;
			two = UIR_SEQ_BRN + r1k->seq_fiu;
		}
		if (uadr_mux) {
			nua = one;
			r1k->seq_other = two;
		} else {
			nua = two;
			r1k->seq_other = one;
		}
		mp_clock_stop_6 = true;
		r1k->seq_bad_hint_enable = true;
		mp_clock_stop_7 = true;
	}

	if (!mp_sf_stop && mp_seq_prepped) {
		mp_nua_bus = nua & 0x3fff;
	}

	r1k->seq_check_exit_ue = !(mp_uevent_enable && RNDX(RND_CHK_EXIT) && r1k->seq_carry_out);
	r1k->seq_ferr = !(r1k->seq_field_number_error && !(RNDX(RND_FLD_CHK) || !mp_uevent_enable));
	r1k->seq_clock_stop_5 = (r1k->seq_check_exit_ue && r1k->seq_ferr);

	r1k->seq_ram[(r1k->seq_adr + 1) & 0xf] = r1k->seq_topu;

	seq_int_reads();

	r1k->seq_q3cond = precond;

	mp_state_clk_en = !(mp_state_clk_stop && mp_clock_stop_7);

	seq_q3clockstop();

	if (mp_mem_cond) {
		mp_mem_abort_e = true;
	} else if (mp_mem_cond_pol ^ r1k->seq_q3cond) {
		mp_mem_abort_e = true;
	} else {
		mp_mem_abort_e = false;
	}


	if (r1k->seq_wanna_dispatch) {
		r1k->seq_macro_event = 0;
		if (r1k->seq_stop || r1k->seq_maybe_dispatch)
			mp_mem_abort_e = false;
	} else if (r1k->seq_early_macro_pending) {
		r1k->seq_macro_event = 1;
		mp_mem_abort_e = false;
	} else {

		unsigned csa = mp_csa_nve;
		unsigned dec = r1k->seq_decode >> 3;

		r1k->seq_macro_event = 1;
		if (csa < (dec & 7)) {
			r1k->seq_late_macro_pending = 0;
			mp_mem_abort_e = false;
		} else if (csa > ((dec >> 3) | 12)) {
			r1k->seq_late_macro_pending = 1;
			mp_mem_abort_e = false;
		} else if (r1k->seq_stop) {
			r1k->seq_late_macro_pending = 2;
			mp_mem_abort_e = false;
		} else if (!r1k->seq_m_res_ref) {
			r1k->seq_late_macro_pending = 3;
			mp_mem_abort_e = false;
		} else if (!r1k->seq_m_tos_invld) {
			r1k->seq_late_macro_pending = 4;
			mp_mem_abort_e = false;
		} else if (r1k->seq_m_break_class) {
			r1k->seq_late_macro_pending = 6;
			mp_mem_abort_e = false;
		} else if (!r1k->seq_m_ibuff_mt) {
			r1k->seq_late_macro_pending = 7;
		} else {
			r1k->seq_macro_event = 0;
			r1k->seq_late_macro_pending = 8;
			if (((r1k->seq_decode & 0x7) == 4) || r1k->seq_stop)
				mp_mem_abort_e = false;
		}
	}

	if (RNDX(RND_TOS_VLB) && !r1k->seq_stop) {
		r1k->seq_tost = r1k->seq_typ_bus >> 32;
		r1k->seq_vost = r1k->seq_val_bus >> 32;
		r1k->seq_tosof = (r1k->seq_typ_bus >> 7) & 0xfffff;
	}
	if (r1k->seq_maybe_dispatch) {
		switch (r1k->seq_mem_start) {
		case 0:
		case 1:
		case 2:
			r1k->seq_name_bus = r1k->seq_namram[r1k->seq_resolve_address] ^ 0xffffffff;
			break;
		case 3:
		case 7:
			r1k->seq_name_bus = r1k->seq_tost ^ 0xffffffff;
			break;
		default:
			r1k->seq_name_bus = r1k->seq_vost ^ 0xffffffff;
			break;
		}
	} else {
		r1k->seq_name_bus = r1k->seq_namram[r1k->seq_resolve_address] ^ 0xffffffff;
	}
	if (!(r1k->seq_foo9 || mp_clock_stop_6)) {
		r1k->seq_treg = 0;
		r1k->seq_foo7 = false;
	}
	if (mp_adr_oe & 0x8) {
		unsigned pa040a = 0;
		pa040a |= (r1k->seq_decode & 0x7) << 6;
		if (r1k->seq_wanna_dispatch) pa040a |= 0x20;
		if (RNDX(RND_ADR_SEL)) pa040a |= 0x10;
		if (r1k->seq_resolve_address != 0xf) pa040a |= 0x08;
		if (r1k->seq_stop) pa040a |= 0x04;
		if (!r1k->seq_maybe_dispatch) pa040a |= 0x02;
		if (r1k->seq_bad_hint) pa040a |= 0x01;
		unsigned pa040d = seq_pa040[pa040a];

		if (r1k->seq_macro_event) {
			mp_spc_bus = 0x6;
		} else {
			mp_spc_bus = (pa040d >> 3) & 0x7;
		}
		bool adr_is_code = !((!r1k->seq_macro_event) && (pa040d & 0x01));
		bool resolve_drive;
		if (!r1k->seq_macro_event) {
			resolve_drive = !((pa040d >> 6) & 1);
		} else {
			resolve_drive = true;
		}
		if (!resolve_drive) {
			mp_adr_bus = r1k->seq_resolve_offset << 7;
		} else if (adr_is_code) {
			mp_adr_bus = (r1k->seq_code_offset >> 3) << 7;
		} else {
			mp_adr_bus = r1k->seq_output_ob << 7;
		}

		uint64_t branch = r1k->seq_branch_offset & 7;
		branch ^= 0x7;
		mp_adr_bus |= branch << 4;
		if (!adr_is_code) {
			mp_adr_bus |= r1k->seq_name_bus << 32;
		} else if (!(r1k->seq_urand & 0x2)) {
			mp_adr_bus |= r1k->seq_pcseg << 32;
		} else {
			mp_adr_bus |= r1k->seq_retseg << 32;
		}
	}
	bool bad_hint_disp = (!r1k->seq_bad_hint || (r1k->seq_bhreg & 0x08));
	mp_mem_abort_l = bad_hint_disp && !(RNDX(RND_L_ABRT) && !r1k->seq_stop);
}

static void
seq_q4(void)
{
	bool state_clock = r1k->seq_s_state_stop && !r1k->seq_stop;

	bool bhcke = r1k->seq_s_state_stop && mp_clock_stop_6 && (!r1k->seq_late_macro_event || r1k->seq_bad_hint);
	bool dispatch = r1k->seq_wanna_dispatch || r1k->seq_early_macro_pending || (r1k->seq_late_macro_pending != 8);

	if (state_clock && !dispatch) {
		Trace(trace_macro_prog,
		    "s %06jx o %05x d = %04x u = %04x c = %08jx",
		    (uintmax_t)r1k->seq_pcseg,
		    0x7fff ^ r1k->seq_macro_pc_offset,
		    0xffff ^ r1k->seq_display,
		    mp_cur_uadr,
		    (uintmax_t)(r1k->seq_cur_name ^ 0xffffffff)
		);
	}

	bool update_display = false;
	if (state_clock) {
		seq_nxt_lex_valid();
		if (!RNDX(RND_RES_OFFS)) {
			r1k->seq_tosram[r1k->seq_resolve_address] = (r1k->seq_typ_bus >> 7) & 0xfffff;
		}
		if (!r1k->seq_ibld) {
			r1k->seq_macro_ins_typ = r1k->seq_typ_bus;
			r1k->seq_macro_ins_val = r1k->seq_val_bus;
			update_display = true;
		}
		if (!RNDX(RND_RETRN_LD)) {
			r1k->seq_retrn_pc_ofs = r1k->seq_macro_pc_offset;
		}
		if (!RNDX(RND_CUR_LEX)) {
			r1k->seq_curr_lex = r1k->seq_val_bus & 0xf;
			r1k->seq_curr_lex ^= 0xf;
		}
	}
	if (!mp_sf_stop) {
		r1k->seq_late_macro_event = state_clock && r1k->seq_macro_event && !r1k->seq_early_macro_pending;

		mp_seq_halted |= state_clock && !RNDX(RND_HALT);
		if (mp_seq_halted)
			printf("SEQ HALTED\n");

		r1k->seq_early_macro_pending = mp_macro_event != 0;
		r1k->seq_emac = mp_macro_event ^ 0x7f;
		if (r1k->seq_early_macro_pending) {
			r1k->seq_uadr_decode = 0x0400 + 0x20 * fls(mp_macro_event);
		}
	}

	if (bhcke && !r1k->seq_macro_event) {
		unsigned mode = 0;
		if (!r1k->seq_wanna_dispatch) {
			mode = 1;
		} else if (r1k->seq_cload) {
			mode = 0;
		} else {
			if (!r1k->seq_bad_hint) {
				if (RNDX(RND_M_PC_MD0))
					mode |= 2;
			} else if (!((r1k->seq_bhreg >> 2) & 1)) {
				mode |= 2;
			}

			if (RNDX(RND_M_PC_MD1)) mode |= 1;
		}
		if (mode == 3) {
			if (!RNDX(RND_M_PC_MUX)) {
				r1k->seq_macro_pc_offset = r1k->seq_val_bus >> 4;
			} else {
				r1k->seq_macro_pc_offset = r1k->seq_branch_offset;
			}
		} else if (mode == 2) {
			r1k->seq_macro_pc_offset += 1;
		} else if (mode == 1) {
			r1k->seq_macro_pc_offset += 0x7fff;
		}
		if (mode != 0) {
			update_display = true;
			r1k->seq_macro_pc_offset &= 0x7fff;
		}
	}

	bool crnana = !(RNDX(RND_INSTR_LD) && dispatch);

	if (state_clock) {
		unsigned dsp = 0;
		if (!RNDX(RND_INSTR_MX)) {
			dsp = r1k->seq_display;
		} else {
			dsp = r1k->seq_val_bus & 0xffff;
		}
		dsp ^= 0xffff;

		if (crnana && r1k->seq_topbot)
			r1k->seq_ctop = dsp;
		if (crnana && !r1k->seq_topbot)
			r1k->seq_cbot = dsp;
		if (!RNDX(RND_BR_MSK_L)) {
			r1k->seq_break_mask = (r1k->seq_val_bus >> 16) & 0x7fff;
		}

		if (!RNDX(RND_NAME_LD)) {
			r1k->seq_cur_name = r1k->seq_typ_bus >> 32;
		}

		if (!RNDX(RND_RES_NAME)) {
			r1k->seq_namram[r1k->seq_resolve_address] = r1k->seq_typ_bus >> 32;
		}

		if (!RNDX(RND_RETRN_LD)) {
			r1k->seq_retseg = r1k->seq_pcseg;
		}
		if (!RNDX(RND_M_PC_LDH)) {
			r1k->seq_pcseg = (~r1k->seq_val_bus >> 32) & 0xffffff;
		}
		if (!RNDX(RND_SAVE_LD)) {
			r1k->seq_savrg = r1k->seq_resolve_offset;
			r1k->seq_carry_out = r1k->seq_tmp_carry_out;
		}

		if (!RNDX(RND_PRED_LD)) {
			if (!RNDX(RND_CNTL_MUX)) {
				r1k->seq_pred = ((~r1k->seq_typ_bus) >> 7) & 0xfffff;
			} else {
				r1k->seq_pred = (mp_fiu_bus >> 7) & 0xfffff;
			}
		}

		if (!RNDX(RND_TOP_LD)) {
			if (!RNDX(RND_CNTL_MUX)) {
				r1k->seq_topcnt = ((~r1k->seq_typ_bus) >> 7) & 0xfffff;
			} else {
				r1k->seq_topcnt = (mp_fiu_bus >> 7) & 0xfffff;
			}
		} else if (mp_csa_cntl == 2) {
			r1k->seq_topcnt += 1;
		} else if (mp_csa_cntl == 3) {
			r1k->seq_topcnt += 0xfffff;
		}
		r1k->seq_topcnt &= 0xfffff;
	}

	if (bhcke) {
		if (crnana) {
			r1k->seq_topbot = !r1k->seq_topbot;
		} else if (r1k->seq_bad_hint && !(r1k->seq_bhreg & 0x04)) {
			r1k->seq_topbot = !r1k->seq_topbot;
		}

		if (r1k->seq_topbot) {
			r1k->seq_curins = r1k->seq_cbot;
		} else {
			r1k->seq_curins = r1k->seq_ctop;
		}

		unsigned ccl;
		if (r1k->seq_curins & 0xfc00) {
			ccl = (r1k->seq_top[r1k->seq_curins >> 6] >> 4) & 0xf;
		} else {
			ccl = (r1k->seq_bot[r1k->seq_curins & 0x3ff] >> 4) & 0xf;
		}

		if (ccl == 0) {
			r1k->seq_m_break_class = false;
		} else {
			r1k->seq_m_break_class = (r1k->seq_break_mask >> (15 - ccl)) & 1;
		}
	}

	if (r1k->seq_s_state_stop && r1k->seq_l_macro_hic) {
		bool xwrite;
		bool pop;
		unsigned stkinpsel = 0;
		if (!mp_clock_stop_6) {
			xwrite = true;
			pop = true;
			stkinpsel = 3;
		} else if (!r1k->seq_push) {
			xwrite = true;
			pop = false;
			if (!r1k->seq_push_br) stkinpsel |= 2;
			if (r1k->seq_bad_hint) stkinpsel |= 1;
		} else {
			xwrite = !RNDX(RND_PUSH);
			pop = r1k->seq_preturn || RNDX(RND_POP);
			stkinpsel = 0x1;
		}

		if (xwrite) {
			switch(stkinpsel) {
			case 0:
				r1k->seq_topu = UIR_SEQ_BRN;
				if (r1k->seq_q3cond) r1k->seq_topu |= (1<<15);
				if (r1k->seq_latched_cond) r1k->seq_topu |= (1<<14);
				r1k->seq_topu ^= 0xffff;
				break;
			case 1:
				r1k->seq_topu = mp_fiu_bus & 0xffff;
				break;
			case 2:
				r1k->seq_topu = mp_cur_uadr;
				if (r1k->seq_q3cond) r1k->seq_topu |= (1<<15);
				if (r1k->seq_latched_cond) r1k->seq_topu |= (1<<14);
				r1k->seq_topu += 1;
				r1k->seq_topu ^= 0xffff;
				break;
			case 3:
				r1k->seq_topu = mp_cur_uadr;
				if (r1k->seq_q3cond) r1k->seq_topu |= (1<<15);
				if (r1k->seq_latched_cond) r1k->seq_topu |= (1<<14);
				r1k->seq_topu ^= 0xffff;
				break;
			default: assert(0);
			}
		} else if (pop) {
			r1k->seq_topu = r1k->seq_ram[r1k->seq_adr];
		}
		r1k->seq_saved_latched = !((r1k->seq_topu >> 14) & 0x1);

		if (RNDX(RND_CLEAR_ST) && !r1k->seq_stop) {
			r1k->seq_adr = xwrite;
		} else if (xwrite || pop) {
			if (xwrite) {
				r1k->seq_adr = (r1k->seq_adr + 1) & 0xf;
			} else {
				r1k->seq_adr = (r1k->seq_adr + 0xf) & 0xf;
			}
		}
		r1k->seq_stack_size_zero = r1k->seq_adr == 0;
	}

	if (state_clock) {
		r1k->seq_fiu = mp_fiu_bus;
		r1k->seq_fiu &= 0x3fff;
	}

	if (!mp_sf_stop) {
		if (!r1k->seq_maybe_dispatch) {
			r1k->seq_late_u = 7;
		} else {
			r1k->seq_late_u = r1k->seq_late_macro_pending;
			if (r1k->seq_late_u == 8)
				r1k->seq_late_u = 7;
		}

		mp_seq_uev &= ~(UEV_CK_EXIT|UEV_FLD_ERR|UEV_NEW_PAK);
		if (!r1k->seq_check_exit_ue) {
			mp_seq_uev |= UEV_CK_EXIT;
		}
		if (!r1k->seq_ferr) {
			mp_seq_uev |= UEV_FLD_ERR;
		}
		if (!r1k->seq_clock_stop_1) {
			mp_seq_uev |= UEV_NEW_PAK;
		}

		r1k->seq_uev = 16 - fls(mp_seq_uev);

		if (r1k->seq_s_state_stop) {
			mp_cur_uadr = mp_nua_bus;
		}

		if (bhcke) {
			unsigned adr = 0;
			if (mp_clock_stop_6)
				adr |= 0x02;
			if (!r1k->seq_macro_event)
				adr |= 0x04;
			adr |= r1k->seq_br_tim << 3;
			adr |= r1k->seq_br_typ << 5;
			r1k->seq_bhreg = seq_pa044[adr];

			if (!state_clock) {
				r1k->seq_bhreg |= 0x2;
			} else {
				r1k->seq_bhreg ^= 0x2;
			}
		}

		r1k->seq_hint_last = (r1k->seq_bhreg >> 1) & 1;
		r1k->seq_hint_t_last = (r1k->seq_bhreg >> 0) & 1;

		bool bad_hint_disp = (!r1k->seq_bad_hint || (r1k->seq_bhreg & 0x08));
		if (r1k->seq_s_state_stop && r1k->seq_bad_hint_enable && bad_hint_disp) {
			unsigned restrt_rnd = 0;
			restrt_rnd |= RNDX(RND_RESTRT0) ? 2 : 0;
			restrt_rnd |= RNDX(RND_RESTRT1) ? 1 : 0;
			if (!r1k->seq_wanna_dispatch) {
				r1k->seq_rreg = 0xa;
			} else if (restrt_rnd != 0) {
				r1k->seq_rreg = (restrt_rnd & 0x3) << 1;
			} else {
				r1k->seq_rreg &= 0xa;
			}
			if (r1k->seq_macro_event) {
				r1k->seq_rreg &= ~0x2;
			}
			r1k->seq_treg = 0x3;
			bool dnan0d = !(dispatch && RNDX(RND_PRED_LD));
			bool tsnor0b = !(dnan0d || r1k->seq_tos_vld_cond);
			if (tsnor0b)
				r1k->seq_treg |= 0x8;
			if (!r1k->seq_tos_vld_cond)
				r1k->seq_treg |= 0x4;
		} else if (r1k->seq_s_state_stop && r1k->seq_bad_hint_enable) {
			r1k->seq_rreg <<= 1;
			r1k->seq_rreg &= 0xe;
			r1k->seq_rreg |= 0x1;
			r1k->seq_treg <<= 1;
			r1k->seq_treg &= 0xe;
			r1k->seq_treg |= 0x1;
		}
		r1k->seq_rq = r1k->seq_rreg;
		r1k->seq_foo7 = r1k->seq_treg >> 3;

		if (state_clock) {
			unsigned condsel = UIR_SEQ_CSEL;
			uint8_t pa042 = seq_pa042[condsel << 2];
			bool is_e_ml = (pa042 >> 7) & 1;
			r1k->seq_lreg = 0;
			r1k->seq_lreg |= r1k->seq_latched_cond << 3;
			r1k->seq_lreg |= is_e_ml << 2;
			r1k->seq_lreg |= UIR_SEQ_LUIR << 1;
			r1k->seq_lreg |= r1k->seq_q3cond << 0;

			if (r1k->seq_lreg & 0x4) {
				r1k->seq_last_late_cond = r1k->seq_q3cond;
			}

			switch(r1k->seq_lreg & 0x6) {
			case 0x0:
			case 0x4:
				r1k->seq_latched_cond = (r1k->seq_lreg >> 3) & 1;
				break;
			case 0x2:
				r1k->seq_latched_cond = (r1k->seq_lreg >> 0) & 1;
				break;
			case 0x6:
				r1k->seq_latched_cond = r1k->seq_last_late_cond;
				break;
			default:
				assert(0);
			}
			r1k->seq_n_in_csa = mp_csa_nve;
			r1k->seq_foo9 = !RNDX(RND_TOS_VLB);
		}
	}

	bool last_cond_late = (r1k->seq_lreg >> 2) & 1;
	if (r1k->seq_hint_last) {
		r1k->seq_bad_hint = false;
	} else if (!last_cond_late && !r1k->seq_hint_t_last) {
		r1k->seq_bad_hint = r1k->seq_lreg & 1;
	} else if (!last_cond_late &&  r1k->seq_hint_t_last) {
		r1k->seq_bad_hint = !(r1k->seq_lreg & 1);
	} else if ( last_cond_late && !r1k->seq_hint_t_last) {
		r1k->seq_bad_hint = r1k->seq_last_late_cond;
	} else if ( last_cond_late &&  r1k->seq_hint_t_last) {
		r1k->seq_bad_hint = !r1k->seq_last_late_cond;
	}

	if (update_display) {
		switch(r1k->seq_macro_pc_offset & 7) {
		case 0x0: r1k->seq_display = r1k->seq_macro_ins_val >>  0; break;
		case 0x1: r1k->seq_display = r1k->seq_macro_ins_val >> 16; break;
		case 0x2: r1k->seq_display = r1k->seq_macro_ins_val >> 32; break;
		case 0x3: r1k->seq_display = r1k->seq_macro_ins_val >> 48; break;
		case 0x4: r1k->seq_display = r1k->seq_macro_ins_typ >>  0; break;
		case 0x5: r1k->seq_display = r1k->seq_macro_ins_typ >> 16; break;
		case 0x6: r1k->seq_display = r1k->seq_macro_ins_typ >> 32; break;
		case 0x7: r1k->seq_display = r1k->seq_macro_ins_typ >> 48; break;
		default: assert(0);
		}
		r1k->seq_display &= 0xffff;
		if ((r1k->seq_display >> 10) != 0x3f) {
			r1k->seq_decram = r1k->seq_top[(r1k->seq_display ^ 0xffff) >> 6];
		} else {
			r1k->seq_decram = r1k->seq_bot[(r1k->seq_display ^ 0xffff) & 0x3ff];
		}
	}

	if (!r1k->seq_early_macro_pending) {
		r1k->seq_uadr_decode = (r1k->seq_decram >> 16);
		r1k->seq_decode = (r1k->seq_decram >> 8) & 0xff;
		r1k->seq_uses_tos = (r1k->seq_uadr_decode >> 2) & 1;
		r1k->seq_ibuf_fill = (r1k->seq_uadr_decode >> 1) & 1;
	}

	mp_clock_stop_7 = !r1k->seq_bad_hint && r1k->seq_l_macro_hic;
	mp_state_clk_en = !(mp_state_clk_stop && mp_clock_stop_7);
	if (!mp_sf_stop && mp_seq_prepped) {
		r1k->seq_uir = r1k->seq_wcsram[mp_nua_bus] ^ (0x7fULL << 13);	// Invert condsel
		mp_nxt_cond_sel = UIR_SEQ_CSEL;
	}
}

// -------------------- TYP --------------------

static bool
typ_bin_op_pass(void)
{
	bool dp = !(TYP_A_BIT(35) && TYP_B_BIT(35));
	bool abim = !(!(TYP_A_BITS(31) == r1k->typ_ofreg) | dp);
	bool bbim = !(!(TYP_B_BITS(31) == r1k->typ_ofreg) | dp);

	return (!(
		(abim && bbim) ||
		(bbim && TYP_A_BIT(34)) ||
		(abim && TYP_B_BIT(34)) ||
		(TYP_A_BIT(34) && TYP_A_BIT(35) && TYP_B_BIT(34) && TYP_B_BIT(35))
	));
}

static bool
typ_priv_path_eq(void)
{
	return (!(
		(TYP_A_BITS(31) == TYP_B_BITS(31)) &&
		((TYP_A_BITS(56) & 0xfffff) == (TYP_B_BITS(56) & 0xfffff))
	));
}

static bool
typ_a_op_pass(void)
{
	return (!(TYP_A_BIT(35) && ((TYP_A_BITS(31) == r1k->typ_ofreg) || TYP_A_BIT(34))));
}

static bool
typ_b_op_pass(void)
{
	return (!(TYP_B_BIT(35) && ((TYP_B_BITS(31) == r1k->typ_ofreg) || TYP_B_BIT(34))));
}

static bool
typ_clev(void)
{
	return (!(
		((r1k->typ_rand == 0x4) && (TYP_A_LIT() == UIR_TYP_CLIT)) ||
		((r1k->typ_rand == 0x6) && (TYP_A_LIT() == TYP_B_LIT())) ||
		((r1k->typ_rand == 0x5) && (TYP_B_LIT() == UIR_TYP_CLIT)) ||
		((r1k->typ_rand == 0x7) && (TYP_A_LIT() == TYP_B_LIT()) && (TYP_B_LIT() == UIR_TYP_CLIT))
	));
}

static bool
typ_cond(void)
{

	unsigned condsel = mp_cond_sel;

	if ((condsel >> 3) == 0xb)
		condsel &= ~0x40;

	switch(condsel) {
	case 0x18:	// L - TYP_ALU_ZERO
		r1k->typ_cond = (r1k->typ_nalu != 0);
		break;
	case 0x19:	// L - TYP_ALU_NONZERO
		r1k->typ_cond = (r1k->typ_nalu == 0);
		break;
	case 0x1a:	// L - TYP_ALU_A_GT_OR_GE_B
		{
		bool ovrsign = (!(((TYP_A_BIT(0) != TYP_B_BIT(0)) && r1k->typ_is_binary) || (!r1k->typ_is_binary && !TYP_A_BIT(0))));
		r1k->typ_cond = (!(
		    ((TYP_A_BIT(0) != TYP_B_BIT(0)) && TYP_A_BIT(0)) ||
		    (r1k->typ_coh && (ovrsign ^ r1k->typ_sub_else_add))
		));
		}
		break;
	case 0x1b:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x1c:	// E - TYP_LOOP_COUNTER_ZERO
		r1k->typ_cond = (r1k->typ_count != 0x3ff);
		break;
	case 0x1d:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x1e:	// L - TYP_ALU_ZERO - COMBO with VAL_ALU_NONZERO
		r1k->typ_cond = (r1k->typ_nalu != 0);
		break;
	case 0x1f:	// L - TYP_ALU_32_CO - ALU 32 BIT CARRY OUT
		r1k->typ_cond = (r1k->typ_com);
		break;
	case 0x20:	// L - TYP_ALU_CARRY
		r1k->typ_cond = (!r1k->typ_coh);
		break;
	case 0x21:	// L - TYP_ALU_OVERFLOW
		{
		bool ovrsign = (!(((TYP_A_BIT(0) != TYP_B_BIT(0)) && r1k->typ_is_binary) || (!r1k->typ_is_binary && !TYP_A_BIT(0))));
		r1k->typ_cond = (r1k->typ_ovr_en || (
		    r1k->typ_coh ^ r1k->typ_almsb ^ r1k->typ_sub_else_add ^ ovrsign
		));
		}
		break;
	case 0x22:	// L - TYP_ALU_LT_ZERO
		r1k->typ_cond = (r1k->typ_almsb);
		break;
	case 0x23:	// L - TYP_ALU_LE_ZERO
		r1k->typ_cond = (!(r1k->typ_almsb && (r1k->typ_nalu != 0)));
		break;
	case 0x24:	// ML - TYP_SIGN_BITS_EQUAL
		r1k->typ_cond = ((TYP_A_BIT(0) != TYP_B_BIT(0)));
		break;
	case 0x25:	// E - TYP_FALSE
		r1k->typ_cond = (true);
		break;
	case 0x26:	// E - TYP_TRUE
		r1k->typ_cond = (false);
		break;
	case 0x27:	// E - TYP_PREVIOUS
		r1k->typ_cond = (r1k->typ_last_cond);
		break;
	case 0x28:	// ML - OF_KIND_MATCH
		{
		unsigned mask_a = typ_pa059[UIR_TYP_CLIT] >> 1;
		unsigned okpat_a = typ_pa059[UIR_TYP_CLIT + 256] >> 1;
		bool oka = (0x7f ^ (mask_a & TYP_B_LIT())) != okpat_a; // XXX r1k->typ_b ??

		unsigned mask_b = typ_pa059[UIR_TYP_CLIT + 128] >> 1;
		unsigned okpat_b = typ_pa059[UIR_TYP_CLIT + 384] >> 1;
		bool okb = (0x7f ^ (mask_b & TYP_B_LIT())) != okpat_b;

		bool okm = !(oka & okb);
		r1k->typ_cond = (okm);
		}
		break;
	case 0x29:	// ML - CLASS_A_EQ_LIT
		r1k->typ_cond = (TYP_A_LIT() != UIR_TYP_CLIT);
		break;
	case 0x2a:	// ML - CLASS_B_EQ_LIT
		r1k->typ_cond = (TYP_B_LIT() != UIR_TYP_CLIT);
		break;
	case 0x2b:	// ML - CLASS_A_EQ_B
		r1k->typ_cond = (TYP_A_LIT() != TYP_B_LIT());
		break;
	case 0x2c:	// ML - CLASS_A_B_EQ_LIT
		r1k->typ_cond = (!(TYP_A_LIT() != UIR_TYP_CLIT) || (TYP_B_LIT() != UIR_TYP_CLIT));
		break;
	case 0x2d:	// E - PRIVACY_A_OP_PASS
		r1k->typ_cond = (typ_a_op_pass());
		break;
	case 0x2e:	// ML - PRIVACY_B_OP_PASS
		r1k->typ_cond = (typ_b_op_pass());
		break;
	case 0x2f:	// ML - PRIVACY_BIN_EQ_PASS
		r1k->typ_cond = (typ_priv_path_eq() && typ_bin_op_pass());
		break;
	case 0x30:	// ML - PRIVACY_BIN_OP_PASS
		r1k->typ_cond = (typ_bin_op_pass());
		break;
	case 0x31:	// ML - PRIVACY_NAMES_EQ
		r1k->typ_cond = (TYP_A_BITS(31) == TYP_B_BITS(31));
		break;
	case 0x32:	// ML - PRIVACY_PATHS_EQ
		r1k->typ_cond = (typ_priv_path_eq());
		break;
	case 0x33:	// ML - PRIVACY_STRUCTURE
		r1k->typ_cond = (!(typ_bin_op_pass() || typ_priv_path_eq()));
		break;
	case 0x34:	// E - PASS_PRIVACY_BIT
		r1k->typ_cond = (r1k->typ_pass_priv);
		break;
	case 0x35:	// ML - B_BUS_BIT_32
		r1k->typ_cond = (TYP_B_BIT(32));
		break;
	case 0x36:	// ML - B_BUS_BIT_33
		r1k->typ_cond = (TYP_B_BIT(33));
		break;
	case 0x37:	// ML - B_BUS_BIT_34
		r1k->typ_cond = (TYP_B_BIT(34));
		break;
	case 0x38:	// ML - B_BUS_BIT_35
		r1k->typ_cond = (TYP_B_BIT(35));
		break;
	case 0x39:	// ML - B_BUS_BIT_36
		r1k->typ_cond = (TYP_B_BIT(36));
		break;
	case 0x3a:	// ML - B_BUS_BIT_33_34_OR_36
		r1k->typ_cond = ((TYP_B_BITS(36) & 0xd) != 0xd);
		break;
	case 0x3b:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x3c:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x3d:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x3e:	// SPARE
		r1k->typ_cond = (true);
		break;
	case 0x3f:	// ML - B_BUS_BIT_21
		r1k->typ_cond = (TYP_B_BIT(21));
		break;
	default: assert(0);
	}
	return (!r1k->typ_cond);
}


static void
typ_h1(void)
{
	r1k->typ_rand = UIR_TYP_RAND;

	unsigned marctl = UIR_TYP_MCTL;

	if (mp_fiu_oe == 0x4) {
		r1k->typ_a = tv_find_ab(UIR_TYP_A, UIR_TYP_FRM, true, true, r1k->typ_rfram);
		mp_fiu_bus = ~r1k->typ_a;
	}
	if (mp_tv_oe & TYP_T_OE) {
		r1k->typ_b = tv_find_ab(UIR_TYP_B, UIR_TYP_FRM, false, true, r1k->typ_rfram);
		mp_typ_bus = ~r1k->typ_b;
	}

	if (mp_adr_oe & 0x6) {
		if (marctl & 0x8) {
			mp_spc_bus = (marctl & 0x7) ^ 0x7;
		} else {
			r1k->typ_b = tv_find_ab(UIR_TYP_B, UIR_TYP_FRM, false, true, r1k->typ_rfram);
			mp_spc_bus = (r1k->typ_b & 0x7) ^ 0x7;
		}
	}
}

static void
typ_q2(void)
{

	unsigned priv_check = UIR_TYP_UPVC;
	if (mp_fiu_oe != 0x4) {
		r1k->typ_a = tv_find_ab(UIR_TYP_A, UIR_TYP_FRM, true, true, r1k->typ_rfram);
	}
	if (!(mp_tv_oe & TYP_T_OE)) {
		r1k->typ_b = tv_find_ab(UIR_TYP_B, UIR_TYP_FRM, false, true, r1k->typ_rfram);
	}

	bool divide = r1k->typ_rand != 0xb;
	bool acond = true;
	if (divide && r1k->typ_last_cond)
		acond = false;
	if (!divide && mp_q_bit)
		acond = false;
	unsigned tmp, idx, alurand, alufunc = UIR_TYP_AFNC;

	if (r1k->typ_rand < 8) {
		alurand = 7;
	} else {
		alurand = 15 - r1k->typ_rand;
	}
	idx = acond << 8;
	idx |= alurand << 5;
	idx |= alufunc;

	tmp = typ_pa068[idx];
	r1k->typ_is_binary = (tmp >> 1) & 1;

	if (r1k->typ_rand != 0xf) {
		F181_ALU(tmp, r1k->typ_a, r1k->typ_b, ((tmp >> 2) & 1), r1k->typ_nalu, r1k->typ_com);
	} else {
		if (tmp >= 0xf0) {
			r1k->typ_nalu = ~(r1k->typ_a + 0x80ULL);
			r1k->typ_com = ((r1k->typ_nalu ^ r1k->typ_a) & 0x80000000) != 0;
		} else {
			r1k->typ_nalu = ~(r1k->typ_a - 0x80ULL);
			r1k->typ_com = ((r1k->typ_nalu ^ r1k->typ_a) & 0x80000000) == 0;
		}
		r1k->typ_nalu &= 0xffffffffULL;
	}

	tmp = tv_pa010[idx];
	r1k->typ_sub_else_add = (tmp >> 2) & 1;
	r1k->typ_ovr_en = (tmp >> 1) & 1;

	uint32_t o;
	F181_ALU(tmp, r1k->typ_a >> 32, r1k->typ_b >> 32, r1k->typ_com, o, r1k->typ_coh);
	r1k->typ_nalu |= ((uint64_t)o) << 32;
	r1k->typ_alu = ~r1k->typ_nalu;
	r1k->typ_almsb = r1k->typ_alu >> 63ULL;

	if (mp_adr_oe & 0x4) {
		uint64_t alu = r1k->typ_alu;
		unsigned spc = mp_spc_bus;
		if (spc != 4) {
			alu |=0xf8000000ULL;
		}
		mp_adr_bus = ~alu;
	}

	bool micros_en = mp_uevent_enable;
	mp_clock_stop_3 = true;
	mp_clock_stop_4 = true;
	unsigned selcond = 0x00;
	if (r1k->typ_pass_priv) {
		selcond = 0x80 >> priv_check;
	}
#define TYP_UEV (UEV_CLASS|UEV_BIN_EQ|UEV_BIN_OP|UEV_TOS_OP|UEV_TOS1_OP|UEV_CHK_SYS)
	mp_seq_uev &= ~TYP_UEV;
	if (micros_en) {
		if (selcond == 0x40 && typ_bin_op_pass()) {
			mp_seq_uev |= UEV_BIN_OP;
		}
		if (selcond == 0x80 && typ_priv_path_eq() && typ_bin_op_pass()) {
			mp_seq_uev |= UEV_BIN_EQ;
			mp_clock_stop_3 = false;
		}
		if ((0x3 < r1k->typ_rand && r1k->typ_rand < 0x8) && typ_clev()) {
			mp_seq_uev |= UEV_CLASS;
			mp_clock_stop_3 = false;
		}
		if ((selcond == 0x10 && typ_a_op_pass()) || (selcond == 0x04 && typ_b_op_pass())) {
			mp_seq_uev |= UEV_TOS1_OP;
		}
		if ((selcond == 0x20 && typ_a_op_pass()) || (selcond == 0x08 && typ_b_op_pass())) {
			mp_seq_uev |= UEV_TOS_OP;
		}
		if ((r1k->typ_rand == 0xe) && (TYP_B_LIT() != UIR_TYP_CLIT)) {
			mp_seq_uev |= UEV_CHK_SYS;
			mp_clock_stop_3 = false;
		}
	}

	if (selcond == 0x40 && typ_bin_op_pass()) {
		mp_clock_stop_4 = false;
	}

	if ((selcond & 0x30) && typ_a_op_pass()) {
		mp_clock_stop_4 = false;
	}

	if ((selcond & 0x0c) && typ_b_op_pass()) {
		mp_clock_stop_4 = false;
	}

	unsigned marctl = UIR_TYP_MCTL;
	if ((mp_adr_oe & 0x6) && marctl < 0x8) {	// XXX: && ?
		mp_spc_bus = (r1k->typ_b & 0x7) ^ 0x7;
		// XXX: when 4, possible race against address bus truncation in TYP or VAL
	}
}

static void
typ_q4(void)
{
	uint64_t c = 0;
	unsigned priv_check = UIR_TYP_UPVC;

	if (mp_ram_stop && !mp_freeze) {

		bool c_source = UIR_TYP_CSRC;
		bool fiu0, fiu1;
		fiu0 = c_source;
		fiu1 = c_source == (r1k->typ_rand != 0x3);

		bool sel = UIR_TYP_SEL;

		if (!fiu0) {
			c |= ~mp_fiu_bus & 0xffffffff00000000ULL;
		} else {
			if (sel) {
				c |= r1k->typ_wdr & 0xffffffff00000000ULL;
			} else {
				c |= r1k->typ_alu & 0xffffffff00000000ULL;
			}
		}
		if (!fiu1) {
			c |= ~mp_fiu_bus & 0xffffffffULL;
		} else {
			if (sel) {
				c |= r1k->typ_wdr & 0xffffffffULL;
			} else {
				c |= r1k->typ_alu & 0xffffffffULL;
			}
		}

		unsigned cadr = tv_cadr(UIR_TYP_C, UIR_TYP_FRM, r1k->typ_count);
		if (cadr < 0x400)
			r1k->typ_rfram[cadr] = ~c;

		if (mp_clock_stop) {
			if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
				r1k->typ_wdr = ~mp_typ_bus;
			}
			if (UIR_TYP_C == 0x28) {
				r1k->typ_count = c;
				r1k->typ_count &= 0x3ff;
			} else if (r1k->typ_rand == 0x2) {
				r1k->typ_count += 1;
				r1k->typ_count &= 0x3ff;
			} else if (r1k->typ_rand == 0x1) {
				r1k->typ_count += 0x3ff;
				r1k->typ_count &= 0x3ff;
			}

			r1k->typ_last_cond = r1k->typ_cond;
			if (r1k->typ_rand == 0xc) {
				r1k->typ_ofreg = r1k->typ_b >> 32;
			}

			if (priv_check != 7) {
				r1k->typ_pass_priv = r1k->typ_rand != 0xd;
			}
		}
	}
	if (!mp_sf_stop) {
		r1k->typ_uir = r1k->typ_wcsram[mp_nua_bus] ^ 0x7fffc0000000ULL;
		mp_nxt_mar_cntl = UIR_TYP_MCTL;
		mp_nxt_csa_cntl = UIR_TYP_CCTL;
		mp_nxt_csa_offset = mp_csa_this_offs;
		mp_nxt_csa_write_enable = !(mp_csa_hit || mp_csa_wr);
	}
}

// -------------------- VAL --------------------

static bool
val_ovrsgn(void)
{
	bool a0 = r1k->val_amsb;
	bool b0 = r1k->val_bmsb;
	bool se = r1k->val_isbin;
	return (!(
		(se && (a0 ^ b0)) ||
		(!se && !a0)
	));
}

static bool
val_cond(void)
{
	unsigned csel = mp_cond_sel;
	if ((csel & 0x78) == 0x58)
		csel ^= 0x58;
	switch(csel) {
	case 0x00:	// L VAL_ALU_ZERO
		r1k->val_thiscond = (r1k->val_nalu != 0);
		break;
	case 0x01:	// L VAL_ALU_NONZERO
		r1k->val_thiscond = (r1k->val_nalu == 0);
		break;
	case 0x02:	// L VAL_ALU_A_LT_OR_LE_B
		r1k->val_thiscond = !(
			(r1k->val_bmsb && (r1k->val_amsb ^ r1k->val_bmsb)) ||
			(!r1k->val_coh && (val_ovrsgn() ^ r1k->val_sub_else_add))
		);
		break;
	case 0x03:	// SPARE
		r1k->val_thiscond = true;
		break;
	case 0x04:	// E VAL_LOOP_COUNTER_ZERO
		r1k->val_thiscond = r1k->val_count != 0x3ff;
		break;
	case 0x05:	// SPARE
		r1k->val_thiscond = true;
		break;
	case 0x06:	// L VAL_ALU_NONZERO
		r1k->val_thiscond = (r1k->val_nalu == 0);
		break;
	case 0x07:	// L VAL_ALU_32_CO
		r1k->val_thiscond = r1k->val_carry_middle;
		break;
	case 0x08:	// L VAL_ALU_CARRY
		r1k->val_thiscond = !r1k->val_coh;
		break;
	case 0x09:	// L VAL_ALU_OVERFLOW
		r1k->val_thiscond = r1k->val_ovren || (val_ovrsgn() ^ r1k->val_sub_else_add ^ r1k->val_coh ^ r1k->val_cmsb);
		break;
	case 0x0a:	// L VAL_ALU_LT_ZERO
		r1k->val_thiscond = r1k->val_cmsb;
		break;
	case 0x0b:	// L VAL_ALU_LE_ZERO
		r1k->val_thiscond = !r1k->val_cmsb || (r1k->val_nalu == 0);
		break;
	case 0x0c:	// ML VAL_SIGN_BITS_EQUAL
		r1k->val_thiscond = (r1k->val_amsb ^ r1k->val_bmsb);
		break;
	case 0x0d:	// SPARE
		r1k->val_thiscond = true;
		break;
	case 0x0e:	// SPARE
		r1k->val_thiscond = true;
		break;
	case 0x0f:	// E VAL_PREVIOUS
		r1k->val_thiscond = r1k->val_last_cond;
		break;
	case 0x10:	// L VAL_ALU_32_ZERO
		r1k->val_thiscond = (r1k->val_nalu >> 32);
		break;
	case 0x11:	// L VAL_ALU_40_ZERO
		r1k->val_thiscond = (r1k->val_nalu >> 16);
		break;
	case 0x12:	// L VAL_ALU_MIDDLE_ZERO
		r1k->val_thiscond = (r1k->val_nalu & 0xffff0000ULL);
		break;
	case 0x13:	// E VAL_Q_BIT
		r1k->val_thiscond = mp_q_bit;
		break;
	case 0x14:	// SPARE
		r1k->val_thiscond = true;
		break;
	case 0x15:	// E VAL_M_BIT
		r1k->val_thiscond = r1k->val_mbit;
		break;
	case 0x16:	// E VAL_TRUE
		r1k->val_thiscond = false;
		break;
	case 0x17:	// E VAL_FALSE
		r1k->val_thiscond = true;
		break;
	default:
		break;
	}
	return (!r1k->val_thiscond);
}

static bool
val_fiu_cond(void)
{
	unsigned csel = mp_cond_sel;
	bool fcond;
	switch (csel) {
	case 0x00:
		fcond = r1k->val_nalu == 0;
		break;
	case 0x01:
		fcond = r1k->val_nalu != 0;
		break;
	case 0x02:
		if (r1k->val_amsb ^ r1k->val_bmsb) {
			fcond = r1k->val_bmsb;
		} else {
			fcond = !r1k->val_coh;
		}
		break;
	case 0x0f:
	case 0x16:		// Undocumented
		fcond = r1k->val_last_cond;
		break;
	default:
		assert(false);
		break;
	}
	return (!fcond);
}

static uint64_t
val_find_b(unsigned uir)
{
	uint64_t retval = tv_find_ab(uir, UIR_VAL_FRM, false, false, r1k->val_rfram);
	if (r1k->val_rand == 0x6) {		// "IMMEDIATE_OP"
		retval &= ~0xffULL;
		retval |= ~mp_val_bus & 0xffULL;
	}
	return (retval);
}

static void
val_h1(void)
{
	r1k->val_rand = UIR_VAL_RAND;
	if (mp_fiu_oe == 0x2) {
		r1k->val_a = tv_find_ab(UIR_VAL_A, UIR_VAL_FRM, true, false, r1k->val_rfram);
		r1k->val_amsb = r1k->val_a >> 63;
		mp_fiu_bus = ~r1k->val_a;
	}
	if (mp_tv_oe & VAL_V_OE) {
		r1k->val_b = val_find_b(UIR_VAL_B);
		r1k->val_bmsb = r1k->val_b >> 63;
		mp_val_bus = ~r1k->val_b;
	}
}

static void
val_q2(void)
{

	bool divide = r1k->val_rand != 0xb;
	if (mp_fiu_oe != 0x02) {
		r1k->val_a = tv_find_ab(UIR_VAL_A, UIR_VAL_FRM, true, false, r1k->val_rfram);
		r1k->val_amsb = r1k->val_a >> 63;
	}
	if (!(mp_tv_oe & VAL_V_OE)) {
		r1k->val_b = val_find_b(UIR_VAL_B);
		r1k->val_bmsb = r1k->val_b >> 63;
	}

	if (r1k->val_rand == 0xc) {
		r1k->val_malat = ~r1k->val_a;
		r1k->val_mblat = ~r1k->val_b;
	}

	unsigned proma = UIR_VAL_AFNC;
	if (r1k->val_rand < 8) {
		proma |= 7 << 5;
	} else {
		proma |= (15 - r1k->val_rand) << 5;
	}
	if (!((r1k->val_last_cond && divide) || (mp_q_bit && !divide))) {
		proma |= 0x100;
	}

	unsigned tmp = val_pa011[proma];
	r1k->val_isbin = (tmp >> 1) & 1;

	F181_ALU(tmp, r1k->val_a, r1k->val_b,(tmp >> 2) & 1, r1k->val_nalu, r1k->val_carry_middle);

	tmp = tv_pa010[proma];
	r1k->val_ovren = (tmp >> 1) & 1;
	r1k->val_sub_else_add = (tmp >> 2) & 1;

	uint64_t o;
	F181_ALU(tmp, r1k->val_a >> 32, r1k->val_b >> 32, r1k->val_carry_middle, o, r1k->val_coh);
	r1k->val_nalu |= o << 32;

	r1k->val_alu = ~r1k->val_nalu;
	r1k->val_cmsb = r1k->val_alu >> 63;
	if (mp_adr_oe & 0x2) {
		uint64_t alu = r1k->val_alu;
		// XXX: there is a race here, if TYP gets the space from typ_b only in Q2
		if (mp_spc_bus != 4) {
			alu |=0xf8000000ULL;
		}
		mp_adr_bus = ~alu;
	}
}

static void
val_q4(void)
{

	if (mp_ram_stop && !mp_freeze) {
		uint64_t fiu = 0, mux = 0;
		bool c_source = UIR_VAL_CSRC;
		bool split_c_src = r1k->val_rand == 0x4;
		if (split_c_src || !c_source) {
			fiu = ~mp_fiu_bus;
		}
		if (!c_source && (r1k->val_rand == 3 || r1k->val_rand == 6)) {
			fiu &= ~1ULL;
			fiu |= val_fiu_cond();
		}
		if (c_source || split_c_src) {
			unsigned sel = UIR_VAL_SEL;
			switch (sel) {
			case 0x0:
				mux = r1k->val_alu << 1;
				mux |= 1;
				break;
			case 0x1:
				mux = r1k->val_alu >> 16;
				mux |= 0xffffULL << 48;
				break;
			case 0x2:
				mux = r1k->val_alu;
				break;
			case 0x3:
				mux = r1k->val_wdr;
				break;
			default:
				assert(0);
			}
		}
		uint64_t val_c;
		if (!split_c_src && !c_source) {
			val_c = fiu;
		} else if (!split_c_src) {
			val_c = mux;
		} else if (c_source) {
			val_c = fiu & 0xffffffffULL;
			val_c |= mux & 0xffffffffULL << 32;
		} else {
			val_c = mux & 0xffffffffULL;
			val_c |= fiu & 0xffffffffULL << 32;
		}

		uint32_t a;
		switch (UIR_VAL_MSRC >> 2) {
		case 0: a = (r1k->val_malat >> 48) & 0xffff; break;
		case 1: a = (r1k->val_malat >> 32) & 0xffff; break;
		case 2: a = (r1k->val_malat >> 16) & 0xffff; break;
		case 3: a = (r1k->val_malat >>  0) & 0xffff; break;
		default: assert(false);
		}
		uint32_t b;
		switch (UIR_VAL_MSRC & 3) {
		case 0: b = (r1k->val_mblat >> 48) & 0xffff; break;
		case 1: b = (r1k->val_mblat >> 32) & 0xffff; break;
		case 2: b = (r1k->val_mblat >> 16) & 0xffff; break;
		case 3: b = (r1k->val_mblat >>  0) & 0xffff; break;
		default: assert(false);
		}
		r1k->val_mprod = a * b;

		unsigned cadr = tv_cadr(UIR_VAL_C, UIR_VAL_FRM, r1k->val_count);
		if (cadr < 0x400)
			r1k->val_rfram[cadr] = ~val_c;

		if (mp_clock_stop) {
			bool divide = r1k->val_rand != 0xb;
			if (!(mp_load_wdr || !(mp_clock_stop_6 && mp_clock_stop_7))) {
				r1k->val_wdr = ~mp_val_bus;
			}
			if (UIR_VAL_C == 0x28) {
				r1k->val_count = val_c;
				r1k->val_count &= 0x3ff;
			} else if (r1k->val_rand == 0x2 || !divide) {
				r1k->val_count += 1;
				r1k->val_count &= 0x3ff;
			} else if (r1k->val_rand == 0x1) {
				r1k->val_count += 0x3ff;
				r1k->val_count &= 0x3ff;
			}

			mp_nxt_q_bit = !(((!divide) && (mp_q_bit ^ r1k->val_mbit ^ (!r1k->val_coh))) || (divide && r1k->val_coh));
			r1k->val_mbit = r1k->val_cmsb;

			if (r1k->val_rand == 0x5) {
				uint64_t count2 = 0x40 - flsll(~r1k->val_alu);
				r1k->val_zerocnt = ~count2;
			}
			r1k->val_last_cond = r1k->val_thiscond;
		}
	}
	if (!mp_sf_stop) {
		r1k->val_uir = r1k->val_wcsram[mp_nua_bus] ^ 0xffff800000ULL;
	}
}

// ------------------ TYP&VAL ------------------

static uint64_t
tv_find_ab(unsigned uir, unsigned frame, bool a, bool t, const uint64_t *rfram)
{
	// NB: uir is inverted
	// Sorted after frequency of use.

	if (uir >= 0x30) { // very frequent
		return(~(rfram[uir & 0x1f]));						// 0x00…0x0f	GP0…GPF
	}

	if (uir < 0x20) { // very frequent
		return (~(rfram[(frame << 5) | (uir & 0x1f)]));				// 0x20…0x30	FRAME:REG
	}

	if (uir >= 0x2d) {								// 0x10…0x12	TOP,TOP+1,SPARE
		return (~(rfram[(uir + r1k->csa_topreg + 1) & 0xf]));
	}

	if (!a && uir == 0x29) {							// 0x16		CSA/VAL_BUS
		if ((!t) && !(mp_tv_oe & VAL_V_OE)) {
			return (~mp_val_bus);
		} else if ((t) && !(mp_tv_oe & TYP_T_OE)) {
			return (~mp_typ_bus);
		} else {
			unsigned adr = (r1k->csa_botreg + (uir&1)) & 0xf;
			adr += mp_csa_offset;
			adr &= 0xf;
			return(~(rfram[adr]));
		}
	}

	if (0x20 <= uir && uir <= 0x27) {						// 0x18…0x1f	TOP-8…TOP-1
		return (~(rfram[(uir + r1k->csa_topreg + 1) & 0xf]));
	}

	if (t && uir == 0x2c) {								// 0x13		[LOOP]
		return(~(rfram[r1k->typ_count]));
	} else if (uir == 0x2c) {
		return(~(rfram[r1k->val_count]));
	}

	if (t && a && uir >= 0x29) {							// 0x14…0x16	ZERO,SPARE,SPARE
		return(~0ULL);
	}

	if ((!t) && a && uir == 0x2b) {							// 0x14		ZEROS
		return(~0ULL);
	}

	if ((!t) && a && uir == 0x2a) {							// 0x15		ZERO_COUNTER
		return(r1k->val_zerocnt);
	}

	if ((!t) && a && uir == 0x29) {							// 0x16		PRODUCT
		unsigned mdst;
		bool prod_16 = r1k->val_rand != 0xd;
		bool prod_32 = r1k->val_rand != 0xe;
		mdst = prod_32 << 1;
		mdst |= prod_16;
		switch(mdst) {
		case 0: r1k->val_a = 0; break;
		case 1: r1k->val_a = r1k->val_mprod << 32; break;
		case 2: r1k->val_a = r1k->val_mprod << 16; break;
		case 3: r1k->val_a = r1k->val_mprod <<  0; break;
		default: assert(0);
		}
		return (~r1k->val_a);
	}

	if (a && uir == 0x28) {								// 0x17		LOOP
		if (t)
			return ((~0ULL << 10) | r1k->typ_count);
		else
			return ((~0ULL << 10) | r1k->val_count);
	}

	if (!a && uir >= 0x2a) {							// 0x14…0x15	BOT-1,BOT
		unsigned adr = (r1k->csa_botreg + (uir&1)) & 0xf;
		return(~(rfram[adr]));
	}

	if (!a && uir == 0x28) {							// 0x17		SPARE
		return(~0ULL);
	}

	assert(0);
}

static void
csa_q4(void)
{
	bool sclken = (mp_clock_stop && mp_ram_stop && !mp_freeze);

	if (sclken) {
		unsigned csmux0;

		if (mp_load_top)
			csmux0 = r1k->csa_botreg;
		else
			csmux0 = r1k->csa_topreg;

		unsigned csalu0 = mp_csa_this_offs + csmux0 + 1;

		if (!mp_load_bot)
			r1k->csa_botreg = csalu0;
		if (!(mp_load_top && mp_pop_down))
			r1k->csa_topreg = csalu0;
	}
}

static unsigned
tv_cadr(unsigned uirc, unsigned frame, unsigned count)
{
	// Ordered by frequency of use.
	// Pay attention to the order of range comparisons when reordering

	if (uirc == 0x29 && !mp_csa_write_enable) {			// 0x29		DEFAULT (RF write disabled)
		return(0x400);
	}
	if (uirc >= 0x30) {						// 0x30…0x3f	GP[0…F]
		return(0x10 | (uirc & 0x0f));
	}
	if (uirc <= 0x1f) {						// 0x00…0x1f	FRAME:REG
		return((uirc & 0x1f) | (frame << 5));
	}
	if (uirc == 0x2e || uirc == 0x2f) {				// 0x2e…0x2f	TOP+1,TOP
		return((r1k->csa_topreg + (uirc & 0x1) + 0xf) & 0xf);
	}
	if (uirc <= 0x27) {						// 0x20…0x27	TOP-1…TOP-8
		return((r1k->csa_topreg + (uirc & 0x7) + 1) & 0xf);
	}
	if (uirc == 0x28) {						// 0x28		LOOP COUNTER (RF write disabled)
		return(0x400);
	}
	if (uirc == 0x29 && mp_csa_write_enable) {			// 0x29		DEFAULT (RF write disabled)
		return ((r1k->csa_botreg + mp_csa_offset + 1) & 0xf);
	}
	if (uirc <= 0x2b) {						// 0x2a…0x2b	BOT,BOT-1
		return ((r1k->csa_botreg + (uirc & 1)) & 0xf);
	}
	if (uirc == 0x2c) {						// 0x2c		LOOP_REG
		return(count);
	}
	if (uirc == 0x2d) {						// 0x2d		SPARE
		return (0x400);
	}
	assert(0);
}

// -------------------- IOC --------------------

static void
ioc_do_xact(void)
{
	if (!r1k->ioc_xact)
		r1k->ioc_xact = ioc_sc_bus_get_xact();

	if (!r1k->ioc_xact)
		return;

	if (r1k->ioc_xact->sc_state == 200 && r1k->ioc_xact->address == 0xfffff100) {
		/* READ GET REQUEST */
		r1k->ioc_xact->data = r1k->ioc_reqreg;
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff200) {
		/* WRITE FRONT PANEL */
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}

	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff300) {
		/* WRITE SENSE TEST */
		r1k->ioc_request_int_en = (r1k->ioc_xact->data >> 1) & 1;
		r1k->ioc_response_int_en = (r1k->ioc_xact->data >> 0) & 1;
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff400) {
		/* WRITE CONTROL */
		r1k->ioc_fffff400 = (r1k->ioc_xact->data >> 16) & 0xf;
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff500) {
		/* WRITE FIFO INIT */
		r1k->ioc_reqwrp = r1k->ioc_reqrdp = 0;
		r1k->ioc_rspwrp = r1k->ioc_rsprdp = 0;
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}

	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff600) {
		/* WRITE FIFO CPU RSP */
		r1k->ioc_rspfifo[r1k->ioc_rspwrp++] = r1k->ioc_xact->data;
		r1k->ioc_rspwrp &= 0x3ff;

		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}

	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff700) {
		/* WRITE CPU REQUEST */
		r1k->ioc_reqreg = r1k->ioc_reqfifo[r1k->ioc_reqrdp++];
		r1k->ioc_reqrdp &= 0x3ff;
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}

	if (r1k->ioc_xact->sc_state == 200 && r1k->ioc_xact->address == 0xfffff800) {
		/* READ STATUS */
		r1k->ioc_xact->data = 0x9000ff80;
		if (r1k->ioc_cpu_running) {
			r1k->ioc_xact->data |= 0x40000000;
		}
		// if (PIN_PROTE)			r1k->ioc_xact->data |= 0x02000000;
		if (r1k->ioc_fffff400 & 8)	r1k->ioc_xact->data |= 0x00080000; // IOP.INTR_EN
		if (r1k->ioc_fffff400 & 4)	r1k->ioc_xact->data |= 0x00040000; // GOOD_PARITY
		if (r1k->ioc_fffff400 & 2)	r1k->ioc_xact->data |= 0x00020000; // PERR_ENABLE
		if (r1k->ioc_fffff400 & 1)	r1k->ioc_xact->data |= 0x00010000; // IOP.NEXT_CLK
		r1k->ioc_xact->data |= 0x7 << 4;
		if (!mp_key_switch)		r1k->ioc_xact->data |= 0x00000008;
		r1k->ioc_xact->data |= r1k->ioc_iack << 0;

		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}

	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffff900) {
		/* WRITE CLEAR BERR */
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffffe00) {
		/* WRITE CPU CONTROL */
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
	if (r1k->ioc_xact->sc_state == 100 && r1k->ioc_xact->address == 0xfffffd00) {
		ioc_sc_bus_done(&r1k->ioc_xact);
		return;
	}
}

static bool
ioc_cond(void)
{
	switch (mp_cond_sel) {
	case 0x78:
		return (true); // r1k->ioc_multibit_error;
		break;
	case 0x79:
		{
		uint64_t tmp = mp_typ_bus & 0x80000047;
		return (tmp == 0x80000000 || tmp == 0x80000040 || tmp == 0x80000044);
		}
		break;
	case 0x7a:
		return (true); // r1k->ioc_checkbit_error;
		break;
	case 0x7b:
		return (r1k->ioc_reqwrp != r1k->ioc_reqrdp);
		break;
	case 0x7c:
		return (r1k->ioc_acnt == 0xfff);
		break;
	case 0x7d:
		return (true);
		break;
	case 0x7e:
		return (r1k->ioc_rspwrp != r1k->ioc_rsprdp);
		break;
	case 0x7f:
		return (true);
		break;
	default: assert(0);
	}
}

static void
ioc_h1(void)
{
	if (r1k->ioc_rspwrp != r1k->ioc_rsprdp) {
		mp_macro_event |= 0x8;
	} else {
		mp_macro_event &= ~0x8;
	}

	mp_load_wdr = UIR_IOC_ULWDR;

	if (mp_tv_oe & IOC_TV_OE) {
		mp_val_bus = r1k->ioc_dummy_val;

		switch (UIR_IOC_RAND) {
		case 0x05:
			mp_typ_bus = (uint64_t)(r1k->ioc_slice) << 48;
			mp_typ_bus |= (uint64_t)(r1k->ioc_delay) << 32;
			mp_typ_bus |= ((uint64_t)r1k->ioc_rtc) << 16;
			mp_typ_bus |= r1k->ioc_rspfifo[r1k->ioc_rsprdp];
			break;
		case 0x08:
		case 0x09:
		case 0x19:
			mp_typ_bus = (uint64_t)(r1k->ioc_slice) << 48;
			mp_typ_bus |= (uint64_t)(r1k->ioc_delay) << 32;
			mp_typ_bus |= ((uint64_t)r1k->ioc_rtc) << 16;
			break;
		case 0x16:
		case 0x1c:
		case 0x1d:
			mp_typ_bus = ((uint64_t)r1k->ioc_rdata) << 32;
			mp_typ_bus |= ((uint64_t)r1k->ioc_rtc) << 16;
			break;
		default:
			mp_typ_bus = r1k->ioc_dummy_typ;
			break;
		}
	}
}

static void
ioc_q2(void)
{
	unsigned rand = UIR_IOC_RAND;
	if (r1k->ioc_slice_ev && !r1k->ioc_ten) {
		mp_macro_event |= 0x2;
	}
	if (rand == 0x0a) {
		mp_macro_event &= ~0x2;
	}
	if (r1k->ioc_delay_ev && !r1k->ioc_ten) {
		mp_macro_event |= 0x1;
	}
	if (rand == 0x0b) {
		mp_macro_event &= ~0x1;
	}
	uint64_t tmp = (mp_typ_bus >> 7) & 0xfffff;
	bool below = (tmp >= 0xc);
	bool exit_proc = rand != 0x12;
	mp_below_tcp = !(below || exit_proc);
}

static void
ioc_q4(void)
{
	unsigned rand = UIR_IOC_RAND;

	if (mp_ioc_trace && ((mp_sync_freeze & 0x3) == 0) && !r1k->ioc_is_tracing) {
		r1k->ioc_is_tracing = true;
	}
	if (mp_ioc_trace && (mp_sync_freeze & 0x3) && r1k->ioc_is_tracing) {
		r1k->ioc_is_tracing = true;
		mp_ioc_trace = 0;
	}

	if ((r1k->ioc_request_int_en && r1k->ioc_reqrdp != r1k->ioc_reqwrp) && r1k->ioc_iack != 6) {
		r1k->ioc_iack = 6;
		ioc_sc_bus_start_iack(6);
	}
	if ((!r1k->ioc_request_int_en || r1k->ioc_reqrdp == r1k->ioc_reqwrp) && r1k->ioc_iack != 7) {
		r1k->ioc_iack = 7;
		ioc_sc_bus_start_iack(7);
	}

	ioc_do_xact();

	if (mp_clock_stop) {
		unsigned adr = (r1k->ioc_areg | r1k->ioc_acnt) << 2;
		assert(adr < (512<<10));

		switch(rand) {
		case 0x01:
			r1k->ioc_acnt = (mp_typ_bus >> 2) & 0x00fff;
			r1k->ioc_areg = (mp_typ_bus >> 2) & 0x1f000;
			break;
		case 0x04:
			r1k->ioc_reqfifo[r1k->ioc_reqwrp++] = mp_typ_bus & 0xffff;
			r1k->ioc_reqwrp &= 0x3ff;
			break;
		case 0x05:
			r1k->ioc_rsprdp++;
			r1k->ioc_rsprdp &= 0x3ff;
			break;
		case 0x06:
			r1k->ioc_slice = mp_typ_bus >> 48;
			break;
		case 0x07:
			r1k->ioc_delay = mp_typ_bus >> 32;
			break;
		case 0x08:
			r1k->ioc_rtc = 0;
			break;
		case 0x0c:
			r1k->ioc_sen = false;
			break;
		case 0x0d:
			r1k->ioc_sen = true;
			break;
		case 0x0e:
			r1k->ioc_den = false;
			break;
		case 0x0f:
			r1k->ioc_den = true;
			break;
		case 0x1c:
			r1k->ioc_rdata = vbe32dec(r1k->ioc_ram + adr);
			r1k->ioc_acnt += 1;
			r1k->ioc_acnt &= 0xfff;
			break;
		case 0x1d:
			r1k->ioc_rdata = vbe32dec(r1k->ioc_ram + adr);
			break;
		case 0x1e:
			vbe32enc(r1k->ioc_ram + adr, mp_typ_bus >> 32);
			r1k->ioc_acnt += 1;
			r1k->ioc_acnt &= 0xfff;
			break;
		case 0x1f:
			vbe32enc(r1k->ioc_ram + adr, mp_typ_bus >> 32);
			break;
		case 0x23:
			r1k->ioc_cpu_running = true;
			break;
		case 0x24:
			r1k->ioc_cpu_running = false;
			break;
		default:
			break;
		}
	}

	if (!mp_sf_stop && rand != 0x08) {
		r1k->ioc_rtc++;
		r1k->ioc_rtc &= 0xffff;
	}

	r1k->ioc_prescaler++;
	r1k->ioc_ten = r1k->ioc_prescaler != 0xf;
	r1k->ioc_prescaler &= 0xf;

	if (!r1k->ioc_ten) {
		r1k->ioc_slice_ev = r1k->ioc_slice == 0xffff;
		r1k->ioc_delay_ev= r1k->ioc_delay == 0xffff;
		if (rand != 0x06 && !r1k->ioc_sen)
			r1k->ioc_slice++;
		if (rand != 0x07 && !r1k->ioc_den)
			r1k->ioc_delay++;
	}
	bool rddum = (UIR_IOC_TVBS < 0xc) || !r1k->ioc_dumen;
	if (rddum && !mp_restore_rdr) {
		r1k->ioc_dummy_typ = mp_typ_bus;
		r1k->ioc_dummy_val = mp_val_bus;
	}

	if (!mp_sf_stop) {
		r1k->ioc_uir = r1k->ioc_wcsram[mp_nua_bus];
		assert (r1k->ioc_uir <= 0xffff);
		mp_nxt_adr_oe = 1U << UIR_IOC_AEN;
		mp_nxt_fiu_oe = 1U << UIR_IOC_FEN;
		r1k->ioc_dumen = !mp_dummy_next;
		r1k->ioc_csa_hit = !mp_csa_hit;

		uint16_t tdat = mp_nua_bus;
		if (!mp_clock_stop)
			tdat |= 0x8000;
		if (r1k->ioc_csa_hit)
			tdat |= 0x4000;
		uint16_t tptr = r1k->ioc_tram[2048];
		r1k->ioc_tram[tptr] = tdat;
		if (mp_ioc_trace) {
			tptr += 1;
			tptr &= 0x7ff;
			r1k->ioc_tram[2048] = tptr;
		}

		mp_nxt_tv_oe = 1U << UIR_IOC_TVBS;
		if (mp_nxt_tv_oe & MEM_TV_OE) {
			if (r1k->ioc_dumen) {
				mp_nxt_tv_oe = 1U << 4;	   // IOC_TV
			} else if (r1k->ioc_csa_hit) {
				mp_nxt_tv_oe = 1U << 0;	   // VAL_V|TYP_T
			}
		}
	}
}
