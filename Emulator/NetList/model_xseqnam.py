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
   SEQ Name generation
   ===================

'''

from part import PartModelDQ, PartFactory

class XSEQNAM(PartFactory):
    ''' SEQ Name generation '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t tost, vost, cur_name;
		|	uint32_t namram[1<<BUS_RADR_WIDTH];
		|	unsigned pcseg, retseg, last, cseg;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	output.nspoe = !(PIN_DADOF=> && !(PIN_DADON=> && PIN_SEQAE=>));
		|
		|	output.z_ospc = output.nspoe;
		|	if (!output.z_ospc) {
		|		BUS_ISPC_READ(output.ospc);
		|		output.ospc ^= BUS_OSPC_MASK;
		|	}
		|
		|	if (!PIN_TOSCLK=>) {
		|		BUS_DT_READ(state->tost);
		|		BUS_DV_READ(state->vost);
		|	}
		|
		|	if (PIN_CNCK.posedge()) {
		|		BUS_DT_READ(state->cur_name);
		|	}
		|
		|	if (PIN_RAMWE.posedge()) {
		|		unsigned radr;
		|		BUS_RADR_READ(radr);
		|		BUS_DT_READ(state->namram[radr]);
		|	}
		|
		|	uint32_t name_bus;
		|	if (!PIN_TYPOE=>) {
		|		name_bus = state->tost ^ 0xffffffff;
		|	} else if (!PIN_VALOE=>) {
		|		name_bus = state->vost ^ 0xffffffff;
		|	} else if (!PIN_RAMCS=>) {
		|		unsigned radr;
		|		BUS_RADR_READ(radr);
		|		name_bus = state->namram[radr] ^ 0xffffffff;
		|	} else {
		|		name_bus = 0xffffffff;
		|	}
		|	output.z_qt = PIN_QTOE=>;
		|	if (!output.z_qt) {
		|		if (PIN_CNOE=>)
		|			output.qt = name_bus ^ BUS_QT_MASK;
		|		else
		|			output.qt = state->cur_name;
		|	}
		|
		|	if (PIN_RCLK.posedge()) {
		|		state->retseg = state->pcseg;
		|	}
		|	if (PIN_MCLK.posedge()) {
		|		unsigned val;
		|		BUS_DV_READ(val);
		|		val ^= BUS_DV_MASK;
		|		state->pcseg = val;
		|		state->pcseg &= 0xffffff;
		|	}
		|	if (!PIN_CSEL) {
		|		state->cseg = state->pcseg;
		|	} else {
		|		state->cseg = state->retseg;
		|	}
		|
		|	unsigned adr_name;
		|	if (PIN_ADRICD=>) {
		|		adr_name = state->cseg;
		|	} else {
		|		adr_name = name_bus;
		|	}
		|
		|	output.z_adrn = output.nspoe;
		|	if (!output.z_adrn)
		|		output.adrn = adr_name;
		|	
		|	output.z_qv = PIN_QVOE=>;
		|	if (!output.z_qv) {
		|		output.qv = state->cseg ^ BUS_QV_MASK;
		|	}
		|
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQNAM", PartModelDQ("XSEQNAM", XSEQNAM))
