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
   MEM32 CACHE
   ===========

'''


from part import PartModel, PartFactory
from pin import Pin
from node import Node

class XCACHE(PartFactory):

    ''' MEM32 CACHE '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_A_WIDTH];
		|	uint8_t rame[1<<BUS_A_WIDTH];
		|	uint8_t par[1<<BUS_A_WIDTH];
		|	bool zvq;
		|	uint64_t vq;
		|	bool zpq;
		|	uint8_t pq;
		|	uint8_t parq;
		|	unsigned ae, al, be, bl, sr, la, lb;
		|	bool nme;
		|	bool ome;
		|	bool nml;
		|	bool oml;
		|	bool k12, k13;
		|''')

    def sensitive(self):
        yield "PIN_WE.pos()"
        yield "PIN_EWE.pos()"
        yield "PIN_LWE.pos()"
        yield "BUS_A_SENSITIVE()"
        yield "PIN_CLK"
        yield "PIN_OEE"
        yield "PIN_OEL"
        yield "PIN_EQ"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	TRACE(
		|		<< " we^ " << PIN_WE.posedge()
		|		<< " ewe^ " << PIN_EWE.posedge()
		|		<< " lwe^ " << PIN_LWE.posedge()
		|		<< " a " << BUS_A_TRACE()
		|		<< " clk^v " << PIN_CLK.posedge() << PIN_CLK.negedge()
		|		<< " oee " << PIN_OEE?
		|		<< " oel " << PIN_OEL?
		|		<< " eq " << PIN_EQ?
		|		<< " j " << state->ctx.job
		|	);
		|
		|	if (state->ctx.job) {
		|		PIN_DROE<=(state->zvq);
		|		if (state->zvq) {
		|			BUS_VQ_Z();
		|			BUS_PQ_Z();
		|		} else {
		|			uint64_t v = state->vq & 0xffffffffffff80ff;	// VAL bits
		|			v |= (state->pq & 0xfe) << 7;			// VAL49-55
		|			uint8_t p = state->parq & 0xfd;			// P0-5,7
		|			p |= (state->pq & 1) << 1;			// P6
		|			BUS_VQ_WRITE(v);
		|			BUS_PQ_WRITE(p);
		|		}
		|		state->ctx.job = 0;
		|	}
		|
		|	unsigned adr = 0;
		|	uint64_t data = 0;
		|
		|	BUS_A_READ(adr);
		|	adr &= ~3;
		|	if (state->k12)
		|		adr |= 2;
		|	if (state->k13)
		|		adr |= 1;
		|
		|	data = state->ram[adr];
		|	BUS_TQ_WRITE(data >> 6);
		|
		|	uint8_t pdata;
		|	if (PIN_EVEN=>) {
		|		pdata = state->rame[adr & ~1];
		|	} else {
		|		pdata = state->rame[adr | 1];
		|	}
		|	bool vqoe = !(PIN_DIR=> && PIN_TGOE=> && (PIN_EVEN=> || PIN_LVEN=>));
		|	if (!vqoe && (data != state->vq || pdata != state->pq || state->zvq)) {
		|		state->vq = data;
		|		state->zvq = false;
		|		state->pq = pdata;
		|		state->parq = (state->par[adr] & 0xfd);
		|		state->zpq = false;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	} else if (vqoe && !state->zvq) {
		|		state->zvq = true;
		|		state->zpq = true;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|
		|	bool pos = PIN_CLK.posedge();
		|	bool neg = PIN_CLK.negedge();
		|	uint64_t tag = data, bpar = 0;
		|
		|	bool oee = PIN_OEE=>;
		|	bool oel = PIN_OEL=>;
		|	unsigned tspr;
		|	BUS_TSPR_READ(tspr);
		|	if (pos && tspr) {
		|		if (tspr == 3) {
		|			state->sr = state->la << 8;
		|			state->sr |= state->lb;
		|		} else if (tspr == 2) {
		|			state->sr >>= 1;
		|			state->sr |= PIN_DIAG=> << 15;
		|		} else if (tspr == 1) {
		|			state->sr <<= 1;
		|			state->sr &= 0xf7f7;
		|		}
		|		PIN_TSPO<=(state->sr & 1);
		|	}
		|
		|	if (pos || neg) {
		|		bpar = odd_parity64(tag);
		|	}
		|	if (pos) {
		|		bool ts6l = odd_parity(state->rame[adr | 1] & 0xfe);
		|		ts6l ^= ((tag >> 15) & 1);
		|		state->al = bpar & 0xfd;
		|		state->al |= ts6l << 1;
		|		state->bl = state->par[adr] & 0xfd;
		|		state->bl |= (state->rame[adr | 1] & 0x1) << 1;
		|	}
		|	if (neg) {
		|		bool ts6e = odd_parity(state->rame[adr & ~1] & 0xfe);
		|		ts6e ^= ((tag >> 15) & 1);
		|		state->ae = bpar & 0xfd;
		|		state->ae |= ts6e << 1;
		|		state->be = state->par[adr] & 0xfd;
		|		state->be |= (state->rame[adr & ~1] & 0x1) << 1;
		|	}
		|
		|
		|	if (!oee) {
		|		state->la = state->ae;
		|		state->lb = state->be;
		|	} else if (!oel) {
		|		state->la = state->al;
		|		state->lb = state->bl;
		|	} else if (!PIN_TSMO=> && tspr != 3) {
		|		state->la = (state->sr >> 8) & 0xff;
		|		state->lb = (state->sr >> 0) & 0xff;
		|	} else {
		|		state->la = 0xff;
		|		state->lb = 0xff;
		|	}
		|	PIN_PERR<=(state->la != state->lb);
		|
		|
		|	uint64_t ta, ts, nm, pg, sp;
		|	bool name, offset;
		|
		|	ta = data;
		|	ts = ta & 0x7;
		|	ta = ta >> 19;
		|	BUS_NM_READ(nm);
		|	BUS_PG_READ(pg);
		|	BUS_SP_READ(sp);
		|
		|	if (PIN_E) {
		|		name = true;
		|		offset = true;
		|	} else {
		|		name = (nm != (ta >> BUS_PG_WIDTH));
		|		offset = (pg != (ta & BUS_PG_MASK)) || (sp != ts);
		|	}
		|	
		|	PIN_NME<=(!state->nme && !(PIN_EQ=> && state->ome));
		|	PIN_NML<=(!state->nml && !(PIN_EQ=> && state->oml));
		|
		|	if (PIN_CLK.negedge()) {
		|		state->nme = name;
		|		state->ome = offset;
		|		next_trigger(5, SC_NS);
		|	} else if (PIN_CLK.posedge()) {	 
		|		state->nml = name;
		|		state->oml = offset;
		|		next_trigger(5, SC_NS);
		|	}
		|
		|	uint64_t vd;
		|	BUS_VD_READ(vd);
		|	uint8_t pd;
		|	BUS_PD_READ(pd);
		|
		|	if (!PIN_OE=> && PIN_WE.posedge()) {
		|		state->ram[adr] = vd & ~(0xfeULL << 7);	// VAL bits
		|		state->par[adr] = pd;
		|		if (state->ctx.do_trace & 2) {
		|			char buf[128];
		|			snprintf(buf, sizeof buf, "W %x %jx %jx %x", adr, (uintmax_t)state->ram[adr], (uintmax_t)vd, pd);
		|			sysc_trace(this->name(), buf);
		|		}
		|	}
		|
		|	if (!PIN_ELCE=> && PIN_EWE.posedge()) {
		|		if (!PIN_DIR=> && PIN_EVEN=> && PIN_TGOE=>) {
		|			data = (pd & 0x02) >> 1;	// P6
		|			data |= (vd >> 7) & 0xfe;	// VAL49-55
		|		} else {
		|			BUS_CWE_READ(data);
		|			data &= 0x3f;
		|			data |= (state->rame[adr & ~1] & 0xc0);
		|		}
		|		state->rame[adr & ~1] = data;
		|	}
		|
		|	if (!PIN_ELCE=> && PIN_LWE.posedge()) {
		|		if (!PIN_DIR=> && PIN_LVEN=> && PIN_TGOE=>) {
		|			data = (pd & 0x02) >> 1;	// P6
		|			data |= (vd >> 7) & 0xfe;	// VAL49-55
		|		} else {
		|			BUS_CWL_READ(data);
		|			data &= 0x3f;
		|			data |= (state->rame[adr | 1] & 0xc0);
		|		}
		|		state->rame[adr | 1] = data;
		|	}
		|	data = state->rame[adr & ~1];
		|	BUS_CRE_WRITE(data);
		|	data = state->rame[adr | 1];
		|	BUS_CRL_WRITE(data);
		|
		|	if (PIN_CLK.posedge())
		|		state->k12 = PIN_K12=>;
		|	else if (PIN_CLK.negedge())
		|		state->k13 = PIN_K13=>;
		|''')




class ModelXCACHE(PartModel):
    ''' MEM32 CACHE '''

    def assign(self, comp, part_lib):

        for node in comp:
            if node.pin.name[:3] in ('VDQ', 'PDQ'):
                b = node.pin.name[0]
                pn = node.pin.name[3:]
                new_pin = Pin(b + "D" + pn, b + "D" + pn, "input")
                Node(node.net, comp, new_pin)
                new_pin = Pin(b + "Q" + pn, b + "Q" + pn, "tri_state")
                Node(node.net, comp, new_pin)
                node.remove()
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCACHE", ModelXCACHE("XCACHE", XCACHE))
