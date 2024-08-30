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
   1MEG DRAM
   =========

'''

from part import PartModel, PartModelDQ, PartFactory
from pin import Pin
from net import Net
from node import Node
from component import Component

class BRAM(PartFactory):
    ''' 1MEGxN DRAM '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint16_t bitc[1 << 20];
		|	uint64_t bitt[1 << 21];
		|	unsigned set, cl, wd;
		|	uint16_t cdreg, cqreg;
		|	uint64_t tdreg, tqreg;
		|	uint64_t vdreg, vqreg;
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"
        yield "PIN_QCOE"
        yield "PIN_DCK.pos()"
        yield "PIN_ICK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	if (PIN_DCK.posedge()) {
		|		BUS_DC_READ(state->cdreg);
		|		BUS_DT_READ(state->tdreg);
		|		BUS_DV_READ(state->vdreg);
		|	}
		|	if (PIN_RAS.posedge()) {
		|		BUS_CL_READ(state->cl);
		|		BUS_WD_READ(state->wd);
		|	}
		|	if (PIN_CAS.negedge()) {
		|		BUS_SET_READ(state->set);
		|	}
		|
		|	uint32_t adr =
		|		(state->set << 18) |
		|		(state->cl << 6) |
		|		state->wd;
		|
		|	assert(adr < (1 << 20));
		|	if (PIN_CAS.negedge()) {
		|		if (PIN_WE=>) {
		|			state->bitc[adr] = state->cdreg;
		|			state->bitt[adr+adr] = state->tdreg;
		|			state->bitt[adr+adr+1] = state->vdreg;
		|		}
		|	}
		|	if (PIN_ICK.posedge() && !PIN_CAS=>) {
		|		state->cqreg = state->bitc[adr];
		|		state->tqreg = state->bitt[adr+adr];
		|		state->vqreg = state->bitt[adr+adr+1];
		|	}
		|	output.z_qc = PIN_QCOE=>;
		|	output.z_qt = output.z_qc;
		|	output.z_qv = output.z_qc;
		|	if (!output.z_qc) {
		|		output.qc = state->cqreg;
		|		output.qt = state->tqreg;
		|		output.qv = state->vqreg;
		|	}
		|''')



class DRAM1MEGCLK(PartFactory):
    ''' 1MEGxN DRAM '''

    autopin = True

    def state(self, file):
        if len(self.comp.nodes) - 13 <= 16:
            file.fmt('''
		|	uint16_t bits[1 << 20];
		|	unsigned ras, cas;
		|	uint16_t dreg, qreg;
		|''')
        else:
            file.fmt('''
		|	uint64_t bits[1 << 20];
		|	unsigned ras, cas;
		|	uint64_t dreg, qreg;
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"
        yield "PIN_OE"
        yield "PIN_DCK.pos()"
        yield "PIN_ICK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint32_t adr = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_DCK.posedge()) {
		|		BUS_D_READ(state->dreg);
		|	}
		|	if (PIN_RAS.negedge())
		|		state->ras = adr;
		|	if (PIN_CAS.negedge()) {
		|		state->cas = adr;
		|		adr = (state->cas << 10) | state->ras;
		|		if (PIN_WE=>) {
		|			state->bits[adr] = state->dreg;
		|		}
		|	}
		|	adr = (state->cas << 10) | state->ras;
		|	if (PIN_ICK.posedge() && !PIN_CAS=>) {
		|		state->qreg = state->bits[adr];
		|	}
		|	output.z_q = PIN_OE=>;
		|	if (!output.z_q) {
		|		output.z_q = false;
		|		output.q = state->qreg;
		|	}
		|''')


class DRAM1MEGWIDE(PartFactory):
    ''' 1MEGxN DRAM '''

    autopin = True
    autotrace = False

    def state(self, file):
        if len(self.comp.nodes) - 13 <= 16:
            file.fmt('''
		|	uint16_t bits[1 << 20];
		|	unsigned ras, cas;
		|''')
        else:
            file.fmt('''
		|	uint64_t bits[1 << 20];
		|	unsigned ras, cas;
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint32_t adr = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_RAS.negedge())
		|		state->ras = adr;
		|	if (PIN_CAS.negedge()) {
		|		state->cas = adr;
		|		adr = (state->cas << 10) | state->ras;
		|		if (PIN_OE=>) {
		|			output.z_q = true;
		|			BUS_D_READ(state->bits[adr]);
		|		} else {
		|			output.z_q = false;
		|			output.q = state->bits[adr];
		|		}
		|	}
		|	if (PIN_RAS.posedge() || PIN_CAS.posedge()) {
		|		output.z_q = true;
		|	}
		|	if (!PIN_CAS=> || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << " ras " << PIN_RAS.negedge()
		|		    << " cas " << PIN_CAS.negedge()
		|		    << " oe " << PIN_OE?
		|		    << " a " << BUS_A_TRACE()
		|		    << " ra " << std::hex << state->ras
		|		    << " ca " << std::hex << state->cas
		|		    << " d " << BUS_D_TRACE()
		|		);
		|	}
		|
		|''')


class DRAM1MEG(PartFactory):

    ''' 1MEG DRAM '''

    def state(self, file):
        file.fmt('''
		|	unsigned ras, cas;
		|	uint32_t bits[(1<<20)>>5];
		|''')

    def sensitive(self):
        yield "PIN_RAS"
        yield "PIN_CAS"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint32_t adr = 0, data = 0, mask = 0;
		|
		|	BUS_A_READ(adr);
		|
		|	if (PIN_RAS.negedge())
		|		state->ras = adr;
		|	if (PIN_CAS.negedge()) {
		|		state->cas = adr;
		|		adr = (state->cas << 10) | state->ras;
		|		mask = 1 << (adr & 0x1f);
		|		adr >>= 5;
		|		if (!PIN_WE=>) {
		|			PIN_DQ = sc_dt::sc_logic_Z;
		|			if (PIN_DQ=>)
		|				state->bits[adr] |= mask;
		|			else
		|				state->bits[adr] &= ~mask;
		|		} else {
		|			data = (state->bits[adr] & mask) != 0;
		|			PIN_DQ = AS(data);
		|		}
		|	}
		|	if (PIN_RAS.posedge() || PIN_CAS.posedge()) {
		|		PIN_DQ = sc_dt::sc_logic_Z;
		|	}
		|	if (!PIN_CAS=> || (state->ctx.do_trace & 2)) {
		|		TRACE(
		|		    << " ras " << PIN_RAS?
		|		    << " cas " << PIN_CAS?
		|		    << " we " << PIN_OE?
		|		    << " a " << BUS_A_TRACE()
		|		    << " dq " << PIN_DQ?
		|		    << " ras " << std::hex << state->ras
		|		    << " cas " << std::hex << state->cas
		|		    << " data " << std::hex << data
		|		    << " mask " << std::hex << mask
		|		);
		|	}
		|
		|''')

class Model1Meg(PartModel):
    ''' 1MEG DRAM '''

    def assign(self, comp, part_lib):

        node = comp["D"]
        node.remove()
        node = comp["Q"]
        node.remove()
        node.pin.name = "DQ"
        node.pin.set_role("bidirectional")
        node.insert()

        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("1MEG", Model1Meg("1MEG", DRAM1MEG))
    part_lib.add_part("XDRAM", PartModelDQ("XDRAM", DRAM1MEGWIDE))
    part_lib.add_part("XERAM", PartModelDQ("XERAM", DRAM1MEGCLK))
    part_lib.add_part("XFRAM", PartModelDQ("XFRAM", DRAM1MEGCLK))
    part_lib.add_part("XBRAM", PartModelDQ("XBRAM", BRAM))
