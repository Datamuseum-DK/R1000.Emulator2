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
   8-bit adder
   ===========

'''


from part import PartModel, PartFactory

class XADD(PartFactory):

    ''' N bit adder '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a, b, sum;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	sum = a + b;
		|	if (PIN_CI=>)
		|		sum++;
		|	TRACE (
		|	    << "a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " ci " << PIN_CI?
		|	    << " | " << std::hex << sum
		|	);
		|	BUS_Y_WRITE(sum);
		|	PIN_CO<=(sum >> BUS_Y_WIDTH);
		|''')

class XSUB(PartFactory):

    ''' N bit adder '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned a, b, diff;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	diff = b - a;
		|	if (!PIN_CI=>)
		|		diff--;	// Unused at fiu_33
		|	TRACE (
		|	    << "a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " ci " << PIN_CI?
		|	    << " | " << std::hex << diff
		|	);
		|	BUS_Y_WRITE(diff);
		|	PIN_CO<=(diff >> BUS_Y_WIDTH);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XADD8", PartModel("XADD8", XADD))
    part_lib.add_part("XSUB8", PartModel("XSUB8", XSUB))
    part_lib.add_part("XADD14", PartModel("XADD14", XADD))
