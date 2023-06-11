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
   F299 Octal Universal Shift/Storage Register with Common Parallel I/O Pins
   ==========================================================================

   Ref: Fairchild DS009515 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory
from node import Node
from pin import Pin
from net import Net
from component import Component

class F299(PartFactory):

    ''' F299 Octal Universal Shift/Storage Register with Common Parallel I/O Pins '''

    def state(self, file):
        file.fmt('''
		|	unsigned reg;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_OE"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = NULL;
		|	unsigned mode = 0;
		|
		|	BUS_S_READ(mode);
		|
		|	if (mode == 0) {
		|		next_trigger(
		|		    BUS_S_EVENTS() |
		|		    PIN_OE.default_event()
		|		);
		|	}
		|
		|''')
        if "CLR" in self.comp and not self.comp["CLR"].net.is_const():
            file.fmt('''
		|	if (!PIN_CLR=>) {
		|		state->reg = 0;
		|		what = "clr ";
		|		next_trigger(PIN_CLR.posedge_event());
		|	} else
		|''')

        file.fmt('''
		|	if (PIN_CLK.posedge()) {
		|		switch (mode) {
		|		case 3:
		|			what = "load ";
		|			BUS_D_READ(state->reg);
		|			break;
		|		case 2:
		|			what = "<< ";
		|			state->reg <<= 1;
		|			if (PIN_LSI=>) state->reg |= 0x01;
		|			break;
		|		case 1:
		|			what = ">> ";
		|			state->reg >>= 1;
		|			state->reg &= (BUS_D_MASK >> 1);
		|			if (PIN_RSI=>) state->reg |= (1 << (BUS_D_WIDTH-1));
		|			break;
		|		default:
		|			break;
		|		}
		|	}
		|	if (PIN_OE=> || (mode == 3)) {
		|		if (what == NULL && (state->ctx.do_trace & 2))
		|			what = "Z ";
		|		BUS_Y_Z();
		|	} else {
		|		if (what == NULL && (state->ctx.do_trace & 2))
		|			what = "out ";
		|		BUS_Y_WRITE(state->reg);
		|	}
		|	PIN_Q0<=((state->reg & (1 << (BUS_Y_WIDTH-1))) != 0);
		|#if BUS_Y_WIDTH == 8
		|	PIN_Q7<=((state->reg & 0x01) != 0);
		|#else
		|	PIN_Q15<=((state->reg & 0x01) != 0);
		|#endif
		|
		|	if (what != NULL) {
		|		TRACE(
		|		    << what
		|		    << "clk " << PIN_CLK.posedge()
		|		    << " s " << BUS_S_TRACE()
		|		    << " oe " << PIN_OE?
		|''')

        if "CLR" in self.comp:
            file.fmt('''
		|		    << " mr " << PIN_CLR?
		|''')

        file.fmt('''
		|		    << " rsi " << PIN_RSI?
		|		    << " lsi " << PIN_LSI?
		|		    << " d " << BUS_D_TRACE()
		|		    << " | " << std::hex << (unsigned)state->reg
		|		);
		|	}
		|''')


