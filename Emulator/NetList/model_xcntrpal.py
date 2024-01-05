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
   MEM32 CNTRPAL
   =============

'''

from part import PartModel, PartFactory

class XCNTRPAL(PartFactory):
    ''' MEM32 CNTRPAL '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	unsigned cnt1;
		|	unsigned cnt2;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"
        yield "PIN_RFSH"
        yield "PIN_OVFI"
        yield "BUS_DCNT"

    def doit(self, file):

        file.fmt('''
		|
		|	bool refresh = PIN_RFSH=>;
		|	unsigned diag;
		|	BUS_DIAG_READ(diag);
		|	unsigned dcnt;
		|	BUS_DCNT_READ(dcnt);
		|	bool cnt8_ovf = PIN_OVFI=>;
		|	unsigned cnt1 = state->cnt1;
		|	unsigned cnt2 = state->cnt2;
		|
		|	if (PIN_CLK.posedge()) {
		|		if (!refresh) {
		|			if (cnt2 & 1) {
		|			} else if (cnt1 == 0x0) {
		|				cnt1 = 0x3;
		|			} else if (cnt1 == 0x3) {
		|				cnt1 = 0xc;
		|			} else if (cnt1 == 0xc) {
		|				cnt1 = 0xf;
		|			} else {
		|				cnt1 = 0x0;
		|			}
		|			cnt2 ^= 0x1;
		|		} else {
		|			switch (dcnt) {
		|			case 0x04:
		|				if (!cnt8_ovf)
		|					cnt1 = state->cnt1 + 1;
		|				break;
		|			case 0x06:
		|				cnt2 = state->cnt2 + 1;
		|				break;
		|			case 0x07:
		|				if (!cnt8_ovf)
		|					cnt2 = state->cnt2 + 1;
		|				break;
		|			case 0x0c:
		|				cnt1 = state->cnt2;
		|				break;
		|			case 0x0d:
		|				cnt2 = state->cnt1;
		|				break;
		|			case 0x0e:
		|				cnt1 = diag;
		|				break;
		|			case 0x0f:
		|				cnt2 = diag;
		|				break;
		|			default:
		|				if (dcnt >= 0x10)
		|					cnt2 = dcnt & 0xf;
		|				break;
		|			}
		|		}
		|		state->cnt1 = cnt1;
		|		state->cnt2 = cnt2;
		|		output.tra = cnt1;
		|	}
		|	output.ovfo =
		|	    !(
		|		((dcnt == 0x05) && (!cnt8_ovf)) ||
		|		(((dcnt & 0x1d) == 0x05) && (!cnt8_ovf) &&   cnt2 == 0xf ) ||
		|		((dcnt == 0x06) &&  cnt2 == 0xf ) ||
		|		(((dcnt & 0x1e) == 0x04) && (!cnt8_ovf) &&   cnt1 == 0xf )
		|	    );
		|	output.cen =
		|	    !(
		|		((!refresh) && (!(cnt2 & 1)) && ((cnt1) & 5) == 5) ||
		|		(  refresh  && ((dcnt & 0x1d) == 0x05)) ||
		|		(  refresh  && ((dcnt & 0x1e) == 0x04))
		|	    );
		|
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCNTRPAL", PartModel("XCNTRPAL", XCNTRPAL))
