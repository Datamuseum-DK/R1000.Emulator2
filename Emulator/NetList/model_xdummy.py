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

CBITS = '''
           TYP:0                                                     TYP:63 VAL:0                                                     VAL:63 CHECKBIT
    ECCG16 --------------------------------++++++++++++++++++++++++++++++++ --------------------------------++++++++++++++++++++++++++++++++ +--------
    ECCG17 ++++++++++++++++++++++++++++++++-------------------------------- --------------------------------++++++++++++++++++++++++++++++++ -+-------
    ECCG28 ++++++++-----++---+++-+--+++--+-++++++++-----++---+++-+--+++--+- ++++++++-------+-----+-+--+-+-+----++---+-+-+--++++---++++-+---- --+------
    ECCG29 +++++++++++++-++++---+-------+--+++++++++++++-++++---+-------+-- -+------++++++++-------++----++-----+++++--+-++----+---+--++---+ ---+-----
    ECCG44 ++-----+++++++++--++--+++---+-++++-----+++++++++--++--+++-----++ ---+---+----+++---++++--++++------------++++++++---++++------++- ----+----
    ECCG45 -----++++--+---++++++++++++----+-----++++--+---++++++++++++-+--+ --+--++----+--+-++++++++-----+---++----+--------++++++++----+--+ -----+---
    ECCG46 +-++--+-++--+---++----+-+++++++++-++--+-++--+---++----+-++++++++ ----+-+--++------++---+-+++++++++-++--+--+----++--+-+----++-++-- ------+--
    ECCG61 -++-++----+-++-++-+-++-++-++++---++-++----+-++-++-+-++-++-++++-- +---++-++-+-+--++---+-+--+-----+++---+----+--+---+---+--++++++++ -------+-
    ECCG62 ---++----+++-++--+-+++-+-+-+++++---++----+++-++--+-+++-+-+-+++++ ++++----++-+-+--++-+-------++--+++++++++-+-++---+-------+-----+- --------+
'''