class F299X8(PartFactory):

    ''' 8X F299 Octal Universal Shift/Storage Register with Common Parallel I/O Pins '''

    def state(self, file):
        file.fmt('''
		|	uint64_t reg;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_OE"
        if not self.comp.nodes["CLR"].net.is_pu():
            yield "PIN_CLR"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	const char *what = NULL;
		|	unsigned mode = 0, tmp;
		|
		|	BUS_S_READ(mode);
		|
		|	if (mode == 0) {
		|		next_trigger(
		|		    BUS_S_EVENTS() |
		|		    PIN_OE.default_event()
		|		);
		|	}
		|
		|''')
        if "CLR" in self.comp and not self.comp["CLR"].net.is_const():
            file.fmt('''
		|	if (!PIN_CLR=>) {
		|		state->reg = 0;
		|		what = "clr ";
		|		next_trigger(PIN_CLR.posedge_event());
		|	} else
		|''')

        file.fmt('''
		|	if (PIN_CLK.posedge()) {
		|		switch (mode) {
		|		case 3:
		|			what = "load ";
		|			BUS_D_READ(state->reg);
		|			break;
		|		case 2:
		|			what = "<< ";
		|			state->reg <<= 1;
		|			state->reg &= 0xfefefefefefefefe;
		|			BUS_LI_READ(tmp);
		|			if (tmp & 0x80) state->reg |= (1ULL << 56);
		|			if (tmp & 0x40) state->reg |= (1ULL << 48);
		|			if (tmp & 0x20) state->reg |= (1ULL << 40);
		|			if (tmp & 0x10) state->reg |= (1ULL << 32);
		|			if (tmp & 0x08) state->reg |= (1ULL << 24);
		|			if (tmp & 0x04) state->reg |= (1ULL << 16);
		|			if (tmp & 0x02) state->reg |= (1ULL <<  8);
		|			if (tmp & 0x01) state->reg |= 1;
		|			break;
		|		case 1:
		|			what = ">> ";
		|			state->reg >>= 1;
		|			state->reg &= 0x7f7f7f7f7f7f7f7f;
		|			BUS_RI_READ(tmp);
		|			if (tmp & 0x80) state->reg |= (1ULL << 63);
		|			if (tmp & 0x40) state->reg |= (1ULL << 55);
		|			if (tmp & 0x20) state->reg |= (1ULL << 47);
		|			if (tmp & 0x10) state->reg |= (1ULL << 39);
		|			if (tmp & 0x08) state->reg |= (1ULL << 31);
		|			if (tmp & 0x04) state->reg |= (1ULL << 23);
		|			if (tmp & 0x02) state->reg |= (1ULL << 15);
		|			if (tmp & 0x01) state->reg |= (1ULL << 7);
		|			break;
		|		default:
		|			break;
		|		}
		|	}
		|	if (PIN_OE=> || (mode == 3)) {
		|		if (what == NULL && (state->ctx.do_trace & 2))
		|			what = "Z ";
		|		BUS_Y_Z();
		|	} else {
		|		if (what == NULL && (state->ctx.do_trace & 2))
		|			what = "out ";
		|		BUS_Y_WRITE(state->reg);
		|	}
		|	tmp = 0;
		|	if (state->reg & (1ULL << 56)) tmp |= 0x80;
		|	if (state->reg & (1ULL << 48)) tmp |= 0x40;
		|	if (state->reg & (1ULL << 40)) tmp |= 0x20;
		|	if (state->reg & (1ULL << 32)) tmp |= 0x10;
		|	if (state->reg & (1ULL << 24)) tmp |= 0x08;
		|	if (state->reg & (1ULL << 16)) tmp |= 0x04;
		|	if (state->reg & (1ULL <<  8)) tmp |= 0x02;
		|	if (state->reg & 1ULL)         tmp |= 0x01;
		|	BUS_Q_WRITE(tmp);
		|
		|	if (what != NULL) {
		|		TRACE(
		|		    << what
		|		    << "clk " << PIN_CLK.posedge()
		|		    << " s " << BUS_S_TRACE()
		|		    << " oe " << PIN_OE?
		|''')

        if "CLR" in self.comp:
            file.fmt('''
		|		    << " mr " << PIN_CLR?
		|''')

        file.fmt('''
		|		    << " ri " << BUS_RI_TRACE()
		|		    << " li " << BUS_LI_TRACE()
		|		    << " d " << BUS_D_TRACE()
		|		    << " q " << std::hex << tmp
		|		    << " | " << std::hex << state->reg
		|		);
		|	}
		|''')

class ModelF299(PartModel):
    ''' F299 registers '''

    def assign(self, comp, part_lib):

        for node in comp:
            if node.pin.name[:2] == 'DQ':
                pn = node.pin.name[2:]
                new_pin = Pin("D" + pn, "D" + pn, "input")
                Node(node.net, comp, new_pin)
                new_pin = Pin("Y" + pn, "Y" + pn, "tri_state")
                Node(node.net, comp, new_pin)
                node.remove()

        g1_node = comp["G1"]
        g2_node = comp["G2"]
        if g1_node.net == g2_node.net:
            oe_net = g1_node.net
        elif g1_node.net.is_pd():
            oe_net = g2_node.net
        elif g2_node.net.is_pd():
            oe_net = g1_node.net
        else:
            or_comp = Component(
                compref = comp.ref + "_" + "_OR",
                compvalue = comp.value,
                comppart = "F32"
            )
            comp.scm.add_component(or_comp)
            or_comp.name = comp.name + "_" + "_OR"
            or_comp.part = part_lib[or_comp.partname]

            oe_net = Net(self.name + "_" + "_OE")
            comp.scm.add_net(oe_net)

            Node(oe_net, or_comp, Pin("Q", "Q", "output"))
            Node(g1_node.net, or_comp, Pin("D0", "D0", "input"))
            Node(g2_node.net, or_comp, Pin("D1", "D1", "input"))

        new_pin = Pin("OE", "OE", "input")
        new_node = Node(oe_net, comp, new_pin)
        g1_node.remove()
        g2_node.remove()

        super().assign(comp, part_lib)


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F299", ModelF299("F299", F299))
    part_lib.add_part("F299X2", ModelF299("F299X2", F299))
    part_lib.add_part("F299X8", ModelF299("F299X8", F299X8))
