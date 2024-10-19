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
   XIOP CPU
   ===========

'''

from part import PartModelDQ, PartFactory

class XIOP(PartFactory):

    ''' XIOP CPU'''

    autopin = True

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_SCLK.pos()"
        yield "PIN_QTHOE"
        yield "PIN_QTMOE"
        yield "PIN_QTLOE"

    def extra(self, file):
        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.
        file.write('\t#define XIOP_VARIANT 1\n')
        self.scm.sf_cc.include("Iop/iop_sc_68k20.hh")
        file.include("Infra/vend.h")


    def state(self, file):
        ''' Extra state variable '''

        file.fmt('''
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
		|''');

    def init(self, file):

        file.fmt('''
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ram = (uint8_t*)(c1 + 1);
		|''')

    def priv_decl(self, file):
        ''' further private decls '''
        file.fmt('''
		|       void do_xact(struct output_pins *output);
		|''')

    def priv_impl(self, file):
        file.fmt('''
		|void
		|SCM_«mmm» ::
		|do_xact(struct output_pins *output)
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
		|		output->orst = 0;
		|		output->z_orst = state->xact->data & 1;
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

    def doit(self, file):
        ''' The meat of the doit() function '''

        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.

        file.fmt('''
		|	bool q4_pos = PIN_CLK.posedge();
		|	bool sclk_pos = PIN_SCLK.posedge();
		|	unsigned rnd;
		|	BUS_RND_READ(rnd);
		|
		|	if (sclk_pos) {
		|		if (rnd == 0x23)
		|			state->cpu_running = true;
		|		if (rnd == 0x24)
		|			state->cpu_running = false;
		|	}
		|
		|	if (q4_pos && (state->request_int_en && state->reqrdp != state->reqwrp) && state->iack != 6) {
		|		state->iack = 6;
		|		ioc_sc_bus_start_iack(6);
		|	}
		|	if (q4_pos && (!state->request_int_en || state->reqrdp == state->reqwrp) && state->iack != 7) {
		|		state->iack = 7;
		|		ioc_sc_bus_start_iack(7);
		|	}
		|
		|	if (q4_pos)
		|		do_xact(&output);
		|
		|	if (sclk_pos && rnd == 0x04) {
		|		uint64_t ityp;
		|		BUS_ITYP_READ(ityp);
		|		state->reqfifo[state->reqwrp++] = ityp & 0xffff;
		|		state->reqwrp &= 0x3ff;
		|	}
		|
		|	output.z_qtl = PIN_QTLOE=>;
		|	if (!output.z_qtl) {
		|		output.qtl = state->rspfifo[state->rsprdp];
		|	}
		|
		|	output.rspemp = state->rspwrp != state->rsprdp;
		|	output.rspemn = state->rspwrp == state->rsprdp;
		|	output.reqemp = state->reqwrp != state->reqrdp;
		|
		|	if (sclk_pos && !output.z_qtl) {
		|		state->rsprdp++;
		|		state->rsprdp &= 0x3ff;
		|	}
		|
		|	if (sclk_pos) {
		|		unsigned adr = (state->areg | state->acnt) << 2;
		|
		|		if ((rnd == 0x1c) || (rnd == 0x1d)) {
		|			state->rdata = vbe32dec(state->ram + adr);
		|		}
		|
		|		if ((rnd == 0x1e) || (rnd == 0x1f)) {
		|			uint64_t typ;
		|			BUS_ITYP_READ(typ);
		|			uint32_t data = typ >> 32;
		|			vbe32enc(state->ram + adr, data);
		|		}
		|
		|		if (rnd == 0x01) {
		|			uint64_t typ;
		|			BUS_ITYP_READ(typ);
		|			state->acnt = (typ >> 2) & 0x00fff;
		|			state->areg = (typ >> 2) & 0x1f000;
		|		}
		|
		|		if ((rnd == 0x1c) || (rnd == 0x1e)) {
		|			state->acnt += 1;
		|			state->acnt &= 0xfff;
		|		}
		|		output.oflo = state->acnt == 0xfff;
		|	}
		|	output.z_qth = PIN_QTHOE=>;
		|	if (!output.z_qth) {
		|		output.qth = state->rdata;
		|	}
		|
		|	if (sclk_pos && rnd == 0x08) {
		|		state->rtc = 0;
		|	}
		|	if (q4_pos && !PIN_RTCEN=> && rnd != 0x08) {
		|		state->rtc++;
		|		state->rtc &= 0xffff;
		|	}
		|	output.z_qtm = PIN_QTMOE=>;
		|	if (!output.z_qtm) {
		|		output.qtm = state->rtc;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOP", PartModelDQ("XIOP", XIOP))
