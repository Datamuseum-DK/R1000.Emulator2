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
   64x4 rotator
   ============
		|/*
		| logrw   phys_ref
		| 0       1       0000  PHYSICAL_MEM_WRITE
		| 0       1       0001  PHYSICAL_MEM_READ
		| 1       0       0010  LOGICAL_MEM_WRITE
		| 1       0       0011  LOGICAL_MEM_READ
		| 1       0       0100  COPY 0 TO 1 *
		| 1       0       0101  MEMORY_TO_TAGSTORE *
		| 1       0       0110  COPY 1 to 0 *
		| 1       0       0111  SET HIT FLIP FLOPS *
		| 0       1       1000  PHYSICAL TAG WRITE
		| 0       1       1001  PHYSICAL TAG READ
		| 0       0       1010  INITIALIZE MRU
		| 0       0       1011  LOGICAL TAG READ
		| 0       0       1100  NAME QUERY
		| 0       0       1101  LRU QUERY
		| 0       0       1110  AVAILABLE QUERY
		| 0       0       1111  IDLE
		|*/

'''

from part import PartModelDQ, PartFactory

class FIU(PartFactory):

    ''' FIU first stage rotator '''

    autopin = True

    def extra(self, file):
        file.include("Infra/cache_line.h")

    def state(self, file):
        file.fmt('''
		|       unsigned fiu_oreg;
		|       uint64_t fiu_mdreg;
		|	uint64_t fiu_treg;
		|	uint64_t fiu_vreg;
		|	uint64_t fiu_refresh_reg;
		|	uint64_t fiu_marh;
		|	uint64_t fiu_ti_bus, fiu_vi_bus;
		|	unsigned fiu_lfreg;
		|
		|	uint32_t fiu_srn, fiu_sro, fiu_ctopn, fiu_ctopo;
		|	unsigned fiu_nve, fiu_pdreg;
		|	unsigned fiu_moff;
		|	bool fiu_pdt;
		|
		|	bool fiu_state0, fiu_state1, fiu_labort, fiu_e_abort_dly;
		|	uint8_t fiu_pa025[512];
		|	uint8_t fiu_pa026[512];
		|	uint8_t fiu_pa027[512];
		|	uint8_t fiu_pa028[512];
		|	uint8_t fiu_pa060[512];
		|	uint8_t fiu_pcntl_d;
		|	uint8_t fiu_lcntl;
		|	uint8_t fiu_mcntl;
		|	bool fiu_scav_trap;
		|	bool fiu_cache_miss;
		|	bool fiu_csa_oor;
		|	bool fiu_page_xing;
		|	bool fiu_init_mru_d;
		|	bool fiu_drive_mru;
		|	bool fiu_memcnd;
		|	bool fiu_cndtru;
		|	bool fiu_incmplt_mcyc;
		|	bool fiu_mar_modified;
		|	bool fiu_write_last;
		|	bool fiu_phys_ref;
		|	bool fiu_phys_last;
		|	bool fiu_log_query;
		|	bool fiu_mctl_is_read;
		|	bool fiu_logrw;
		|	bool fiu_logrw_d;
		|	bool fiu_omf20;
		|	bool fiu_nmatch;
		|	bool fiu_in_range;
		|	unsigned fiu_setq;
		|	unsigned fiu_omq;
		|	unsigned fiu_prmt;
		|	bool fiu_dumon;
		|	bool fiu_memex;
		|	bool fiu_logrwn;
		|	bool fiu_page_crossing_next;
		|	bool fiu_miss;
		|	bool fiu_csaht;
		|	bool fiu_csa_oor_next;
		|
		|	unsigned fiu_tcsa_sr;
		|	unsigned fiu_tcsa_inval_csa;
		|	unsigned fiu_tcsa_tf_pred;
		|
		|	uint64_t *fiu_wcsram;
		|	uint64_t *fiu_typwcsram;
		|	uint64_t fiu_uir;
		|	uint64_t fiu_typuir;
		|
		|	unsigned fiu_hit_offset;
		|	unsigned fiu_condsel;
		|	bool fiu_tmp_csa_oor_next;
		|	bool fiu_scav_trap_next;
		|	bool fiu_memcyc1;
		|	bool fiu_uev10_page_x;
		|	bool fiu_uev0_memex;
		|	unsigned fiu_mem_start;
		|	bool fiu_memstart;
		|	unsigned fiu_pa025d, fiu_pa026d, fiu_pa027d;
		|
		|#define UIR_FIU_OL		((state->fiu_uir >> 40) & 0x7f)
		|#define UIR_FIU_LFL	((state->fiu_uir >> 32) & 0x7f)
		|#define UIR_FIU_LFRC	((state->fiu_uir >> 30) & 0x3)
		|#define UIR_FIU_OP		((state->fiu_uir >> 28) & 0x3)
		|#define UIR_FIU_SEL	((state->fiu_uir >> 26) & 0x3)
		|#define UIR_FIU_FSRC	((state->fiu_uir >> 25) & 1)
		|#define UIR_FIU_ORSR	((state->fiu_uir >> 24) & 1)
		|#define UIR_FIU_TIVI	((state->fiu_uir >> 20) & 0xf)
		|#define UIR_FIU_OCLK	((state->fiu_uir >> 19) & 1)
		|#define UIR_FIU_VCLK	((state->fiu_uir >> 18) & 1)
		|#define UIR_FIU_TCLK	((state->fiu_uir >> 17) & 1)
		|#define UIR_FIU_LDMDR	((state->fiu_uir >> 16) & 1)
		|#define UIR_FIU_MSTRT	((state->fiu_uir >> 10) & 0x1f)
		|#define UIR_FIU_RDSRC	((state->fiu_uir >> 9) & 1)
		|#define UIR_FIU_LSRC	((state->fiu_uir >> 1) & 1)
		|#define UIR_FIU_OSRC	((state->fiu_uir >> 0) & 1)
		|''')


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->fiu_pa025, sizeof state->fiu_pa025, "PA025-03");
		|	load_programmable(this->name(), state->fiu_pa026, sizeof state->fiu_pa026, "PA026-02");
		|	load_programmable(this->name(), state->fiu_pa027, sizeof state->fiu_pa027, "PA027-01");
		|	load_programmable(this->name(), state->fiu_pa028, sizeof state->fiu_pa028, "PA028-02");
		|	load_programmable(this->name(), state->fiu_pa060, sizeof state->fiu_pa060, "PA060");
		|	state->fiu_wcsram = (uint64_t*)CTX_GetRaw("FIU_WCS", sizeof(uint64_t) << 14);
		|	state->fiu_typwcsram = (uint64_t*)CTX_GetRaw("TYP_WCS", sizeof(uint64_t) << 14);
		|''')

    def priv_decl(self, file):
        file.fmt('''
		|
		|	uint64_t read_fiu_bus(unsigned line);
		|	void do_tivi(void);
		|	void rotator(bool sclk);
		|	void fiu_conditions(void);
		|	uint64_t frame(void);
		|	void tcsa(bool clock);
		|	void fiu_q1(void);
		|	void fiu_q2(void);
		|	void fiu_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|uint64_t
		|SCM_«mmm» ::
		|read_fiu_bus(unsigned line)
		|{
		|	return (~mp_fiu_bus);
		|}
		|
		|void
		|SCM_«mmm» ::
		|fiu_conditions()
		|{
		|
		|	switch(state->fiu_condsel) {
		|	case 0x60: mp_condx3 = !state->fiu_memex; 		break;
		|	case 0x61: mp_condx3 = !state->fiu_phys_last; 		break;
		|	case 0x62: mp_condx3 = !state->fiu_write_last; 		break;
		|	case 0x63: mp_condx3 = !mp_csa_hit; 		break;
		|	case 0x64: mp_condx3 = !((state->fiu_oreg >> 6) & 1); 	break;
		|	case 0x65: // Cross word shift
		|		mp_condx3 = (state->fiu_oreg + (state->fiu_lfreg & 0x3f) + (state->fiu_lfreg & 0x80)) <= 255;
		|		break;
		|	case 0x66: mp_condx3 = (state->fiu_moff & 0x3f) > 0x30; 	break;
		|	case 0x67: mp_condx3 = !(mp_refresh_count != 0xffff); 		break;
		|	case 0x68: mp_condx2 = !state->fiu_csa_oor_next;		break;
		|	case 0x69: mp_condx2 = !false; 			break; // SCAV_HIT
		|	case 0x6a: mp_condx2 = !state->fiu_page_xing; 		break;
		|	case 0x6b: mp_condx2 = !state->fiu_miss; 		break;
		|	case 0x6c: mp_condx2 = !state->fiu_incmplt_mcyc; 	break;
		|	case 0x6d: mp_condx2 = !state->fiu_mar_modified; 	break;
		|	case 0x6e: mp_condx2 = !state->fiu_incmplt_mcyc; 	break;
		|	case 0x6f: mp_condx2 = (state->fiu_moff & 0x3f) != 0; 	break;
		|	};
		|}
		|
		|uint64_t
		|SCM_«mmm» ::
		|frame(void)
		|{
		|	uint64_t u = 0;
		|
		|	uint64_t line = 0;
		|	line ^= cache_line_tbl_h[(state->fiu_srn >> 10) & 0x3ff];
		|	line ^= cache_line_tbl_l[(state->fiu_moff >> (13 - 7)) & 0xfff];
		|	line ^= cache_line_tbl_s[(state->fiu_sro >> 4) & 0x7];
		|
		|	u |= (uint64_t)mp_mem_cond_pol << BUS64_LSB(9);
		|	u |= (uint64_t)mp_mem_cond << BUS64_LSB(10);
		|	u |= line << BUS64_LSB(23);
		|	u |= (uint64_t)state->fiu_setq << BUS64_LSB(25);
		|	u |= (uint64_t)mp_mem_set << BUS64_LSB(27);
		|	u |= (uint64_t)((state->fiu_omq >> 2) & 0x3) << BUS64_LSB(29);
		|	u |= 0x3ULL << BUS64_LSB(31);
		|	u |= (uint64_t)(state->fiu_uev10_page_x) << BUS64_LSB(32);
		|	u |= (uint64_t)((state->fiu_prmt >> 1) & 1) << BUS64_LSB(33);
		|	u |= (uint64_t)(mp_refresh_count != 0xffff) << BUS64_LSB(34);
		|	u |= (uint64_t)(state->fiu_uev0_memex) << BUS64_LSB(35);
		|	u |= ((line >> 0) & 1) << BUS64_LSB(48);
		|	u |= ((line >> 1) & 1) << BUS64_LSB(50);
		|	u |= (uint64_t)state->fiu_nmatch << BUS64_LSB(56);
		|	u |= (uint64_t)state->fiu_in_range << BUS64_LSB(57);
		|	u |= (uint64_t)state->fiu_csa_oor_next << BUS64_LSB(58);
		|	u |= (uint64_t)mp_csa_hit << BUS64_LSB(59);
		|	u |= (uint64_t)state->fiu_hit_offset;
		|	return (u);
		|}
		|
		|void
		|SCM_«mmm» ::
		|do_tivi(void)
		|{
		|
		|	unsigned tivi = UIR_FIU_TIVI;
		|
		|	uint64_t vi;
		|	switch (tivi) {
		|	case 0x00: case 0x04: case 0x08:
		|		vi = state->fiu_vreg;
		|		break;
		|	case 0x01: case 0x05: case 0x09:
		|		vi = ~mp_val_bus;
		|		break;
		|	case 0x02: case 0x06: case 0x0a:
		|		vi = read_fiu_bus(tivi);
		|		break;
		|	case 0x03: case 0x07: case 0x0b:
		|		vi = frame() ^ ~0ULL;
		|		break;
		|	default:
		|		vi = (uint64_t)state->fiu_srn << 32;
		|		vi |= state->fiu_sro & 0xffffff80;
		|		vi |= state->fiu_oreg;
		|		vi = ~vi;
		|		break;
		|	}
		|	uint64_t ti;
		|	switch (tivi) {
		|	case 0x00: case 0x01: case 0x02: case 0x03:
		|		ti = state->fiu_treg;
		|		break;
		|	case 0x04: case 0x05: case 0x06: case 0x07:
		|		ti = read_fiu_bus(tivi);
		|		break;
		|	case 0x08: case 0x09: case 0x0a: case 0x0b:
		|		ti = ~mp_typ_bus;
		|		break;
		|	default:
		|		uint64_t tmp;
		|		tmp = (state->fiu_sro >> 4) & 0x7;
		|		state->fiu_marh &= ~0x07;
		|		state->fiu_marh |= tmp;
		|		state->fiu_marh &= ~(0x1efULL << 23ULL);
		|		state->fiu_marh |= (uint64_t)(!state->fiu_incmplt_mcyc) << 23;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_mar_modified) << 24;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_write_last) << 25;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_phys_last) << 26;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_cache_miss) << 28;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_page_xing) << 29;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_csa_oor) << 30;
		|		state->fiu_marh |= (uint64_t)(!state->fiu_scav_trap) << 31;
		|		ti = ~state->fiu_marh;
		|		break;
		|	}
		|	state->fiu_ti_bus = ti;
		|	state->fiu_vi_bus = vi;
		|}
		|
		|void
		|SCM_«mmm» ::
		|rotator(bool sclk)
		|{
		|	uint64_t rot = 0;
		|	uint64_t vmsk = 0, tmsk = 0;
		|	bool sgnbit = 0;
		|	uint64_t ft, tir, vir;
		|	unsigned s, fs, sgn;
		|	bool zero_length;
		|
		|	unsigned lfl = UIR_FIU_LFL;
		|
		|	bool fill_mode = false;
		|	if (UIR_FIU_FSRC) {				// UCODE
		|		fill_mode = lfl >> 6;
		|	} else {
		|		fill_mode = (state->fiu_lfreg >> 6) & 1;
		|	}
		|
		|	unsigned lenone;
		|	if (UIR_FIU_LSRC) {				// UCODE
		|		lenone = lfl & 0x3f;
		|	} else {
		|		lenone = state->fiu_lfreg & 0x3f;
		|	}
		|
		|	zero_length = !(fill_mode & (lenone == 0x3f));
		|
		|	unsigned offset;
		|	if (UIR_FIU_OSRC) {				// UCODE
		|		offset = UIR_FIU_OL;
		|	} else {
		|		offset = state->fiu_oreg;
		|	}
		|
		|
		|	unsigned op, sbit, ebit;
		|	op = UIR_FIU_OP;				// UCODE
		|	switch (op) {
		|	case 0:
		|		sbit = (lenone ^ 0x3f) | (1<<6);
		|		ebit = 0x7f;
		|		break;
		|	case 1:
		|		sbit = 0;
		|		ebit = (lenone & 0x3f) + (offset & 0x7f);
		|		break;
		|	case 2:
		|		sbit = offset;
		|		ebit = 0x7f;
		|		break;
		|	case 3:
		|		sbit = offset;
		|		ebit = (lenone & 0x3f) + (offset & 0x7f);
		|		break;
		|	}
		|	sbit &= 0x7f;
		|	ebit &= 0x7f;
		|
		|	uint64_t msk6;
		|	if (op != 0) {
		|		msk6 = ~0ULL;
		|		if (((offset + lenone) & 3) != 3) {
		|			msk6 >>= 4;
		|		}
		|	} else {
		|		unsigned sx = (offset + (lenone & 3)) & ~0x3;
		|		if (sx == 0 || sx == 0x80) {
		|			msk6 = 0;
		|		} else if (sx < 0x40) {
		|			msk6 = ~0ULL << (64 - sx);
		|		} else {
		|			msk6 = ~0ULL >> (sx - 64);
		|		}
		|	}
		|
		|	// The actual rotation
		|	if (op == 0) {
		|		s = (lenone ^ 0x3f) + 0xc0 - offset;
		|	} else {
		|		s = lenone + offset + 1;
		|	}		
		|	s &= 0x3f;
		|
		|	fs = s & 3;
		|	if (fs == 0) {
		|		tir = state->fiu_ti_bus;
		|		vir = state->fiu_vi_bus;
		|	} else {
		|		tir = state->fiu_ti_bus >> fs;
		|		tir |= state->fiu_vi_bus << (64 - fs);
		|		vir = state->fiu_vi_bus >> fs;
		|		vir |= state->fiu_ti_bus << (64 - fs);
		|	}
		|
		|	ft = msk6 & vir;
		|	ft |= (~msk6) & tir;
		|
		|	if (fill_mode) {
		|		sgnbit = true;
		|	} else {
		|		sgn = offset & 0x3c;
		|		if ((offset & 3) + (lenone & 3) > 3)
		|			sgn += 4;
		|		sgn |= (lenone & 3) ^ 3;
		|
		|		sgnbit = (ft >> (63 - sgn)) & 1;
		|	}
		|
		|	{
		|		uint64_t yl = 0, yh = 0;
		|		fs = s & ~3;
		|		yl = ft >> fs;
		|		yh = ft << (64 - fs);
		|		rot = yh | yl;
		|	}
		|
		|	if (zero_length) {
		|		if (ebit == sbit) {
		|			if (ebit < 64) {
		|				tmsk = 1ULL << (63 - ebit);
		|				vmsk = 0;
		|			} else {
		|				tmsk = 0;
		|				vmsk = 1ULL << (127 - ebit);
		|			} 
		|		} else {
		|			uint64_t inv = 0;
		|			unsigned sb = sbit, eb = ebit;
		|			if (eb < sb) {
		|				sb = ebit + 1;
		|				eb = sbit - 1;
		|				inv = ~(uint64_t)0;
		|			}
		|			if (sb < 64)
		|				tmsk = (~(uint64_t)0) >> sb;
		|			if (eb < 63)
		|				tmsk ^= (~(uint64_t)0) >> (eb + 1);
		|			if (eb > 63)
		|				vmsk = (~(uint64_t)0) << (127 - eb);
		|			if (sb > 64)
		|				vmsk ^= (~(uint64_t)0) << (128 - sb);
		|			tmsk ^= inv;
		|			vmsk ^= inv;
		|		}
		|	}
		|
		|	unsigned sel = UIR_FIU_SEL;
		|
		|	uint64_t tii = 0;
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		if (sgnbit)
		|			tii = ~0ULL;
		|		break;
		|	case 2:
		|		tii = mp_val_bus;
		|		tii = state->fiu_vi_bus;
		|		break;
		|	case 3:
		|		tii = read_fiu_bus(0x20);
		|		break;
		|	}
		|
		|	uint64_t rdq;
		|	if (UIR_FIU_RDSRC) {				// UCODE
		|		rdq = state->fiu_mdreg;
		|	} else {
		|		rdq = rot;
		|	}
		|
		|	uint64_t vout = 0;
		|	vout = rdq & vmsk;
		|	vout |= tii & ~vmsk;
		|
		|	if (mp_fiu_oe == 0x1) {
		|		mp_fiu_bus = ~vout;
		|	}
		|
		|	if (sclk && UIR_FIU_LDMDR) {			// (UCODE)
		|		state->fiu_mdreg = rot;
		|	}
		|
		|	if (sclk && !UIR_FIU_TCLK) {			// Q4~^
		|		state->fiu_treg = rdq & tmsk;
		|		state->fiu_treg |= state->fiu_ti_bus & ~tmsk;
		|	}
		|
		|	if (sclk && !UIR_FIU_VCLK) {			// Q4~^
		|		state->fiu_vreg = vout;
		|	}
		|
		|
		|}
		|
		|void
		|SCM_«mmm» ::
		|tcsa(bool clock)
		|{
		|	bool invalidate_csa = !(mp_csa_hit && !state->fiu_tcsa_tf_pred);
		|	unsigned hit_offs = state->fiu_hit_offset;
		|
		|	unsigned adr;
		|	if (state->fiu_tcsa_tf_pred) {
		|		adr = state->fiu_tcsa_sr;
		|		adr |= 0x100;
		|	} else {
		|		adr = hit_offs;
		|	}
		|	adr ^= 0xf;
		|	unsigned csacntl = mp_csa_cntl;
		|	adr |= csacntl << 4;
		|
		|	if (state->fiu_tcsa_inval_csa)
		|		adr |= (1<<7);
		|
		|	unsigned q = state->fiu_pa060[adr];
		|	bool load_ctl_top = (q >> 3) & 0x1;
		|	bool load_top_bot = (q >> 2) & 0x1;
		|	bool sel_constant = (q >> 1) & 0x1;
		|	bool minus_one = (q >> 0) & 0x1;
		|
		|	mp_load_top = !(load_top_bot && ((csacntl >> 1) & 1));
		|	mp_load_bot = !(load_top_bot && ((csacntl >> 2) & 1));
		|	mp_pop_down = load_ctl_top && state->fiu_tcsa_tf_pred;
		|
		|	if (!invalidate_csa) {
		|		mp_csa_offs = 0xf;
		|	} else if (!sel_constant && !minus_one) {
		|		mp_csa_offs = 0x1;
		|	} else if (!sel_constant && minus_one) {
		|		mp_csa_offs = 0xf;
		|	} else {
		|		mp_csa_offs = hit_offs;
		|	}
		|
		|	mp_csa_nve = q >> 4;
		|
		|	if (clock) {
		|		state->fiu_tcsa_sr = q >> 4;
		|		state->fiu_tcsa_inval_csa = invalidate_csa;
		|		unsigned csacntl0 = (state->fiu_typwcsram[mp_nua_bus] >> 1) & 7;
		|		unsigned csacntl1 = (state->fiu_typuir >> 1) & 6;
		|		state->fiu_tcsa_tf_pred = !((csacntl0 == 7) && (csacntl1 == 0));
		|	}
		|
		|}
		|
		|void
		|SCM_«mmm» ::
		|fiu_q1(void)
		|{
		|	bool sclk = false;
		|	bool carry, name_match;
		|
		|	unsigned mar_cntl = mp_mar_cntl;
		|	bool rmarp = (mar_cntl & 0xe) == 0x4;
		|
		|	do_tivi();
		|	if (mp_fiu_oe == 0x1) {
		|		rotator(sclk);
		|	}
		|	unsigned dif;
		|
		|	if (state->fiu_pdt) {
		|		carry = state->fiu_ctopo <= state->fiu_pdreg;
		|		dif = ~0xfffff + state->fiu_pdreg - state->fiu_ctopo;
		|	} else {
		|		carry = state->fiu_moff <= state->fiu_ctopo;
		|		dif = ~0xfffff + state->fiu_ctopo - state->fiu_moff;
		|	}
		|	dif &= 0xfffff;
		|
		|	name_match = 
		|		    (state->fiu_ctopn != state->fiu_srn) ||
		|		    ((state->fiu_sro & 0xf8000070 ) != 0x10);
		|
		|	state->fiu_in_range = (!state->fiu_pdt && name_match) || (dif & 0xffff0);
		|
		|	state->fiu_hit_offset = (0xf + state->fiu_nve - (dif & 0xf)) & 0xf;
		|
		|	mp_csa_hit = (bool)!(carry && !(state->fiu_in_range || ((dif & 0xf) >= state->fiu_nve)));
		|
		|	unsigned pa025a = 0;
		|	pa025a |= state->fiu_mem_start;
		|	pa025a |= state->fiu_state0 << 8;
		|	pa025a |= state->fiu_state1 << 7;
		|	pa025a |= state->fiu_labort << 6;
		|	pa025a |= state->fiu_e_abort_dly << 5;
		|	state->fiu_pa025d = state->fiu_pa025[pa025a];
		|	state->fiu_memcyc1 = (state->fiu_pa025d >> 1) & 1;
		|	state->fiu_memstart = (state->fiu_pa025d >> 0) & 1;
		|
		|	if (state->fiu_memstart) {
		|		state->fiu_mcntl = state->fiu_lcntl;
		|	} else {
		|		state->fiu_mcntl = state->fiu_pcntl_d;
		|	}
		|	state->fiu_phys_ref = !(state->fiu_mcntl & 0x6);
		|	state->fiu_logrwn = !(state->fiu_logrw && state->fiu_memcyc1);
		|	state->fiu_logrw = !(state->fiu_phys_ref || ((state->fiu_mcntl >> 3) & 1));
		|
		|	state->fiu_scav_trap_next = state->fiu_scav_trap;
		|	if (state->fiu_condsel == 0x69) {		// SCAVENGER_HIT
		|		state->fiu_scav_trap_next = false;
		|	} else if (rmarp) {
		|		state->fiu_scav_trap_next = (state->fiu_ti_bus >> BUS64_LSB(32)) & 1;
		|	} else if (state->fiu_log_query) {
		|		state->fiu_scav_trap_next = false;
		|	}
		|
		|
		|	state->fiu_tmp_csa_oor_next = state->fiu_csa_oor;
		|	if (state->fiu_condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|		state->fiu_tmp_csa_oor_next = false;
		|	} else if (rmarp) {
		|		state->fiu_tmp_csa_oor_next = (state->fiu_ti_bus >> BUS64_LSB(33)) & 1;
		|	} else if (state->fiu_log_query) {
		|		state->fiu_tmp_csa_oor_next = state->fiu_csa_oor_next;
		|	}
		|
		|	bool pgmod = (state->fiu_omq >> 1) & 1;
		|	unsigned board_hit = mp_mem_hit;
		|	unsigned pa027a = 0;
		|	pa027a |= board_hit << 5;
		|	pa027a |= state->fiu_init_mru_d << 4;
		|	pa027a |= (state->fiu_omq & 0xc);
		|	pa027a |= 1 << 1;
		|	pa027a |= pgmod << 0;
		|	state->fiu_pa027d = state->fiu_pa027[pa027a];
		|	state->fiu_setq = (state->fiu_pa027d >> 3) & 3;
		|
		|	bool mnor0b = state->fiu_drive_mru || ((state->fiu_pa027d & 3) == 0);
		|	bool mnan2a = !(mnor0b && state->fiu_logrw_d);
		|	state->fiu_miss = !(
		|		((board_hit != 0xf) && mnan2a) ||
		|		(state->fiu_logrw_d && state->fiu_csaht)
		|	);
		|	if (mp_refresh_count == 0xffff) {
		|		mp_macro_event |= 0x40;
		|	} else {
		|		mp_macro_event &= ~0x40;
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|fiu_q2(void)
		|{
		|	do_tivi();
		|	unsigned pa025a = 0;
		|	pa025a |= state->fiu_mem_start;
		|	pa025a |= state->fiu_state0 << 8;
		|	pa025a |= state->fiu_state1 << 7;
		|	pa025a |= state->fiu_labort << 6;
		|	pa025a |= state->fiu_e_abort_dly << 5;
		|	state->fiu_pa025d = state->fiu_pa025[pa025a];
		|	state->fiu_memcyc1 = (state->fiu_pa025d >> 1) & 1;
		|	state->fiu_memstart = (state->fiu_pa025d >> 0) & 1;
		|
		|	if (state->fiu_memstart) {
		|		state->fiu_mcntl = state->fiu_lcntl;
		|	} else {
		|		state->fiu_mcntl = state->fiu_pcntl_d;
		|	}
		|	state->fiu_phys_ref = !(state->fiu_mcntl & 0x6);
		|	state->fiu_logrwn = !(state->fiu_logrw && state->fiu_memcyc1);
		|	state->fiu_logrw = !(state->fiu_phys_ref || ((state->fiu_mcntl >> 3) & 1));
		|
		|	unsigned mar_cntl = mp_mar_cntl;
		|	bool rmarp = (mar_cntl & 0xe) == 0x4;
		|
		|	state->fiu_scav_trap_next = state->fiu_scav_trap;
		|	if (state->fiu_condsel == 0x69) {		// SCAVENGER_HIT
		|		state->fiu_scav_trap_next = false;
		|	} else if (rmarp) {
		|		state->fiu_scav_trap_next = (state->fiu_ti_bus >> BUS64_LSB(32)) & 1;
		|	} else if (state->fiu_log_query) {
		|		state->fiu_scav_trap_next = false;
		|	}
		|
		|
		|	state->fiu_tmp_csa_oor_next = state->fiu_csa_oor;
		|	if (state->fiu_condsel == 0x68) {		// CSA_OUT_OF_RANGE
		|		state->fiu_tmp_csa_oor_next = false;
		|	} else if (rmarp) {
		|		state->fiu_tmp_csa_oor_next = (state->fiu_ti_bus >> BUS64_LSB(33)) & 1;
		|	} else if (state->fiu_log_query) {
		|		state->fiu_tmp_csa_oor_next = state->fiu_csa_oor_next;
		|	}
		|
		|	unsigned pa026a = state->fiu_mem_start;
		|	if (state->fiu_omq & 0x02)	// INIT_MRU_D
		|		pa026a |= 0x20;
		|	if (state->fiu_phys_last)
		|		pa026a |= 0x40;
		|	if (state->fiu_write_last)
		|		pa026a |= 0x80;
		|	state->fiu_pa026d = state->fiu_pa026[pa026a];
		|	// INIT_MRU, ACK_REFRESH, START_IF_INCM, START_TAG_RD, PCNTL0-3
		|
		|	if (state->fiu_log_query) {
		|		// PIN_MISS instead of cache_miss_next looks suspicious
		|		// but confirmed on both /200 and /400 FIU boards.
		|		// 20230910/phk
		|		state->fiu_memex = !(!state->fiu_miss && !state->fiu_tmp_csa_oor_next && !state->fiu_scav_trap_next);
		|	} else {
		|		state->fiu_memex = !(!state->fiu_cache_miss && !state->fiu_csa_oor && !state->fiu_scav_trap);
		|	}
		|	mp_restore_rdr = (state->fiu_prmt >> 1) & 1;
		|	bool sel = !((!mp_state_clk_stop && state->fiu_memcyc1) || (mp_state_clk_en && !state->fiu_memcyc1));
		|	if (sel) {
		|		mp_dummy_next = !((state->fiu_prmt >> 0) & 1);
		|	} else {
		|		mp_dummy_next = !state->fiu_dumon;
		|	}
		|			
		|	mp_csa_wr = !(mp_mem_abort_l && mp_mem_abort_el && !(state->fiu_logrwn || (state->fiu_mcntl & 1)));
		|	if (mp_adr_oe & 0x1) {
		|		bool inc_mar = (state->fiu_prmt >> 3) & 1;
		|		unsigned inco = state->fiu_moff & 0x1f;
		|		if (inc_mar && inco != 0x1f)
		|			inco += 1;
		|
		|		mp_adr_bus = (uint64_t)state->fiu_srn << 32;
		|		mp_adr_bus |= state->fiu_sro & 0xfffff000;
		|		mp_adr_bus |= (inco & 0x1f) << 7;
		|		mp_adr_bus |= state->fiu_oreg;
		|		mp_spc_bus = (state->fiu_sro >> 4) & 7;
		|	}
		|
		|	state->fiu_lcntl = state->fiu_mcntl;
		|	state->fiu_drive_mru = state->fiu_init_mru_d;
		|	state->fiu_memcnd = (state->fiu_pa025d >> 4) & 1;	// CM_CTL0
		|	state->fiu_cndtru = (state->fiu_pa025d >> 3) & 1;	// CM_CTL1
		|	mp_mem_cond= !(state->fiu_memcnd);
		|	mp_mem_cond_pol = !(state->fiu_cndtru);
		|			
		|	if (state->fiu_memcyc1) {
		|		mp_mem_ctl= state->fiu_lcntl;
		|	} else {
		|		mp_mem_ctl= state->fiu_pa026d & 0xf;
		|	}
		|	bool inc_mar = (state->fiu_prmt >> 3) & 1;
		|	state->fiu_page_crossing_next = (
		|		state->fiu_condsel != 0x6a) && (// sel_pg_xing
		|		state->fiu_condsel != 0x6e) && (// sel_incyc_px
		|		(
		|			(state->fiu_page_xing) ||
		|			(!state->fiu_page_xing && inc_mar && (state->fiu_moff & 0x1f) == 0x1f)
		|		)
		|	);
		|	mp_mem_continue= !((state->fiu_pa025d >> 5) & 1);
		|	state->fiu_uev10_page_x = !(mp_uevent_enable && state->fiu_page_xing);
		|	if (mp_uevent_enable && state->fiu_page_xing) {
		|		mp_seq_uev |= UEV_PAGE_X;
		|	} else {
		|		mp_seq_uev &= ~UEV_PAGE_X;
		|	}
		|	state->fiu_uev0_memex = !(mp_uevent_enable && state->fiu_memex);
		|	if (mp_uevent_enable && state->fiu_memex) {
		|		mp_seq_uev |= UEV_MEMEX;
		|	} else {
		|		mp_seq_uev &= ~UEV_MEMEX;
		|	}
		|	mp_clock_stop_0 = state->fiu_uev10_page_x && state->fiu_uev0_memex;
		|}
		|
		|void
		|SCM_«mmm» ::
		|fiu_q4(void)
		|{
		|	bool sclk = !mp_state_clk_en;
		|	bool tcsa_clk = (mp_clock_stop && mp_ram_stop && !mp_freeze);
		|	unsigned mar_cntl = mp_mar_cntl;
		|	bool rmarp = (mar_cntl & 0xe) == 0x4;
		|	bool carry, name_match;
		|
		|	unsigned csa = mp_csa_cntl;
		|
		|	do_tivi();
		|	tcsa(tcsa_clk);
		|	if (sclk) {
		|		if (UIR_FIU_LDMDR || !UIR_FIU_TCLK || !UIR_FIU_VCLK) {
		|			rotator(sclk);
		|		}
		|
		|		if (!UIR_FIU_OCLK) {			// Q4~^
		|			if (UIR_FIU_ORSR) {			// UCODE
		|				state->fiu_oreg = UIR_FIU_OL;
		|			} else {
		|				state->fiu_oreg = mp_adr_bus & 0x7f;
		|			}
		|		}
		|
		|		if (mar_cntl == 5) {
		|			state->fiu_refresh_reg = state->fiu_ti_bus;
		|			state->fiu_marh &= 0xffffffffULL;
		|			state->fiu_marh |= (state->fiu_refresh_reg & 0xffffffff00000000ULL);
		|			state->fiu_marh ^= 0xffffffff00000000ULL;
		|		}
		|
		|		unsigned lfrc;
		|		lfrc = UIR_FIU_LFRC;
		|
		|		switch(lfrc) {
		|		case 0:
		|			state->fiu_lfreg = (((state->fiu_vi_bus >> BUS64_LSB(31)) & 0x3f) + 1) & 0x3f;
		|			if ((state->fiu_ti_bus >> BUS64_LSB(36)) & 1)
		|				state->fiu_lfreg |= (1 << 6);
		|			else if (!((state->fiu_vi_bus >> BUS64_LSB(25)) & 1))
		|				state->fiu_lfreg |= (1 << 6);
		|			state->fiu_lfreg ^= 0x7f;
		|			break;
		|		case 1:
		|			state->fiu_lfreg = UIR_FIU_LFL;
		|			break;
		|		case 2:
		|			state->fiu_lfreg = (state->fiu_ti_bus >> BUS64_LSB(48)) & 0x3f;
		|			if ((state->fiu_ti_bus >> BUS64_LSB(36)) & 1)
		|				state->fiu_lfreg |= (1 << 6);
		|			state->fiu_lfreg = state->fiu_lfreg ^ 0x7f;
		|			break;
		|		case 3:	// No load
		|			break;
		|		}
		|
		|		state->fiu_marh &= ~(0x3fULL << 15);
		|		state->fiu_marh |= (state->fiu_lfreg & 0x3f) << 15;
		|		state->fiu_marh &= ~(1ULL << 27);
		|		state->fiu_marh |= ((state->fiu_lfreg >> 6) & 1) << 27;
		|		if (state->fiu_lfreg != 0x7f)
		|			state->fiu_lfreg |= 1<<7;
		|
		|{
		|		unsigned csacntl0 = (state->fiu_typwcsram[mp_nua_bus] >> 1) & 7;
		|		unsigned csacntl1 = (state->fiu_typuir >> 1) & 6;
		|		state->fiu_pdt = (csacntl0 == 7) && (csacntl1 == 0);
		|}
		|		state->fiu_nve = mp_csa_nve;
		|		if (!(csa >> 2)) {
		|			state->fiu_pdreg = state->fiu_ctopo;
		|		}
		|	}
		|
		|	unsigned dif;
		|
		|	if (state->fiu_pdt) {
		|		carry = state->fiu_ctopo <= state->fiu_pdreg;
		|		dif = ~0xfffff + state->fiu_pdreg - state->fiu_ctopo;
		|	} else {
		|		carry = state->fiu_moff <= state->fiu_ctopo;
		|		dif = ~0xfffff + state->fiu_ctopo - state->fiu_moff;
		|	}
		|	dif &= 0xfffff;
		|
		|	name_match = 
		|		    (state->fiu_ctopn != state->fiu_srn) ||
		|		    ((state->fiu_sro & 0xf8000070 ) != 0x10);
		|
		|	state->fiu_in_range = (!state->fiu_pdt && name_match) || (dif & 0xffff0);
		|
		|	state->fiu_hit_offset = (0xf + state->fiu_nve - (dif & 0xf)) & 0xf;
		|
		|	uint64_t adr = 0;
		|	adr = mp_adr_bus;
		|	bool load_mar = (state->fiu_prmt >> 4) & 1;
		|			
		|	if (sclk && load_mar) {
		|		state->fiu_srn = adr >> 32;
		|		state->fiu_sro = adr & 0xffffff80;
		|		state->fiu_sro |= mp_spc_bus << 4;
		|		state->fiu_sro |= 0xf;
		|	}
		|	state->fiu_moff = (state->fiu_sro >> 7) & 0xffffff;
		|			
		|	state->fiu_nmatch =
		|	    (state->fiu_ctopn != state->fiu_srn) ||
		|	    ((state->fiu_sro & 0xf8000070 ) != 0x10);
		|			
		|	if (sclk && (csa == 0)) {
		|		state->fiu_ctopn = adr >> 32;
		|		state->fiu_nmatch =
		|		    (state->fiu_ctopn != state->fiu_srn) ||
		|		    ((state->fiu_sro & 0xf8000070 ) != 0x10);
		|	}
		|			
		|	if (sclk && !(csa >> 2)) {
		|		if (csa <= 1) {
		|			state->fiu_ctopo = adr >> 7;
		|		} else if (!(csa & 1)) {
		|			state->fiu_ctopo += 1;
		|		} else {
		|			state->fiu_ctopo += 0xfffff;
		|		}
		|		state->fiu_ctopo &= 0xfffff;
		|			
		|	}
		|			
		|	if (state->fiu_mem_start == 0x06) {
		|		mp_refresh_count = state->fiu_ti_bus >> 48;
		|	} else if (mp_refresh_count != 0xffff) {
		|		mp_refresh_count++;
		|	}
		|
		|	bool le_abort = mp_mem_abort_el;
		|	bool e_abort = mp_mem_abort_e;
		|	bool eabrt = !(e_abort && le_abort);
		|	bool l_abort = mp_mem_abort_l;
		|	bool idum;
		|	bool sel = !((!mp_state_clk_stop && state->fiu_memcyc1) || (mp_state_clk_en && !state->fiu_memcyc1));
		|	if (sel) {
		|		idum = (state->fiu_prmt >> 5) & 1;
		|	} else {
		|		idum = state->fiu_dumon;
		|	}
		|	state->fiu_state0 = (state->fiu_pa025d >> 7) & 1;
		|	state->fiu_state1 = (state->fiu_pa025d >> 6) & 1;
		|	state->fiu_labort = !(l_abort && le_abort);
		|	state->fiu_e_abort_dly = eabrt;
		|	state->fiu_pcntl_d = state->fiu_pa026d & 0xf;
		|	state->fiu_dumon = idum;
		|	state->fiu_csaht = !mp_csa_hit;
		|
		|	if (!mp_sf_stop) {
		|		bool cache_miss_next = state->fiu_cache_miss;
		|		if (state->fiu_condsel == 0x6b) {		// CACHE_MISS
		|			cache_miss_next = false;
		|		} else if (rmarp) {
		|			cache_miss_next = (state->fiu_ti_bus >> BUS64_LSB(35)) & 1;
		|		} else if (state->fiu_log_query) {
		|			cache_miss_next = state->fiu_miss;
		|		}
		|		state->fiu_scav_trap = state->fiu_scav_trap_next;
		|		state->fiu_cache_miss = cache_miss_next;
		|		state->fiu_csa_oor = state->fiu_tmp_csa_oor_next;
		|								
		|		if (rmarp) {
		|			state->fiu_mar_modified = (state->fiu_ti_bus >> BUS64_LSB(39)) & 1;
		|		} else if (state->fiu_condsel == 0x6d) {
		|			state->fiu_mar_modified = 1;
		|		} else if (state->fiu_omf20) {
		|			state->fiu_mar_modified = le_abort;
		|		} else if (!state->fiu_memstart && le_abort) {
		|			state->fiu_mar_modified = le_abort;
		|		}
		|		if (rmarp) {
		|			state->fiu_incmplt_mcyc = (state->fiu_ti_bus >> BUS64_LSB(40)) & 1;
		|		} else if (state->fiu_mem_start == 0x12) {
		|			state->fiu_incmplt_mcyc = true;
		|		} else if (state->fiu_memcyc1) {
		|			state->fiu_incmplt_mcyc = le_abort;
		|		}
		|		if (rmarp) {
		|			state->fiu_phys_last = (state->fiu_ti_bus >> BUS64_LSB(37)) & 1;
		|			state->fiu_write_last = (state->fiu_ti_bus >> BUS64_LSB(38)) & 1;
		|		} else if (state->fiu_memcyc1) {
		|			state->fiu_phys_last = state->fiu_phys_ref;
		|			state->fiu_write_last = (state->fiu_mcntl & 1);
		|		}
		|								
		|		state->fiu_log_query = !(state->fiu_labort || state->fiu_logrwn);
		|										
		|		state->fiu_omf20 = (state->fiu_memcyc1 && ((state->fiu_prmt >> 3) & 1) && !mp_state_clk_en);
		|		
		|		if (state->fiu_memcyc1)
		|			state->fiu_mctl_is_read = !(state->fiu_lcntl & 1);
		|		else
		|			state->fiu_mctl_is_read = !(state->fiu_pa026d & 1);
		|								
		|		state->fiu_logrw_d = state->fiu_logrw;
		|	}
		|
		|	if (!mp_state_clk_en) {
		|		state->fiu_omq = 0;
		|		state->fiu_omq |= (state->fiu_pa027d & 3) << 2;
		|		state->fiu_omq |= ((state->fiu_pa027d >> 5) & 1) << 1;
		|		if (rmarp) {
		|			state->fiu_page_xing = (state->fiu_ti_bus >> BUS64_LSB(34)) & 1;
		|		} else {
		|			state->fiu_page_xing = (state->fiu_page_crossing_next);
		|		}
		|		state->fiu_init_mru_d = (state->fiu_pa026d >> 7) & 1;
		|	}
		|	state->fiu_csa_oor_next = !(carry || name_match);
		|
		|	if (!mp_sf_stop) {
		|		state->fiu_uir = state->fiu_wcsram[mp_nua_bus];
		|		state->fiu_typuir = state->fiu_typwcsram[mp_nua_bus];
		|	}
		|}
		|''')

    def sensitive(self):
        yield "PIN_Q2"
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	bool q1pos = PIN_Q2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q4pos = PIN_Q4.posedge();
		|
		|	state->fiu_condsel = mp_cond_sel;
		|
		|	unsigned mar_cntl = mp_mar_cntl;
		|
		|	unsigned pa028a = mar_cntl << 5;
		|	pa028a |= state->fiu_incmplt_mcyc << 4;
		|	pa028a |= state->fiu_e_abort_dly << 3;
		|	pa028a |= state->fiu_state1 << 2;
		|	pa028a |= state->fiu_mctl_is_read << 1;
		|	pa028a |= state->fiu_dumon;
		|	state->fiu_prmt = state->fiu_pa028[pa028a];
		|	state->fiu_prmt ^= 0x02;
		|	state->fiu_prmt &= 0x7b;
		|
		|	state->fiu_mem_start = UIR_FIU_MSTRT ^ 0x1e;
		|
		|	if (q1pos) {
		|		fiu_q1();
		|	} else if (q2pos) {
		|		fiu_q2();
		|	} else if (q4pos) {
		|		fiu_q4();
		|	}
		|
		|	if ((!mp_fiut_oe || !mp_fiuv_oe) && !q4pos) {
		|		do_tivi();
		|		if (!mp_fiut_oe) {
		|			mp_typ_bus = ~state->fiu_ti_bus;
		|		}
		|		if (!mp_fiuv_oe) {
		|			mp_val_bus = ~state->fiu_vi_bus;
		|		}
		|	}
		|
		|	if (state->fiu_condsel == 0x6b) {
		|		if (q2pos) {
		|			fiu_conditions();
		|		}
		|	} else if (!q4pos && (60 <= state->fiu_condsel && state->fiu_condsel <= 0x6f)) {
		|		fiu_conditions();
		|	}
		|	if (!q4pos) {
		|		tcsa(false);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("FIU", PartModelDQ("FIU", FIU))
