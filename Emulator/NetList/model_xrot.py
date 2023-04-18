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
   64x4 rotator
   ============

'''


from part import PartModel, PartFactory

class XROT16(PartFactory):

    ''' 16x4x2 rotator '''


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a, b, s, ab, y = 0;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_S_READ(s);
		|	BUS_AB_READ(ab);
		|	a >>= s;
		|	b >>= s;
		|	y |= (ab & 0x1) ? (b & 0x000f) : (a & 0x000f);
		|	y |= (ab & 0x2) ? (b & 0x00f0) : (a & 0x00f0);
		|	y |= (ab & 0x4) ? (b & 0x0f00) : (a & 0x0f00);
		|	y |= (ab & 0x8) ? (b & 0xf000) : (a & 0xf000);
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " s " << BUS_S_TRACE()
		|	    << " ab " << BUS_AB_TRACE()
		|	    << " y " << std::hex << y
		|	);
		|	BUS_Y_WRITE(y);
		|''')


class XROT64(PartFactory):

    ''' 64x4 rotator '''


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t s, i, yl = 0, yh = 0, y;
		|
		|	if (PIN_OE=>) {
		|		TRACE(<<"Z");
		|		BUS_Y_Z();
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|
		|	BUS_S_READ(s);
		|	BUS_I_READ(i);
		|	s <<= 2;
		|	yl = i >> s;
		|	yh = i << (64 - s);
		|	y = yh | yl;
		|	BUS_Y_WRITE(y);
		|	TRACE(
		|	    << " oe " << PIN_OE?
		|	    << " s " << BUS_S_TRACE()
		|	    << " i " << BUS_I_TRACE()
		|	    << " " << std::hex << i
		|	    << " y " << std::hex << y
		|	);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XROT16", PartModel("XROT16", XROT16))
    part_lib.add_part("XROT64", PartModel("XROT64", XROT64))
