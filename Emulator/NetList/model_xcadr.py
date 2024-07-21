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
   TV C-addr calculation
   =====================

'''

from part import PartModel, PartFactory

class XCADR(PartFactory):
    ''' TV C-addr calculation '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned csa_offset;
		|	unsigned topreg;
		|	unsigned botreg;
		|''')

    def sensitive(self):
        yield "PIN_UCLK.pos()"
        yield "PIN_CCLK.pos()"
        yield "PIN_H2"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	bool diag_mode = PIN_DMODE=>;
		|	unsigned diag;
		|	BUS_DIAG_READ(diag);
		|
		|	unsigned a, b, c;
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_C_READ(c);
		|
		|	bool bot_mux_sel, top_mux_sel, add_mux_sel;
		|	bot_mux_sel = PIN_LBOT=>;
		|	add_mux_sel = PIN_LTOP=>;
		|	top_mux_sel = !(add_mux_sel && PIN_LPOP=>);
		|
		|	unsigned csmux3;
		|	if (diag_mode)
		|		csmux3 = diag & 0xf;
		|	else
		|		BUS_CSAO_READ(csmux3);
		|	csmux3 ^= 0xf;
		|
		|	unsigned csmux0;
		|	if (add_mux_sel)
		|		csmux0 = state->botreg;
		|	else
		|		csmux0 = state->topreg;
		|
		|	unsigned csalu0 = csmux3 + csmux0 + 1;
		|
		|	if (PIN_UCLK.posedge()) {
		|		state->csa_offset = csmux3;
		|	}
		|	if (PIN_CCLK.posedge()) {
		|		if (!bot_mux_sel)
		|			state->botreg = csalu0;
		|		if (top_mux_sel)
		|			state->topreg = csalu0;
		|	}
		|
		|	unsigned atos = (a & 0xf) + state->topreg + 1;
		|	unsigned btos = (b & 0xf) + state->topreg + 1;
		|
		|	unsigned csa = state->botreg + (b&1);
		|	if (!(b & 2)) {
		|		csa += state->csa_offset;
		|	}
		|
		|	unsigned ctl;
		|	BUS_CTL_READ(ctl);
		|
		|	unsigned foo;
		|	if (ctl & 4) {
		|		foo = state->botreg;
		|	} else {
		|		foo = c & 0xf;
		|	}
		|
		|	unsigned bar;
		|	if (ctl & 8) {
		|		bar = 0;
		|	} else if (ctl & 4) {
		|		bar = state->csa_offset;
		|	} else {
		|		bar = state->topreg;
		|	}
		|
		|	unsigned sum;
		|	if (ctl & 0x10) {
		|		sum = foo + bar + 1;
		|	} else if (ctl & 0x20) {
		|		sum = foo | bar;
		|	} else {
		|		printf("XXX: CTL 0x%02x\\n", ctl);
		|		sum = 5;
		|	}
		|
		|	unsigned cadr = 0, frm, loop;
		|	BUS_FRM_READ(frm);
		|	BUS_LOOP_READ(loop);
		|	if (ctl & 2) {
		|		cadr |= loop & 0xf;
		|	} else {
		|		cadr |= sum & 0xf;
		|	}
		|
		|	if (ctl & 1) {
		|		// nothing
		|	} else if (ctl & 2) {
		|		cadr |= loop & 0x3c0;
		|	} else {
		|		cadr |= (frm & 0x1e) << 5;
		|	}
		|
		|	if (ctl & 1) {
		|		// nothing
		|	} else if (ctl & 2) {
		|		cadr |= loop & 0x20;
		|	} else {
		|		cadr |= (frm & 1) << 5;
		|	}
		|
		|	if (ctl & 2) {
		|		cadr |= loop & 0x10;
		|	} else {
		|		cadr |= c & 0x10;
		|	}
		|
		|	unsigned aadr = 0, badr = 0;
		|	if (!PIN_H2=>) {
		|		if (PIN_ALOOP=>) {
		|			aadr = loop;
		|		} else {
		|			if (!(a & 0x20)) {
		|				aadr = frm << 5;
		|			}
		|			aadr |= (a & 0x10);
		|			if ((a & 0x30) != 0x20) {
		|				aadr |= a & 0xf;
		|			} else {
		|				aadr |= atos & 0xf;
		|			}
		|		}
		|
		|		if (PIN_BLOOP=>) {
		|			badr = loop;
		|		} else {
		|			if (!(b & 0x20)) {
		|				badr = frm << 5;
		|			}
		|			badr |= (b & 0x10);
		|			if ((b & 0x30) != 0x20) {
		|				badr |= b & 0xf;
		|			} else if ((b & 0x3c) == 0x28) {
		|				badr |= csa & 0xf;
		|			} else {
		|				badr |= btos & 0xf;
		|			}
		|		}
		|	} else {
		|		aadr = cadr;
		|		badr = cadr;
		|	}
		|	output.aadr = aadr;
		|	output.badr = badr;
		|
		|	TRACE(
		|		<< " uclk^ " << PIN_UCLK.posedge()
		|		<< " cclk^ " << PIN_CCLK.posedge()
		|		<< " uclk " << PIN_UCLK?
		|		<< " cclk " << PIN_CCLK?
		|		<< " h2 " << PIN_H2?
		|		<< " a " << std::hex << a
		|		<< " b " << std::hex << b
		|		<< " c " << std::hex << c
		|		<< " dm " << diag_mode
		|		<< " diag " << std::hex << diag
		|		<< " bot " << PIN_LBOT?
		|		<< " top " << PIN_LTOP?
		|		<< " pop " << PIN_LPOP?
		|		<< " csao " << BUS_CSAO_TRACE()
		|		<< " ctl " << BUS_CTL_TRACE()
		|		<< " frm " << BUS_FRM_TRACE()
		|		<< " loop " << BUS_LOOP_TRACE()
		|		<< " aloop " << PIN_ALOOP?
		|		<< " bloop " << PIN_BLOOP?
		|		<< " - aadr " << std::hex << aadr
		|		<< " badr " << std::hex << badr
		|		<< " cadr " << std::hex << cadr
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCADR", PartModel("XCADR", XCADR))
