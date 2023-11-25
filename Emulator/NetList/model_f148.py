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
   F148 8-Line to 3-Line Priority Encoder
   ======================================

   Ref: Fairchild DS009480 April 1988 Revised September 2000
'''

from part import PartModel, PartFactory

class F148(PartFactory):
    ''' F148 8-Line to 3-Line Priority Encoder '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	unsigned s, i;
		|
		|	BUS_I_READ(i);
		|	if (!(i & 0x80))
		|		s = 7;
		|	else if (!(i & 0x40))
		|		s = 6;
		|	else if (!(i & 0x20))
		|		s = 5;
		|	else if (!(i & 0x10))
		|		s = 4;
		|	else if (!(i & 0x08))
		|		s = 3;
		|	else if (!(i & 0x04))
		|		s = 2;
		|	else if (!(i & 0x02))
		|		s = 1;
		|	else if (!(i & 0x01))
		|		s = 0;
		|	else
		|		s = 8|16;
		|	if (PIN_E=>)
		|		s = 16;
		|	TRACE(
		|	    << " i " << BUS_I_TRACE()
		|	    << " e " << PIN_E?
		|	    << " | "
		|	    << std::hex << s
		|	);
		|	output.y = ~s;
		|	output.gs = (s >> 4) & 1;
		|	output.ez = !((s >> 3) & 1);
		|''')

class F148X2(PartFactory):
    ''' Dual F148 8-Line to 3-Line Priority Encoder '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	unsigned s, i;
		|
		|	BUS_I_READ(i);
		|	if (!(i & 0x8000))
		|		s = 15;
		|	else if (!(i & 0x4000))
		|		s = 14;
		|	else if (!(i & 0x2000))
		|		s = 13;
		|	else if (!(i & 0x1000))
		|		s = 12;
		|	else if (!(i & 0x0800))
		|		s = 11;
		|	else if (!(i & 0x0400))
		|		s = 10;
		|	else if (!(i & 0x0200))
		|		s = 9;
		|	else if (!(i & 0x0100))
		|		s = 8;
		|	else if (!(i & 0x0080))
		|		s = 7;
		|	else if (!(i & 0x0040))
		|		s = 6;
		|	else if (!(i & 0x0020))
		|		s = 5;
		|	else if (!(i & 0x0010))
		|		s = 4;
		|	else if (!(i & 0x0008))
		|		s = 3;
		|	else if (!(i & 0x0004))
		|		s = 2;
		|	else if (!(i & 0x0002))
		|		s = 1;
		|	else if (!(i & 0x0001))
		|		s = 0;
		|	else
		|		s = 16|32;
		|	if (PIN_E=>)
		|		s = 32;
		|	TRACE(
		|	    << " i " << BUS_I_TRACE()
		|	    << " e " << PIN_E?
		|	    << " | "
		|	    << std::hex << s
		|	);
		|	output.y = ~s;
		|	output.gs = (s >> 5) & 1;
		|	output.ez = !((s >> 4) & 1);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F148", PartModel("F148", F148))
    part_lib.add_part("F148X2", PartModel("F148X2", F148X2))
