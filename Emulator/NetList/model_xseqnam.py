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

from part import PartModel, PartFactory

class XSEQNAM(PartFactory):
    ''' SEQ Name generation '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint32_t tost;
		|	uint32_t vost;
		|	uint32_t namram[1<<BUS_RADR_WIDTH];
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

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
		|		BUS_ITYP_READ(state->tost);
		|		BUS_IVAL_READ(state->vost);
		|	}
		|
		|	if (PIN_RAMWE.posedge()) {
		|		unsigned radr;
		|		BUS_RADR_READ(radr);
		|		BUS_ITYP_READ(state->namram[radr]);
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
		|	output.z_qtyp = PIN_QTYPOE=>;
		|	if (!output.z_qtyp) {
		|		output.qtyp = name_bus ^ BUS_QTYP_MASK;
		|	}
		|
		|	unsigned adr_name;
		|	if (PIN_ADRICD=>) {
		|		BUS_CODS_READ(adr_name);
		|	} else {
		|		adr_name = name_bus;
		|	}
		|
		|	output.z_adrn = output.nspoe;
		|	if (!output.z_adrn)
		|		output.adrn = adr_name;
		|	
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XSEQNAM", PartModel("XSEQNAM", XSEQNAM))
