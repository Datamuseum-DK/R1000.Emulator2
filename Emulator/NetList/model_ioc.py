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
   IOC Dummy register
   ==================

'''

from part import PartModelDQ, PartFactory

class IOC(PartFactory):
    ''' IOC Dummy register '''

    autopin = True

    def extra(self, file):
        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.
        file.write('\t#define XIOP_VARIANT 1\n')
        self.scm.sf_cc.include("Iop/iop_sc_68k20.hh")
        file.include("Infra/vend.h")

    def state(self, file):
        file.fmt('''
		|	uint64_t ioc_dummy_typ, ioc_dummy_val;
		|
		|	unsigned ioc_iack;
		|	struct ioc_sc_bus_xact *ioc_xact;
		|	unsigned ioc_fffff400;
		|	bool ioc_request_int_en;
		|	bool ioc_response_int_en;
		|	unsigned ioc_reqfifo[1024], ioc_reqwrp, ioc_reqrdp, ioc_reqreg;
		|	unsigned ioc_rspfifo[1024], ioc_rspwrp, ioc_rsprdp;
		|	bool ioc_cpu_running;
		|	uint8_t *ioc_ram;
		|	unsigned ioc_acnt;
		|	unsigned ioc_areg;
		|	unsigned ioc_rdata;
		|	unsigned ioc_rtc;
		|
		|	unsigned ioc_prescaler;
		|	uint16_t ioc_delay, ioc_slice;
		|	bool ioc_slice_ev, ioc_delay_ev;
		|	bool ioc_sen, ioc_den, ioc_ten;
		|	uint8_t ioc_pb011[32];
		|	bool ioc_dumen;
		|	bool ioc_csa_hit;
		|	uint16_t *ioc_tram;
		|	uint64_t *ioc_wcsram;
		|	uint64_t ioc_uir;
		|
		|#define UIR_IOC_ULWDR	((state->ioc_uir >> 13) & 0x1)
		|#define UIR_IOC_RAND	((state->ioc_uir >>  8) & 0x1f)
		|#define UIR_IOC_AEN	((state->ioc_uir >>  6) & 0x3)
		|#define UIR_IOC_FEN	((state->ioc_uir >>  4) & 0x3)
		|#define UIR_IOC_TVBS	((state->ioc_uir >>  0) & 0xf)
		|''');


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->ioc_pb011, sizeof state->ioc_pb011, "PB011");
		|	state->ioc_wcsram = (uint64_t*)CTX_GetRaw("IOC_WCS", sizeof(uint64_t) << 14);
		|	state->ioc_tram = (uint16_t*)CTX_GetRaw("IOC_TRAM", sizeof(uint16_t) * 2049);
		|
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ioc_ram = (uint8_t*)(c1 + 1);
		|	is_tracing = false;
		|''')

    def priv_decl(self, file):
        ''' further private decls '''
        file.fmt('''
		|	bool is_tracing = 0;
		|       void do_xact(void);
		|       void ioc_cond(void);
		|       void ioc_h1(void);
		|       void ioc_q2(void);
		|       void ioc_q4(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|do_xact(void)
		|{
		|	if (!state->ioc_xact)
		|		state->ioc_xact = ioc_sc_bus_get_xact();
		|
		|	if (!state->ioc_xact)
		|		return;
		|
		|	if (state->ioc_xact->sc_state == 200 && state->ioc_xact->address == 0xfffff100) {
		|		/* READ GET REQUEST */
		|		state->ioc_xact->data = state->ioc_reqreg;
		|		TRACE("RD FIFO GET REQUEST " << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff200) {
		|		/* WRITE FRONT PANEL */
		|		TRACE("WR FP " << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff300) {
		|		/* WRITE SENSE TEST */
		|		TRACE("WR SENSE TEST " << std::hex << state->ioc_xact->data);
		|		state->ioc_request_int_en = (state->ioc_xact->data >> 1) & 1;
		|		state->ioc_response_int_en = (state->ioc_xact->data >> 0) & 1;
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff400) {
		|		/* WRITE CONTROL */
		|		TRACE("WR CONTROL " << std::hex << state->ioc_xact->data);
		|		state->ioc_fffff400 = (state->ioc_xact->data >> 16) & 0xf;
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff500) {
		|		/* WRITE FIFO INIT */
		|		TRACE("WR FIFO INIT " << std::hex << state->ioc_xact->data);
		|		state->ioc_reqwrp = state->ioc_reqrdp = 0;
		|		state->ioc_rspwrp = state->ioc_rsprdp = 0;
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff600) {
		|		/* WRITE FIFO CPU RSP */
		|		TRACE("WR FIFO CPU RSP " << std::hex << state->ioc_xact->data);
		|		state->ioc_rspfifo[state->ioc_rspwrp++] = state->ioc_xact->data;
		|		state->ioc_rspwrp &= 0x3ff;
		|
		|		TRACE(
		|			"WR FIFO RSP " << std::hex << state->ioc_xact->data
		|			<< " wr " << state->ioc_rspwrp
		|			<< " rd " << state->ioc_rsprdp
		|		);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff700) {
		|		/* WRITE CPU REQUEST */
		|		state->ioc_reqreg = state->ioc_reqfifo[state->ioc_reqrdp++];
		|		state->ioc_reqrdp &= 0x3ff;
		|		TRACE(
		|			"WR FIFO CPU REQUEST " << std::hex << state->ioc_reqreg
		|				<< " wr " << state->ioc_reqwrp
		|				<< " rd " << state->ioc_reqrdp
		|		);
		|
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	if (state->ioc_xact->sc_state == 200 && state->ioc_xact->address == 0xfffff800) {
		|		/* READ STATUS */
		|		state->ioc_xact->data 			   = 0x9000ff80;
		|		if (state->ioc_cpu_running) {
		|			state->ioc_xact->data |= 0x40000000;
		|		}
		|		// if (PIN_PROTE)			state->ioc_xact->data |= 0x02000000;
		|		if (state->ioc_fffff400 & 8)	state->ioc_xact->data |= 0x00080000; // IOP.INTR_EN
		|		if (state->ioc_fffff400 & 4)	state->ioc_xact->data |= 0x00040000; // GOOD_PARITY
		|		if (state->ioc_fffff400 & 2)	state->ioc_xact->data |= 0x00020000; // PERR_ENABLE
		|		if (state->ioc_fffff400 & 1)	state->ioc_xact->data |= 0x00010000; // IOP.NEXT_CLK
		|		state->ioc_xact->data |= 0x7 << 4;
		|		if (!mp_key_switch)		state->ioc_xact->data |= 0x00000008;
		|		state->ioc_xact->data |= state->ioc_iack << 0;
		|
		|		TRACE("RD STATUS " << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffff900) {
		|		/* WRITE CLEAR BERR */
		|		TRACE("WR CLEAR BERR " << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffffe00) {
		|		/* WRITE CPU CONTROL */
		|		TRACE("WR CPU CONTROL " << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|	if (state->ioc_xact->sc_state == 100 && state->ioc_xact->address == 0xfffffd00) {
		|		TRACE("WR fffffd00" << std::hex << state->ioc_xact->data);
		|		ioc_sc_bus_done(&state->ioc_xact);
		|		return;
		|	}
		|
		|	TRACE(
		|		<< "BXPA state= "
		|		<< state->ioc_xact->sc_state
		|		<< " adr= "
		|		<< std::hex << state->ioc_xact->address
		|		<< " data= "
		|		<< std::hex << state->ioc_xact->data
		|		<< " width = "
		|		<< state->ioc_xact->width
		|		<< " write= "
		|		<< state->ioc_xact->is_write
		|	);
		|}
		|
		|void
		|SCM_«mmm» ::
		|ioc_cond(void)
		|{
		|	switch (mp_cond_sel) {
		|	case 0x78:
		|		mp_condx0 = true; // state->ioc_multibit_error;
		|		break;
		|	case 0x79:
		|		{
		|		uint64_t tmp = mp_typ_bus & 0x80000047;
		|		mp_condx0 = tmp == 0x80000000 || tmp == 0x80000040 || tmp == 0x80000044;
		|		}
		|		break;
		|	case 0x7a:
		|		mp_condx0 = true; // state->ioc_checkbit_error;
		|		break;
		|	case 0x7b:
		|		mp_condx0 = state->ioc_reqwrp != state->ioc_reqrdp;
		|		break;
		|	case 0x7c:
		|		mp_condx0 = state->ioc_acnt == 0xfff;
		|		break;
		|	case 0x7d:
		|		mp_condx0 = true;
		|		break;
		|	case 0x7e:
		|		mp_condx0 = state->ioc_rspwrp != state->ioc_rsprdp;
		|		break;
		|	case 0x7f:
		|		mp_condx0 = true;
		|		break;
		|	}
		|}
		|
		|void
		|SCM_«mmm» ::
		|ioc_h1(void)
		|{
		|	if (state->ioc_rspwrp != state->ioc_rsprdp) {
		|		mp_macro_event |= 0x8;
		|	} else {
		|		mp_macro_event &= ~0x8;
		|	}
		|
		|	mp_load_wdr = UIR_IOC_ULWDR;
		|
		|	if (!mp_ioctv_oe) {
		|		mp_val_bus = state->ioc_dummy_val;
		|
		|		switch (UIR_IOC_RAND) {
		|		case 0x05:
		|			mp_typ_bus = (uint64_t)(state->ioc_slice) << 48;
		|			mp_typ_bus |= (uint64_t)(state->ioc_delay) << 32;
		|			mp_typ_bus |= ((uint64_t)state->ioc_rtc) << 16;
		|			mp_typ_bus |= state->ioc_rspfifo[state->ioc_rsprdp];
		|			break;
		|		case 0x08:
		|		case 0x09:
		|		case 0x19:
		|			mp_typ_bus = (uint64_t)(state->ioc_slice) << 48;
		|			mp_typ_bus |= (uint64_t)(state->ioc_delay) << 32;
		|			mp_typ_bus |= ((uint64_t)state->ioc_rtc) << 16;
		|			break;
		|		case 0x16:
		|		case 0x1c:
		|		case 0x1d:
		|			mp_typ_bus = ((uint64_t)state->ioc_rdata) << 32;
		|			mp_typ_bus |= ((uint64_t)state->ioc_rtc) << 16;
		|			break;
		|		default:
		|			mp_typ_bus = state->ioc_dummy_typ;
		|			break;
		|		}
		|	}
		|	ioc_cond();
		|}
		|
		|void
		|SCM_«mmm» ::
		|ioc_q2(void)
		|{
		|	unsigned rand = UIR_IOC_RAND;
		|	if (state->ioc_slice_ev && !state->ioc_ten) {
		|		mp_macro_event |= 0x2;
		|	}
		|	if (rand == 0x0a) {
		|		mp_macro_event &= ~0x2;
		|	}
		|	if (state->ioc_delay_ev && !state->ioc_ten) {
		|		mp_macro_event |= 0x1;
		|	}
		|	if (rand == 0x0b) {
		|		mp_macro_event &= ~0x1;
		|	}
		|	uint64_t tmp = (mp_typ_bus >> 7) & 0xfffff;
		|	bool below = (tmp >= 0xc);
		|	bool exit_proc = rand != 0x12;
		|	mp_below_tcp = !(below || exit_proc);
		|	ioc_cond();
		|}
		|
		|void
		|SCM_«mmm» ::
		|ioc_q4(void)
		|{
		|	bool sclk_pos = mp_clock_stop;
		|	unsigned rand = UIR_IOC_RAND;
		|	uint64_t typ, val;
		|	typ = mp_typ_bus;
		|	val = mp_val_bus;
		|
		|	if (sclk_pos) {
		|		if (rand == 0x23)
		|			state->ioc_cpu_running = true;
		|		if (rand == 0x24)
		|			state->ioc_cpu_running = false;
		|	}
		|
		|	if ((state->ioc_request_int_en &&
		|	    state->ioc_reqrdp != state->ioc_reqwrp) && state->ioc_iack != 6) {
		|		state->ioc_iack = 6;
		|		ioc_sc_bus_start_iack(6);
		|	}
		|	if ((!state->ioc_request_int_en ||
		|	    state->ioc_reqrdp == state->ioc_reqwrp) && state->ioc_iack != 7) {
		|		state->ioc_iack = 7;
		|		ioc_sc_bus_start_iack(7);
		|	}
		|
		|	do_xact();
		|
		|	if (sclk_pos && rand == 0x04) {
		|		state->ioc_reqfifo[state->ioc_reqwrp++] = typ & 0xffff;
		|		state->ioc_reqwrp &= 0x3ff;
		|	}
		|
		|
		|	if (sclk_pos && rand == 0x05) {
		|		state->ioc_rsprdp++;
		|		state->ioc_rsprdp &= 0x3ff;
		|	}
		|
		|	if (sclk_pos) {
		|		unsigned adr = (state->ioc_areg | state->ioc_acnt) << 2;
		|		assert(adr < (512<<10));
		|
		|		if ((rand == 0x1c) || (rand == 0x1d)) {
		|			state->ioc_rdata = vbe32dec(state->ioc_ram + adr);
		|		}
		|
		|		if ((rand == 0x1e) || (rand == 0x1f)) {
		|			uint32_t data = typ >> 32;
		|			vbe32enc(state->ioc_ram + adr, data);
		|		}
		|
		|		if (rand == 0x01) {
		|			state->ioc_acnt = (typ >> 2) & 0x00fff;
		|			state->ioc_areg = (typ >> 2) & 0x1f000;
		|		}
		|
		|		if ((rand == 0x1c) || (rand == 0x1e)) {
		|			state->ioc_acnt += 1;
		|			state->ioc_acnt &= 0xfff;
		|		}
		|	}
		|
		|	if (sclk_pos && rand == 0x08) {
		|		state->ioc_rtc = 0;
		|	}
		|	if (!mp_sf_stop && rand != 0x08) {
		|		state->ioc_rtc++;
		|		state->ioc_rtc &= 0xffff;
		|	}
		|								
		|	state->ioc_prescaler++;
		|	state->ioc_ten = state->ioc_prescaler != 0xf;
		|	state->ioc_prescaler &= 0xf;
		|	if (sclk_pos) {
		|		if (rand == 0x0c) {
		|			state->ioc_sen = false;
		|		}
		|		if (rand == 0x0d) {
		|			state->ioc_sen = true;
		|		}
		|		if (rand == 0x0e) {
		|			state->ioc_den = false;
		|		}
		|		if (rand == 0x0f) {
		|			state->ioc_den = true;
		|		}
		|	}
		|
		|	state->ioc_slice_ev= state->ioc_slice == 0xffff;
		|	if (rand == 0x06) {
		|		uint64_t tmp = typ;
		|		tmp >>= 32;
		|		state->ioc_slice = tmp >> 16;
		|		TRACE(<< " LD " << std::hex << state->ioc_slice);
		|	} else 	if (!state->ioc_sen && !state->ioc_ten) {
		|		state->ioc_slice++;
		|	}
		|
		|	state->ioc_delay_ev= state->ioc_delay == 0xffff;
		|	if (rand == 0x07) {
		|		uint64_t tmp = typ;
		|		tmp >>= 32;
		|		state->ioc_delay = tmp;
		|	} else if (!state->ioc_den && !state->ioc_ten) {
		|		state->ioc_delay++;
		|	}
		|	bool rddum = (UIR_IOC_TVBS < 0xc) || !state->ioc_dumen;
		|	if (rddum && !mp_restore_rdr) {
		|		state->ioc_dummy_typ = typ;
		|		state->ioc_dummy_val = val;
		|	}
		|
		|	if (!mp_sf_stop) {
		|		state->ioc_uir = state->ioc_wcsram[mp_nua_bus];
		|		assert (state->ioc_uir <= 0xffff);
		|		mp_nxt_adr_oe = 1 << UIR_IOC_AEN;
		|		mp_nxt_fiu_oe = 1 << UIR_IOC_FEN;
		|		state->ioc_dumen = !mp_dummy_next;
		|		state->ioc_csa_hit = !mp_csa_hit;
		|		unsigned tvbs = UIR_IOC_TVBS;
		|
		|		uint16_t tdat = mp_nua_bus;
		|		if (!sclk_pos)
		|			tdat |= 0x8000;
		|		if (state->ioc_csa_hit)
		|			tdat |= 0x4000;
		|		uint16_t tptr = state->ioc_tram[2048];
		|		state->ioc_tram[tptr] = tdat;
		|		if (mp_ioc_trace) {
		|			tptr += 1;
		|			tptr &= 0x7ff;
		|			state->ioc_tram[2048] = tptr;
		|		}
		|		mp_nxt_seqtv_oe = true;
		|		mp_nxt_fiuv_oe = true;
		|		mp_nxt_fiut_oe = true;
		|		mp_nxt_memv_oe = true;
		|		mp_nxt_memtv_oe = true;
		|		mp_nxt_ioctv_oe = true;
		|		mp_nxt_valv_oe = true;
		|		mp_nxt_typt_oe = true;
		|		switch (tvbs) {
		|		case 0x0: mp_nxt_valv_oe = false; mp_nxt_typt_oe = false; break;
		|		case 0x1: mp_nxt_fiuv_oe = false; mp_nxt_typt_oe = false; break;
		|		case 0x2: mp_nxt_valv_oe = false; mp_nxt_fiut_oe = false; break;
		|		case 0x3: mp_nxt_fiuv_oe = false; mp_nxt_fiut_oe = false; break;
		|		case 0x4: mp_nxt_ioctv_oe = false; break;
		|		case 0x5: mp_nxt_seqtv_oe = false; break;
		|		case 0x8:
		|		case 0x9:
		|			mp_nxt_memv_oe = false; mp_nxt_typt_oe = false; break;
		|		case 0xa:
		|		case 0xb:
		|			mp_nxt_memv_oe = false; mp_nxt_fiut_oe = false; break;
		|		case 0xc:
		|		case 0xd:
		|		case 0xe:
		|		case 0xf:
		|			if (state->ioc_dumen) {
		|				mp_nxt_ioctv_oe = false;
		|			} else if (state->ioc_csa_hit) {
		|				mp_nxt_typt_oe = false;
		|				mp_nxt_valv_oe = false;
		|			} else {
		|				mp_nxt_memtv_oe = false;
		|				mp_nxt_memv_oe = false;
		|			}
		|			break;
		|		default:
		|			break;
		|		}
		|	}
		|}
		|''')

    def sensitive(self):
        yield "PIN_H2.neg()"
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 2) {
		|		state->ioc_dummy_typ = -1;
		|		state->ioc_dummy_val = -1;
		|	}
		|
		|	if (state->ctx.activations < 1000) {
		|		state->ioc_sen = true;
		|		state->ioc_den = true;
		|	}
		|
		|	if (mp_ioc_trace && ((mp_sync_freeze & 0x3) == 0) && !is_tracing) {
		|		is_tracing = true;
		|		ALWAYS_TRACE(<< " IS TRACING");
		|	}
		|	if (mp_ioc_trace && (mp_sync_freeze & 0x3) && is_tracing) {
		|		is_tracing = true;
		|		mp_ioc_trace = 0;
		|		ALWAYS_TRACE(<< " STOP TRACING");
		|	}
		|
		|	if (PIN_H2.negedge()) { 
		|		ioc_h1();
		|	} else if (PIN_Q2.posedge()) {
		|		ioc_q2();
		|	} else if (PIN_Q4.posedge()) {
		|		ioc_q4();
		|	}
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("IOC", PartModelDQ("IOC", IOC))

'''
   TYP A-side mux+latch
   ====================

TYP drivers

IOP     CPURAM  RTC     CTR     CBBUF
--------------------------------------------- 
-       X       -       X       -       0-31
-       -       X       -       -       32-47
X       -       -       -       X       48-63
---------------------------------------------
0x05    -       0x05    0x05    -       XXX

-       -       0x08    0x08    0x8     XXX
-       -       0x09    0x09    0x9     XXX
-       -       0x19    0x19    0x19    XXX

-       0x16    0x16    -       0x16    XXX
-       0x1c    0x1c    -       0x1c    XXX
-       0x1d    0x1d    -       0x1d    XXX
---------------------------------------------

'''
