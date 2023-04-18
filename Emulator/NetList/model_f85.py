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
   F85 4-bit magnitude comparator
   ===================================

   Ref: Philips IC15 1994 Sep 27
'''

from part import PartModel, PartFactory

class F85(PartFactory):

    ''' F85 4-bit magnitude comparator '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a = 0, b = 0, o = 0;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	if (a > b) {
		|		o = 0x4;
		|	} else if (a < b) {
		|		o = 0x1;
		|	} else {
		|		if (!PIN_Elt=> && !PIN_Eeq=>)
		|			o |= 0x4;
		|		if (PIN_Eeq=>)
		|			o |= 0x2;
		|		if (!PIN_Eeq=> && !PIN_Egt=>)
		|			o |= 0x1;
		|	}
		|	TRACE(
		|	    << " a " << a
		|	    << " " << BUS_A_TRACE()
		|	    << " b " << b
		|	    << " " << BUS_B_TRACE()
		|	    << " e< " << PIN_Elt?
		|	    << " e= " << PIN_Eeq?
		|	    << " e> " << PIN_Egt?
		|	    << " | " << (o & 4 ? ">" : "")
		|	    << (o & 2 ? "=" : "")
		|	    << (o & 1 ? "<" : "")
		|	);
		|	PIN_AgtB<=(o & 4);
		|	PIN_AeqB<=(o & 2);
		|	PIN_AltB<=(o & 1);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F85", PartModel("F85", F85))
