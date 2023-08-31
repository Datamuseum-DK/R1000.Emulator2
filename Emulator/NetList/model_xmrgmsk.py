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
   FIU Merge Mask
   ==============

'''

from part import PartModel, PartFactory

class XMRGMSK(PartFactory):
    ''' FIU Merge Mask '''

    def state(self, file):
        file.fmt('''
		|	uint64_t alat;
		|''')

    def xxsensitive(self):
        yield "PIN_FIU_CLK.pos()"
        yield "PIN_LOCAL_CLK.pos()"
        yield "PIN_Q1not.pos()"
        yield "PIN_DV_U"
        yield "PIN_BAD_HINT"
        yield "PIN_U_PEND"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned sbit, ebit;
		|	BUS_SBIT_READ(sbit);
		|	BUS_EBIT_READ(ebit);
		|	bool zl;
		|	zl = PIN_ZL=>;
		|	uint64_t t = 0, v = 0;
		|
		|	if (zl) {
		|		if (ebit == sbit) {
		|			if (ebit < 64) {
		|				t = 1ULL << (63 - ebit);
		|				v = 0;
		|			} else {
		|				t = 0;
		|				v = 1ULL << (127 - ebit);
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
		|				t = (~(uint64_t)0) >> sb;
		|			if (eb < 63)
		|				t ^= (~(uint64_t)0) >> (eb + 1);
		|			if (eb > 63)
		|				v = (~(uint64_t)0) << (127 - eb);
		|			if (sb > 64)
		|				v ^= (~(uint64_t)0) << (128 - sb);
		|			t ^= inv;
		|			v ^= inv;
		|		}
		|	}
		|	BUS_TMSK_WRITE(t);
		|	BUS_VMSK_WRITE(v);
		|	TRACE(
		|		<< " s " << BUS_SBIT_TRACE()
		|		<< " e " << BUS_EBIT_TRACE()
		|		<< " z " << PIN_ZL?
		|		<< " - "
		|		<< " sb " << std::hex << sbit
		|		<< " eb " << std::hex << ebit
		|		<< " t " << std::hex << t
		|		<< " v " << std::hex << v
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMRGMSK", PartModel("XMRGMSK", XMRGMSK))
