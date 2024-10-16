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

from part import PartModel, PartFactory

class XIOP(PartFactory):

    ''' XIOP CPU'''

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_SCLK.pos()"
        # yield "PIN_MKREQ.pos()"
        yield "PIN_OTYPOE"

    def extra(self, file):
        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.
        file.write('\t#define XIOP_VARIANT 1\n')
        self.scm.sf_cc.include("Iop/iop_sc_68k20.hh")

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
		|''');

    def doit(self, file):
        ''' The meat of the doit() function '''

        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.

        file.fmt('''
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
		|	if ((state->request_int_en && state->reqrdp != state->reqwrp) && state->iack != 6) {
		|		state->iack = 6;
		|		ioc_sc_bus_start_iack(6);
		|		TRACE( << " IRQ 6 ");
		|	}
		|	if ((!state->request_int_en || state->reqrdp == state->reqwrp) && state->iack != 7) {
		|		state->iack = 7;
		|		ioc_sc_bus_start_iack(7);
		|		TRACE( << " IRQ 7 ");
		|	}
		|
		|	if (sclk_pos && rnd == 0x04) {
		|		unsigned ityp;
		|		BUS_ITYP_READ(ityp);
		|		state->reqfifo[state->reqwrp++] = ityp;
		|		state->reqwrp &= 0x3ff;
		|
		|		uint8_t utrc[2];
		|		utrc[0] = UT_REQ_FIFO_WR;
		|		utrc[1] = ityp;
		|		microtrace(utrc, sizeof utrc);
		|
		|		TRACE(
		|			<< "FIFO REQ " << std::hex << ityp
		|			<< " wr " << state->reqwrp
		|			<< " rd " << state->reqrdp
		|		);
		|		PIN_REQEMP = state->reqwrp != state->reqrdp;
		|	}
		|
		|	if (PIN_OTYPOE.negedge()) {
		|		TRACE(<< "OE FIFO RSP " << std::hex << state->rspfifo[state->rsprdp]);
		|
		|		uint8_t utrc[2];
		|		utrc[0] = UT_RESP_FIFO_RD;
		|		utrc[1] = state->rspfifo[state->rsprdp];
		|		microtrace(utrc, sizeof utrc);
		|
		|		BUS_OTYP_WRITE(state->rspfifo[state->rsprdp]);
		|	}
		|	if (PIN_OTYPOE.posedge()) {
		|		TRACE(<< "OE FIFO RSP Z ");
		|		BUS_OTYP_Z();
		|	}
		|
		|	if (sclk_pos && !PIN_OTYPOE) {
		|		state->rsprdp++;
		|		state->rsprdp &= 0x3ff;
		|		PIN_RSPEMP = state->rspwrp != state->rsprdp;
		|		TRACE(
		|			<< "FIFO RSP++ " << std::hex
		|			<< " wr " << state->rspwrp
		|			<< " rd " << state->rsprdp
		|		);
		|	}
		|
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
		|		PIN_REQEMP = state->reqwrp != state->reqrdp;
		|		PIN_RSPEMP = state->rspwrp != state->rsprdp;
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
		|		uint8_t utrc[2];
		|		utrc[0] = UT_RESP_FIFO_WR;
		|		utrc[1] = state->xact->data;
		|		microtrace(utrc, sizeof utrc);
		|
		|		TRACE(
		|			"WR FIFO RSP " << std::hex << state->xact->data
		|			<< " wr " << state->rspwrp
		|			<< " rd " << state->rsprdp
		|		);
		|		PIN_RSPEMP = state->rspwrp != state->rsprdp;
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
		|		PIN_REQEMP = state->reqwrp != state->reqrdp;
		|
		|		uint8_t utrc[2];
		|		utrc[0] = UT_REQ_FIFO_RD;
		|		utrc[1] = state->reqreg;
		|		microtrace(utrc, sizeof utrc);
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
		|		if (state->xact->data & 1)
		|			PIN_ORST = sc_dt::sc_logic_Z;
		|		else
		|			PIN_ORST = sc_dt::sc_logic_0;
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
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XIOP", PartModel("XIOP", XIOP))
