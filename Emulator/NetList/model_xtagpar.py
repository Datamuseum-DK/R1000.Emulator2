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
   MEM32 Tag parity
   ================

'''

from part import PartModel, PartFactory

class XTAGPAR(PartFactory):
    ''' MEM32 Tag parity '''

    def state(self, file):
        file.fmt('''
		|	unsigned ae, al, be, bl, sr, la, lb;
		|''')

    def sensitive(self):
        yield "PIN_CLK"
        yield "PIN_OEE"
        yield "PIN_OEL"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool pos = PIN_CLK.posedge();
		|	bool neg = PIN_CLK.negedge();
		|	uint64_t tag = 0, par = 0;
		|
		|	bool oee = PIN_OEE=>;
		|	bool oel = PIN_OEL=>;
		|	unsigned tspr;
		|	BUS_TSPR_READ(tspr);
		|	if (pos && tspr) {
		|		if (tspr == 3) {
		|#if 0
		|			if (!oee) {
		|				state->sr = state->ae << 8;
		|				state->sr |= state->be;
		|			} else if (!oel) {
		|				state->sr = state->al << 8;
		|				state->sr |= state->bl;
		|			} else {
		|				state->sr = 0xffff;
		|			}
		|#else
		|			state->sr = state->la << 8;
		|			state->sr |= state->lb;
		|#endif
		|		} else if (tspr == 1) {
		|			state->sr >>= 1;
		|			state->sr |= PIN_DIAG=> << 15;
		|		} else if (tspr == 2) {
		|			state->sr <<= 1;
		|			state->sr &= 0xf7f7;
		|		}
		|		PIN_TSPO<=(state->sr & 1);
		|	}
		|
		|	if (pos || neg) {
		|		BUS_TAG_READ(tag);
		|		par = (tag ^ (tag >> 4)) & 0x0f0f0f0f0f0f0f0f;
		|		par = (par ^ (par >> 2)) & 0x0303030303030303;
		|		par = (par ^ (par >> 1)) & 0x0101010101010101;
		|	}
		|	if (pos) {
		|		state->al = 0;
		|		state->al |= ((par >> 56) & 1) << 7;
		|		state->al |= ((par >> 48) & 1) << 6;
		|		state->al |= ((par >> 40) & 1) << 5;
		|		state->al |= ((par >> 32) & 1) << 4;
		|		state->al |= ((par >> 24) & 1) << 3;
		|		state->al |= ((par >> 16) & 1) << 2;
		|		state->al |= PIN_TS6L=> << 1;
		|		state->al |= ((par >> 0) & 1) << 0;
		|		state->bl = (tag >> 7) & 0xfc;
		|		state->bl |= (tag >> 8) & 0x01;
		|		state->bl |= PIN_TA6L=> << 1;
		|	}
		|	if (neg) {
		|		state->ae = 0;
		|		state->ae |= ((par >> 56) & 1) << 7;
		|		state->ae |= ((par >> 48) & 1) << 6;
		|		state->ae |= ((par >> 40) & 1) << 5;
		|		state->ae |= ((par >> 32) & 1) << 4;
		|		state->ae |= ((par >> 24) & 1) << 3;
		|		state->ae |= ((par >> 16) & 1) << 2;
		|		state->ae |= PIN_TS6E=> << 1;
		|		state->ae |= ((par >> 0) & 1) << 0;
		|		state->be = (tag >> 7) & 0xfc;
		|		state->be |= (tag >> 8) & 0x01;
		|		state->be |= PIN_TA6E=> << 1;
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
		|	TRACE(
		|		<< " clk^ " << pos
		|		<< " clkv " << neg
		|		<< " oee " << oee
		|		<< " oel " << oel
		|		<< " tag " << BUS_TAG_TRACE()
		|		<< " tspr " << BUS_TSPR_TRACE()
		|		<< " diag " << PIN_DIAG?
		|		<< " tspo " << (state->sr & 1)
		|		<< " tsmo " << PIN_TSMO?
		|		<< " la " << std::hex << state->la
		|		<< " lb " << std::hex << state->lb
		|		<< " perr " << (state->la != state->lb)
		|		<< " sr " << state->sr
		|		<< " par " << par
		|		<< " ae " << state->ae
		|		<< " al " << state->al
		|		<< " be " << state->be
		|		<< " bl " << state->bl
		|		<< std::dec
		|	);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTAGPAR", PartModel("XTAGPAR", XTAGPAR))
