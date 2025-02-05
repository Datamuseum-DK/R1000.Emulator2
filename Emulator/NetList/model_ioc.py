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
		|	uint64_t dummy_typ, dummy_val;
		|
		|	unsigned iack;
		|	struct ioc_sc_bus_xact *xact;
		|	unsigned fffff400;
		|	bool request_irq;
		|	bool response_irq;
		|	bool request_int_en;
		|	bool response_int_en;
		|	unsigned reqfifo[1024], reqwrp, reqrdp, reqreg;
		|	unsigned rspfifo[1024], rspwrp, rsprdp, rspreg;
		|	bool cpu_running;
		|	uint8_t *ram;
		|	unsigned acnt;
		|	unsigned areg;
		|	unsigned rdata;
		|	unsigned rtc;
		|
		|	unsigned prescaler;
		|	uint16_t delay, slice;
		|	bool slice_ev, delay_ev;
		|	bool sen, den, ten;
		|	uint8_t pb011[32];
		|	bool pfr;
		|	bool dumen;
		|	bool csa_hit;
		|	uint16_t *tram;
		|	uint64_t *wcsram;
		|	uint64_t uir;
		|
		|#define UIR_ULWDR	((state->uir >> 13) & 0x1)
		|#define UIR_RAND	((state->uir >>  8) & 0x1f)
		|#define UIR_AEN	((state->uir >>  6) & 0x3)
		|#define UIR_FEN	((state->uir >>  4) & 0x3)
		|#define UIR_TVBS	((state->uir >>  0) & 0xf)
		|''');


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(), state->pb011, sizeof state->pb011, "PB011");
		|	state->wcsram = (uint64_t*)CTX_GetRaw("IOC_WCS", sizeof(uint64_t) << 14);
		|	state->tram = (uint16_t*)CTX_GetRaw("IOC_TRAM", sizeof(uint16_t) * 2049);
		|
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ram = (uint8_t*)(c1 + 1);
		|	is_tracing = false;
		|''')

    def priv_decl(self, file):
        ''' further private decls '''
        file.fmt('''
		|	bool is_tracing;
		|       void do_xact(void);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|do_xact(void)
		|{
		|	if (!state->xact)
		|		state->xact = ioc_sc_bus_get_xact();
		|
		|	if (!state->xact)
		|		return;
		|
		|	if (state->xact->sc_state == 200 && state->xact->address == 0xfffff100) {
		|		/* READ GET REQUEST */
		|		state->xact->data = state->reqreg;
		|		TRACE("RD FIFO GET REQUEST " << std::hex << state->xact->data);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff200) {
		|		/* WRITE FRONT PANEL */
		|		TRACE("WR FP " << std::hex << state->xact->data);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff300) {
		|		/* WRITE SENSE TEST */
		|		TRACE("WR SENSE TEST " << std::hex << state->xact->data);
		|		state->request_int_en = (state->xact->data >> 1) & 1;
		|		state->response_int_en = (state->xact->data >> 0) & 1;
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff400) {
		|		/* WRITE CONTROL */
		|		TRACE("WR CONTROL " << std::hex << state->xact->data);
		|		state->fffff400 = (state->xact->data >> 16) & 0xf;
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff500) {
		|		/* WRITE FIFO INIT */
		|		TRACE("WR FIFO INIT " << std::hex << state->xact->data);
		|		state->reqwrp = state->reqrdp = 0;
		|		state->rspwrp = state->rsprdp = 0;
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff600) {
		|		/* WRITE FIFO CPU RSP */
		|		TRACE("WR FIFO CPU RSP " << std::hex << state->xact->data);
		|		state->rspfifo[state->rspwrp++] = state->xact->data;
		|		state->rspwrp &= 0x3ff;
		|
		|		TRACE(
		|			"WR FIFO RSP " << std::hex << state->xact->data
		|			<< " wr " << state->rspwrp
		|			<< " rd " << state->rsprdp
		|		);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff700) {
		|		/* WRITE CPU REQUEST */
		|		state->reqreg = state->reqfifo[state->reqrdp++];
		|		state->reqrdp &= 0x3ff;
		|		TRACE(
		|			"WR FIFO CPU REQUEST " << std::hex << state->reqreg
		|				<< " wr " << state->reqwrp
		|				<< " rd " << state->reqrdp
		|		);
		|
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	if (state->xact->sc_state == 200 && state->xact->address == 0xfffff800) {
		|		/* READ STATUS */
		|		unsigned tmp;
		|		state->xact->data 			   = 0x9000ff80;
		|		if (state->cpu_running) {
		|			state->xact->data |= 0x40000000;
		|		}
		|		// if (PIN_PROTE)			state->xact->data |= 0x02000000;
		|		if (state->fffff400 & 8)	state->xact->data |= 0x00080000; // IOP.INTR_EN
		|		if (state->fffff400 & 4)	state->xact->data |= 0x00040000; // GOOD_PARITY
		|		if (state->fffff400 & 2)	state->xact->data |= 0x00020000; // PERR_ENABLE
		|		if (state->fffff400 & 1)	state->xact->data |= 0x00010000; // IOP.NEXT_CLK
		|		BUS_EXTID_READ(tmp);
		|		state->xact->data |= tmp << 4;
		|		if (!PIN_KEY)			state->xact->data |= 0x00000008;
		|		state->xact->data |= state->iack << 0;
		|
		|		TRACE("RD STATUS " << std::hex << state->xact->data);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffff900) {
		|		/* WRITE CLEAR BERR */
		|		TRACE("WR CLEAR BERR " << std::hex << state->xact->data);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffffe00) {
		|		/* WRITE CPU CONTROL */
		|		TRACE("WR CPU CONTROL " << std::hex << state->xact->data);
		|		output.orst = 0;
		|		output.z_orst = state->xact->data & 1;
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|	if (state->xact->sc_state == 100 && state->xact->address == 0xfffffd00) {
		|		TRACE("WR fffffd00" << std::hex << state->xact->data);
		|		ioc_sc_bus_done(&state->xact);
		|		return;
		|	}
		|
		|	TRACE(
		|		<< "BXPA state= "
		|		<< state->xact->sc_state
		|		<< " adr= "
		|		<< std::hex << state->xact->address
		|		<< " data= "
		|		<< std::hex << state->xact->data
		|		<< " width = "
		|		<< state->xact->width
		|		<< " write= "
		|		<< state->xact->is_write
		|	);
		|}
		|''')

    def sensitive(self):
        yield "PIN_H2.neg()"
        yield "PIN_Q2.pos()"
        yield "PIN_Q4.pos()"
        yield "PIN_SCLKST"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 2) {
		|		state->dummy_typ = -1;
		|		state->dummy_val = -1;
		|	}
		|
		|	if (state->ctx.activations < 1000) {
		|		output.sme = true;
		|		state->sen = true;
		|		output.dme = true;
		|		state->den = true;
		|	}
		|
		|	//bool h1pos = PIN_H2.negedge();
		|	bool q2pos = PIN_Q2.posedge();
		|	bool q4pos = PIN_Q4.posedge();
		|	bool sclk_pos = q4pos && !PIN_CSTP;
		|																					if (ioc_trace && PIN_TRAEN=> && !is_tracing) {
		|																						is_tracing = true;
		|																						ALWAYS_TRACE(<< " IS TRACING");
		|																					}
		|																					if (ioc_trace && !PIN_TRAEN=> && is_tracing) {
		|																						is_tracing = true;
		|																						ioc_trace = 0;
		|																						ALWAYS_TRACE(<< " STOP TRACING");
		|																					}
		|
		|	unsigned rand = UIR_RAND;
		|	uint64_t typ, val;
		|	typ = typ_bus;
		|	val = val_bus;
		|
		|//	ALWAYS						Q2				H2				Q3				Q4
		|							if (q2pos) {
		|								//if (val != val_bus) ALWAYS_TRACE(<<"VALBUS " << std::hex << val << " " << val_bus);
		|								if (state->slice_ev && !state->ten) {
		|									output.sme = false;
		|								}
		|								if (rand == 0x0a) {
		|									output.sme = true;
		|								}
		|								if (state->delay_ev && !state->ten) {
		|									output.dme = false;
		|								}
		|								if (rand == 0x0b) {
		|									output.dme = true;
		|								}
		|							}
		|{
		|//	ALWAYS						Q2				H2				Q3				Q4
		|																			if (q4pos) {
		|
		|																				if (sclk_pos) {
		|																					if (rand == 0x23)
		|																						state->cpu_running = true;
		|																					if (rand == 0x24)
		|																						state->cpu_running = false;
		|																				}
		|
		|																				if (q4pos && (state->request_int_en &&
		|																				    state->reqrdp != state->reqwrp) && state->iack != 6) {
		|																					state->iack = 6;
		|																					ioc_sc_bus_start_iack(6);
		|																				}
		|																				if (q4pos && (!state->request_int_en ||
		|																				    state->reqrdp == state->reqwrp) && state->iack != 7) {
		|																					state->iack = 7;
		|																					ioc_sc_bus_start_iack(7);
		|																				}
		|
		|																				if (q4pos)
		|																					do_xact();
		|
		|																				if (sclk_pos && rand == 0x04) {
		|																					state->reqfifo[state->reqwrp++] = typ & 0xffff;
		|																					state->reqwrp &= 0x3ff;
		|																				}
		|
		|
		|																				if (sclk_pos && rand == 0x05) {
		|																					state->rsprdp++;
		|																					state->rsprdp &= 0x3ff;
		|																				}
		|
		|																				if (sclk_pos) {
		|																					unsigned adr = (state->areg | state->acnt) << 2;
		|																					assert(adr < (512<<10));
		|																			
		|																					if ((rand == 0x1c) || (rand == 0x1d)) {
		|																						state->rdata = vbe32dec(state->ram + adr);
		|																					}
		|											
		|																					if ((rand == 0x1e) || (rand == 0x1f)) {
		|																						uint32_t data = typ >> 32;
		|																						vbe32enc(state->ram + adr, data);
		|																					}
		|																			
		|																					if (rand == 0x01) {
		|																						state->acnt = (typ >> 2) & 0x00fff;
		|																						state->areg = (typ >> 2) & 0x1f000;
		|																					}
		|																			
		|																					if ((rand == 0x1c) || (rand == 0x1e)) {
		|																						state->acnt += 1;
		|																						state->acnt &= 0xfff;
		|																					}
		|																				}
		|																			
		|																				if (sclk_pos && rand == 0x08) {
		|																					state->rtc = 0;
		|																				}
		|																				if (q4pos && !PIN_RTCEN=> && rand != 0x08) {
		|																					state->rtc++;
		|																					state->rtc &= 0xffff;
		|																				}
		|																											
		|																				state->prescaler++;
		|																				state->ten = state->prescaler != 0xf;
		|																				state->prescaler &= 0xf;
		|																				if (!PIN_CSTP=>) {
		|																					if (rand == 0x0c) {
		|																						state->sen = false;
		|																					}
		|																					if (rand == 0x0d) {
		|																						state->sen = true;
		|																					}
		|																					if (rand == 0x0e) {
		|																						state->den = false;
		|																					}
		|																					if (rand == 0x0f) {
		|																						state->den = true;
		|																					}
		|																				}
		|																		
		|																				state->slice_ev= state->slice == 0xffff;
		|																				if (rand == 0x06) {
		|																					uint64_t tmp = typ;
		|																					tmp >>= 32;
		|																					state->slice = tmp >> 16;
		|																					TRACE(<< " LD " << std::hex << state->slice);
		|																				} else 	if (!state->sen && !state->ten) {
		|																					state->slice++;
		|																				}
		|																		
		|																				state->delay_ev= state->delay == 0xffff;
		|																				if (rand == 0x07) {
		|																					uint64_t tmp = typ;
		|																					tmp >>= 32;
		|																					state->delay = tmp;
		|																				} else if (!state->den && !state->ten) {
		|																					state->delay++;
		|																				}
		|																			}
		|}
		|
		|	if (!q4pos) {
		|		output.rspemn = state->rspwrp == state->rsprdp;
		|	}
		|
		|{
		|	unsigned tvbs = UIR_TVBS;
		|
		|	bool rddum = true;
		|	bool ioctv = true;
		|	switch (tvbs) {
		|	case 0x0: break;
		|	case 0x1: break;
		|	case 0x2: break;
		|	case 0x3: break;
		|	case 0x4: ioctv = false; break;
		|	case 0x5: break;
		|	case 0x8:
		|	case 0x9: break;
		|	case 0xa:
		|	case 0xb: break;
		|	case 0xc:
		|	case 0xd:
		|	case 0xe:
		|	case 0xf:
		|		if (state->dumen) {
		|			rddum = false;
		|			ioctv = false;
		|		}
		|		break;
		|	default:
		|		break;
		|	}
		|	
		|	bool load_wdr = UIR_ULWDR;
		|
		|	bool uir_load_wdr = !load_wdr;
		|
		|	output.ldwdr = !(uir_load_wdr && PIN_SCLKST=>);
		|
		|																											if (q4pos && rddum && !PIN_RSTRDR=>) {
		|																												//if (val != val_bus) ALWAYS_TRACE(<<"VALBUS " << std::hex << val << " " << val_bus);
		|																												state->dummy_typ = typ;
		|																												state->dummy_val = val;
		|																											}
		|}
		|{
		|	uint64_t tmp;
		|
		|	tmp = (typ >> 7) & 0xfffff;
		|	bool below = (tmp >= 0xc);
		|	bool exit_proc = rand != 0x12;
		|	output.bltcp = !(below || exit_proc);
		|	tmp = typ & 0x80000047;
		|	state->pfr = 
		|	    tmp == 0x80000000 ||
		|	    tmp == 0x80000040 ||
		|	    tmp == 0x80000044;
		|
		|}
		|
		|	if (!PIN_QVALOE=> && !q4pos) {
		|		val_bus = state->dummy_val;
		|	}
		|
		|	if (!PIN_QTYPOE=> && !q4pos) {
		|		switch (rand) {
		|		case 0x05:
		|			typ_bus = (uint64_t)(state->slice) << 48;
		|			typ_bus |= (uint64_t)(state->delay) << 32;
		|			typ_bus |= ((uint64_t)state->rtc) << 16;
		|			typ_bus |= state->rspfifo[state->rsprdp];
		|			break;
		|		case 0x08:
		|		case 0x09:
		|		case 0x19:
		|			typ_bus = (uint64_t)(state->slice) << 48;
		|			typ_bus |= (uint64_t)(state->delay) << 32;
		|			typ_bus |= ((uint64_t)state->rtc) << 16;
		|			// output.qtyp |= state->eidrg >> 1;
		|			// output.qtyp |= state->cbreg1 << 7;
		|			break;
		|		case 0x16:
		|		case 0x1c:
		|		case 0x1d:
		|			typ_bus = ((uint64_t)state->rdata) << 32;
		|			typ_bus |= ((uint64_t)state->rtc) << 16;
		|			// output.qtyp |= state->eidrg >> 1;
		|			// output.qtyp |= state->cbreg1 << 7;
		|			break;
		|		default:
		|			typ_bus = state->dummy_typ;
		|			break;
		|		}
		|	}
		|
		|	unsigned cond_sel;
		|	BUS_CONDS_READ(cond_sel);
		|	switch (cond_sel) {
		|	case 0x78:
		|		output.cond = true; // state->multibit_error;
		|		break;
		|	case 0x79:
		|		output.cond = state->pfr;
		|		break;
		|	case 0x7a:
		|		output.cond = true; // state->checkbit_error;
		|		break;
		|	case 0x7b:
		|		output.cond = state->reqwrp != state->reqrdp;
		|		break;
		|	case 0x7c:
		|		output.cond = state->acnt == 0xfff;
		|		break;
		|	case 0x7d:
		|		output.cond = true;
		|		break;
		|	case 0x7e:
		|		output.cond = state->rspwrp != state->rsprdp;
		|		break;
		|	case 0x7f:
		|		output.cond = true;
		|		break;
		|	}
		|//	ALWAYS						Q2				H2				Q3				Q4
		|																			if (q4pos) {
		|																				if (!PIN_RTCEN=>) {
		|																					unsigned addr;
		|																					BUS_UAD_READ(addr);
		|																					state->uir = state->wcsram[addr];
		|																					assert (state->uir <= 0xffff);
		|																					output.aen = (1 << UIR_AEN) ^ 0xf;
		|																					output.fen = (1 << UIR_FEN) ^ 0xf;
		|																					state->dumen = !PIN_DUMNXT=>;
		|																					state->csa_hit = !PIN_ICSAH=>;
		|																					unsigned tvbs = UIR_TVBS;
		|
		|																					uint16_t tdat = addr;
		|																					if (PIN_CSTP=>)
		|																						tdat |= 0x8000;
		|																					if (state->csa_hit)
		|																						tdat |= 0x4000;
		|																					uint16_t tptr = state->tram[2048];
		|																					state->tram[tptr] = tdat;
		|																					if (ioc_trace) {
		|																						tptr += 1;
		|																						tptr &= 0x7ff;
		|																						state->tram[2048] = tptr;
		|																					}
		|
		|																					output.seqtv = true;
		|																					output.fiuv = true;
		|																					output.fiut = true;
		|																					output.memv = true;
		|																					output.memtv = true;
		|																					output.ioctv = true;
		|																					output.valv = true;
		|																					output.typt = true;
		|																					switch (tvbs) {
		|																					case 0x0: output.valv = false; output.typt = false; break;
		|																					case 0x1: output.fiuv = false; output.typt = false; break;
		|																					case 0x2: output.valv = false; output.fiut = false; break;
		|																					case 0x3: output.fiuv = false; output.fiut = false; break;
		|																					case 0x4: output.ioctv = false; break;
		|																					case 0x5: output.seqtv = false; break;
		|																					case 0x8:
		|																					case 0x9:
		|																						output.memv = false; output.typt = false; break;
		|																					case 0xa:
		|																					case 0xb:
		|																						output.memv = false; output.fiut = false; break;
		|																					case 0xc:
		|																					case 0xd:
		|																					case 0xe:
		|																					case 0xf:
		|																						if (state->dumen) {
		|																							output.ioctv = false;
		|																						} else if (state->csa_hit) {
		|																							output.typt = false;
		|																							output.valv = false;
		|																						} else {
		|																							output.memtv = false;
		|																							output.memv = false;
		|																						}
		|																						break;
		|																					default:
		|																						break;
		|																					}
		|																				}
		|																			}
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