class XDUMMY(PartFactory):
    ''' IOC Dummy register '''

    autopin = True

    def extra(self, file):
        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.
        file.write('\t#define XIOP_VARIANT 1\n')
        self.scm.sf_cc.include("Iop/iop_sc_68k20.hh")
        file.include("Infra/vend.h")

    def getmasks(self):
        invert = [0, 0, 0, 0, 1, 1, 1, 0, 0]
        for i in CBITS.split("\n"):
            if not "ECCG" in i:
                continue
            j = i.split()
            tmask = int(j[1].replace("-", "0").replace("+", "1"), 2)
            vmask = int(j[2].replace("-", "0").replace("+", "1"), 2)
            yield tmask, vmask, invert.pop(0)

    def state(self, file):
        file.fmt('''
		|	uint64_t typ, val;
		|	uint8_t elprom[512];
		|	uint8_t eidrg;
		|	unsigned cbreg1;
		|	unsigned cbreg2;
		|''')
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
		|
		|	unsigned prescaler;
		|	uint16_t delay, slice;
		|	bool slice_ev, delay_ev;
		|	bool sen, den, ten;
		|''');


    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->elprom, sizeof state->elprom,
		|	    "PA115-01");
		|''')
        file.fmt('''
		|	struct ctx *c1 = CTX_Find("IOP.ram_space");
		|	assert(c1 != NULL);
		|	state->ram = (uint8_t*)(c1 + 1);
		|''')

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_QTYPOE",
            "PIN_QVALOE",
            "PIN_LDDUM",
        )

    def sensitive(self):
        yield "PIN_QTYPOE"
        yield "PIN_QVALOE"
        yield "PIN_Q4.pos()"
        yield "PIN_Q2.pos()"
        yield "PIN_QTOE"
        yield "PIN_QTHOE"
        yield "PIN_QTMOE"
        yield "PIN_QTLOE"
        yield "PIN_QIOE"

    def priv_decl(self, file):
        ''' further private decls '''
        file.fmt('''
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

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (state->ctx.activations < 2) {
		|		state->typ = -1;
		|		state->val = -1;
		|	}
		|	bool q4_pos = PIN_Q4.posedge();
		|{
		|	if (q4_pos && !PIN_LDDUM=>) {
		|		BUS_DTYP_READ(state->typ);
		|		BUS_DVAL_READ(state->val);
		|	}
		|	output.z_qval = PIN_QVALOE=>;
		|	if (!output.z_qval)
		|		output.qval = state->val;
		|	output.z_qtyp = PIN_QTYPOE=>;
		|	if (!output.z_qtyp)
		|		output.qtyp = state->typ;
		|''')

        file.fmt('''
		|	uint64_t typ, val, tmp, cbo = 0, cbi;
		|
		|	BUS_DTYP_READ(typ);
		|	BUS_DVAL_READ(val);
		|
		|	if (!PIN_TVEN=>) {
		|		BUS_DC_READ(cbi);
		|	} else {
		|		cbi = 0;
		|	}
		|
		|''')

        for tmask, vmask, invert in self.getmasks():
            file.fmt('\n\ttmp = (typ & 0x%016xULL) ^ (val & 0x%016xULL);\n' % (tmask, vmask))
            file.fmt('''
		|	cbo <<= 1;
		|	cbo |= (uint64_t)__builtin_parityll(tmp);
		|''')
            if invert:
                file.fmt('\tcbo ^= 1;\n')

        file.fmt('''
		|
		|	if (q4_pos && !PIN_CSTP=> && !PIN_LDCB=>) {
		|		state->cbreg2 = (typ >> 7) & 0x1ff;
		|	}
		|
		|	cbo ^= cbi;
		|	output.z_qc = PIN_QCOE=>;
		|	if (!output.z_qc) {
		|		if (!PIN_DROT=>)
		|			output.qc = state->cbreg2;
		|		else
		|			output.qc = cbo;
		|	}
		|	output.err = cbo != 0;
		|
		|#if 0
		|	if (!PIN_TVEN=> && state->eidrg != state->elprom[cbo]) {
		|		idle_next = &write_event;
		|	} else if (!PIN_LDCB=>) {
		|		idle_next = &write_event;
		|	}
		|#endif
		|
		|	if (q4_pos && !PIN_TVEN=>) {
		|		state->eidrg = state->elprom[cbo];
		|		output.cber = (state->eidrg & 0x81) != 0x81;
		|		output.mber = state->eidrg & 1;
		|		BUS_DC_READ(state->cbreg1);
		|		state->cbreg1 ^= BUS_DC_MASK;
		|	}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		output.qt = state->eidrg >> 1;
		|		output.qt |= state->cbreg1 << 7;
		|	}
		|}
		|''')
        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.

        file.fmt('''
		|{
		|	bool sclk_pos = q4_pos && !PIN_CSTP;
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
		|		do_xact();
		|
		|	if (sclk_pos && rnd == 0x04) {
		|		uint64_t ityp;
		|		BUS_DTYP_READ(ityp);
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
		|			BUS_DTYP_READ(typ);
		|			uint32_t data = typ >> 32;
		|			vbe32enc(state->ram + adr, data);
		|		}
		|
		|		if (rnd == 0x01) {
		|			uint64_t typ;
		|			BUS_DTYP_READ(typ);
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
		|}
		|{
		|	uint64_t typ, tmp;
		|
		|	BUS_DTYP_READ(typ);
		|
		|	typ &= 0xffffffff;
		|	tmp = typ >> 7;
		|	tmp &= 0xfffff;
		|	output.below = (tmp >= 0xc);
		|	tmp = typ & 0x80000047;
		|	output.pfr = 
		|	    tmp == 0x80000000 ||
		|	    tmp == 0x80000040 ||
		|	    tmp == 0x80000044;
		|
		|}
		|''')

        file.fmt('''
		|{
		|	if (state->ctx.activations < 1000) {
		|		output.sme = true;
		|		state->sen = true;
		|		output.dme = true;
		|		state->den = true;
		|	}
		|
		|	if (PIN_Q2.posedge()) {
		|		unsigned rnd;
		|		BUS_RND_READ(rnd);
		|		if (state->slice_ev && !state->ten) {
		|			output.sme = false;
		|		}
		|		if (rnd == 0x0a) {
		|			output.sme = true;
		|		}
		|		if (state->delay_ev && !state->ten) {
		|			output.dme = false;
		|		}
		|		if (rnd == 0x0b) {
		|			output.dme = true;
		|		}
		|	}
		|
		|	if (PIN_Q4.posedge()) {
		|		unsigned rnd;
		|		BUS_RND_READ(rnd);
		|		state->prescaler++;
		|		state->ten = state->prescaler != 0xf;
		|		state->prescaler &= 0xf;
		|		if (!PIN_CSTP=>) {
		|			if (rnd == 0x0c) {
		|				state->sen = false;
		|			}
		|			if (rnd == 0x0d) {
		|				assert(rnd == 0x0d);
		|				state->sen = true;
		|			}
		|			if (rnd == 0x0e) {
		|				assert(rnd == 0x0e);
		|				state->den = false;
		|			}
		|			if (rnd == 0x0f) {
		|				assert(rnd == 0x0f);
		|				state->den = true;
		|			}
		|		}
		|
		|		state->slice_ev= state->slice == 0xffff;
		|		// if (!PIN_LDSL=>) {
		|		if (rnd == 0x06) {
		|			uint64_t tmp;
		|			BUS_DTYP_READ(tmp);
		|			tmp >>= 32;
		|			state->slice = tmp >> 16;
		|			TRACE(<< " LD " << std::hex << state->slice);
		|		} else 	if (!state->sen && !state->ten) {
		|			state->slice++;
		|		}
		|
		|		state->delay_ev= state->delay == 0xffff;
		|		// if (!PIN_LDDL=>) {
		|		if (rnd == 0x07) {
		|			uint64_t tmp;
		|			BUS_DTYP_READ(tmp);
		|			tmp >>= 32;
		|			state->delay = tmp;
		|		} else if (!state->den && !state->ten) {
		|			state->delay++;
		|		}
		|	}
		|	output.z_qi = PIN_QIOE=>;
		|	if (!output.z_qi) {
		|		output.qi = ((unsigned)(state->slice) << 16) | state->delay;
		|	}
		|}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XDUMMY", PartModelDQ("XDUMMY", XDUMMY))
