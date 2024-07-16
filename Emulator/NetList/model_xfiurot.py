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
   FIU Rotators
   ============

'''

from part import PartModelDQ, PartFactory

class XFIUROTV(PartFactory):
    ''' FIU Rotators '''

    autopin = True

    def private(self):
        ''' private variables '''
        yield from self.event_or(
           "fiu_event",
           "PIN_RCLK.posedge_event()",
           "PIN_QROE",
           "PIN_TVF",
           "BUS_DFI",
        )

    def state(self, file):
        file.fmt('''
		|	uint64_t reg;
		|	uint64_t tvo;
		|''')

    def sensitive(self):
        if "FIUROT" in self.name:
            yield "PIN_RCLK.pos()"
            yield "PIN_QROE"
            yield "PIN_TVF"
        else:
            yield from super().sensitive()

    def doit(self, file):
        ''' The meat of the doit() function '''

        if "FIUROT" in self.name:
             file.add_subst("«rot_typ»", "true")
        else:
             file.add_subst("«rot_typ»", "false")

        file.fmt('''
		|	bool pos = PIN_RCLK.posedge();
		|
		|	uint64_t vmsk = 0, tmsk = 0;
		|	if (PIN_ZLEN=>) {
		|		unsigned sbit, ebit;
		|		BUS_SBIT_READ(sbit);
		|		BUS_EBIT_READ(ebit);
		|
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
		|	uint64_t tii = 0;
		|#ifndef BUS_SEL_READ
		|	BUS_DR_READ(tii);
		|#else
		|	unsigned sel;
		|	bool sign;
		|
		|	BUS_SEL_READ(sel);
		|
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		sign = PIN_SIGN=>;
		|		if (sign)
		|			tii = BUS_DR_MASK;
		|		break;
		|	case 2:
		|		BUS_DR_READ(tii);
		|		break;
		|	case 3:
		|		BUS_DFI_READ(tii);
		|		tii ^= BUS_DFI_MASK;
		|		break;
		|	}
		|
		|#endif
		|
		|	uint64_t rdata;
		|	BUS_RD_READ(rdata);
		|
		|	uint64_t out = 0;
		|	if («rot_typ») {
		|		out = (rdata & tmsk);
		|		out |= (tii & (tmsk ^ BUS_DR_MASK));
		|	} else {
		|		out = (rdata & vmsk);
		|		out |= (tii & (vmsk ^ BUS_DR_MASK));
		|	}
		|
		|	uint64_t reg = state->reg;
		|	if (pos) {
		|		reg = out;
		|	}
		|
		|	output.z_qr = PIN_QROE=>;
		|	bool tvf = PIN_TVF=>;
		|
		|	uint64_t tvo = state->tvo;
		|	if (!output.z_qr and !tvf) {
		|		BUS_DFI_READ(tvo);
		|		tvo ^= BUS_DFI_MASK;
		|	} else if (!output.z_qr) {
		|		tvo = state->reg;
		|	}
		|
		|	output.qr = tvo;
		|
		|#ifdef BUS_QFI_WRITE
		|	output.z_qfi = PIN_QFIOE=>;
		|	if (!output.z_qfi) {
		|		output.qfi = out ^ BUS_QFI_MASK;
		|	}
		|
		|#endif
		|	if (
		|	    reg != state->reg ||
		|	    tvo != state->tvo
		|	) {
		|		state->reg = reg;
		|		state->tvo = tvo;
		|		next_trigger(5, sc_core::SC_NS);
		|	} else if («rot_typ» && !PIN_TVF=>) {
		|		idle_next = &fiu_event;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUROT", PartModelDQ("XFIUROT", XFIUROTV))
    part_lib.add_part("XFIUROV", PartModelDQ("XFIUROV", XFIUROTV))
