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
   FIU MAR &co
   ===========

'''

from part import PartModel, PartFactory
from pin import Pin
from node import Node

class XFMAR(PartFactory):
    ''' FIU MAR &co '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t srn, sro, par, ctopn, ctopo;
		|''')

    def sensitive(self):
        yield "PIN_CLK2X.pos()"
        yield "BUS_OREG"
        yield "BUS_INC"
        yield "PIN_VIOE"
        yield "PIN_YDIAGOE"
        yield "PIN_YSPCOE"
        yield "PIN_YADROE"
        yield "PIN_DGPAR"
        yield "PIN_COCLK.pos()"
        yield "BUS_CSA"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	uint64_t adr;
		|	BUS_DADR_READ(adr);
		|
		|	if (PIN_CLK2X.posedge()) {
		|		unsigned mode;
		|		unsigned msel;
		|		BUS_MSEL_READ(msel);
		|		bool load_mar = PIN_LMAR=>;
		|		bool sclk_en = PIN_SCLKE=>;
		|
		|		if (msel == 2 || msel == 3) {
		|			mode = msel;
		|		} else if (load_mar && sclk_en && msel == 1) {
		|			mode = 3;
		|		} else {
		|			mode = 0;
		|		}
		|
		|		if (mode == 3) {
		|			uint64_t tmp;
		|			state->srn = adr >> 32;
		|			state->sro = adr & 0xffffff80;
		|			BUS_DSPC_READ(tmp);
		|			state->sro |= tmp << 4;
		|			state->sro |= 0xf;
		|		} else if (mode == 2) {
		|			state->srn >>= 1;
		|			state->sro >>= 1;
		|			uint8_t diag;
		|			BUS_DDIAG_READ(diag);
		|			state->srn &= 0x7f7f7f7f;
		|			state->srn |= ((diag >> 7) & 0x1) << 0x1f;
		|			state->srn |= ((diag >> 6) & 0x1) << 0x17;
		|			state->srn |= ((diag >> 5) & 0x1) << 0x0f;
		|			state->srn |= ((diag >> 4) & 0x1) << 0x07;
		|			state->sro &= 0x7f7f7f7f;
		|			state->sro |= ((diag >> 3) & 0x1) << 0x1f;
		|			state->sro |= ((diag >> 2) & 0x1) << 0x17;
		|			state->sro |= ((diag >> 1) & 0x1) << 0x0f;
		|			state->sro |= ((diag >> 0) & 0x1) << 0x07;
		|		}
		|		output.madr = state->sro;
		|		output.madr |= (uint64_t)state->srn << 32;
		|		state->par = odd_parity64(state->srn) << 4;
		|		state->par |= offset_parity(state->sro) ^ 0xf;
		|		output.nmatch =
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
		|	}
		|
		|	if (PIN_CTCLK.posedge()) {
		|		state->ctopn = adr >> 32;
		|		output.ctpar = odd_parity64(state->ctopn) << 4;
		|		output.nmatch =
		|		    (state->ctopn != state->srn) ||
		|		    ((state->sro & 0xf8000070 ) != 0x10);
		|	}
		|
		|	unsigned oreg;
		|	BUS_OREG_READ(oreg);
		|
		|	state->par &= 0xfe;
		|	state->par |= (odd_parity(oreg) ^ 0xff) & 0x1;
		|
		|	if (PIN_DGPAR=>)
		|		output.par = state->par ^ 0xff;
		|	else
		|		output.par = state->par;
		|
		|	output.z_ydiag = PIN_YDIAGOE=>;
		|	if (!output.z_ydiag) {
		|		output.ydiag = 0;
		|		output.ydiag |= ((state->srn >> 24) & 1) << 7;
		|		output.ydiag |= ((state->srn >> 16) & 1) << 6;
		|		output.ydiag |= ((state->srn >>  8) & 1) << 5;
		|		output.ydiag |= ((state->srn >>  0) & 1) << 4;
		|		output.ydiag |= ((state->sro >> 24) & 1) << 3;
		|		output.ydiag |= ((state->sro >> 16) & 1) << 2;
		|		output.ydiag |= ((state->sro >>  8) & 1) << 1;
		|		output.ydiag |= ((state->sro >>  4) & 1) << 0;
		|	}
		|
		|	output.z_vi = PIN_VIOE=>;
		|	if (!output.z_vi) {
		|		output.vi = (uint64_t)state->srn << 32;
		|		output.vi |= state->sro & 0xffffff80;
		|		output.vi |= oreg;
		|		output.vi ^= BUS_VI_MASK;
		|	}
		|
		|	output.z_yspc = PIN_YSPCOE=>;
		|	if (!output.z_yspc) {
		|		output.yspc = (state->sro >> 4) & 7;
		|	}
		|
		|	output.z_yadr = PIN_YADROE=>;
		|	if (!output.z_yadr) {
		|		output.yadr = (uint64_t)state->srn << 32;
		|		output.yadr |= state->sro & 0xfffff000;
		|		unsigned inc;
		|		BUS_INC_READ(inc);
		|		output.yadr |= (inc & 0x1f) << 7;
		|		output.yadr |= oreg;
		|	}
		|
		|	unsigned csa;
		|	BUS_CSA_READ(csa);
		|	output.cld = csa > 1;
		|	output.ccnt = csa & 1;
		|	output.lctp = csa != 0;
		|
		|	if (PIN_COCLK.posedge()) {
		|		if (!output.cld) {
		|			state->ctopo = adr >> 7;
		|		} else if (!output.ccnt) {
		|			state->ctopo += 1;
		|		} else {
		|			state->ctopo += 0xfffff;
		|		}
		|		state->ctopo &= 0xfffff;
		|		output.cto = state->ctopo;
		|	}
		|''')

class ModelXFMAR(PartModel):
    ''' FIU MAR &co '''

    def assign(self, comp, part_lib):

        for node in comp:
            if node.pin.name[:1] == 'B':
                pn = node.pin.name[1:]
                new_pin = Pin("D" + pn, "D" + pn, "input")
                Node(node.net, comp, new_pin)
                new_pin = Pin("Y" + pn, "Y" + pn, "tri_state")
                Node(node.net, comp, new_pin)
                node.remove()

        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFMAR", ModelXFMAR("XFMAR", XFMAR))
