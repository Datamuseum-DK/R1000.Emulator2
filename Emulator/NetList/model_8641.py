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
   DS8641 Quad Unified Bus Tranceiver
   ==================================

   Ref: National Semiconductor TL/F/5806  RRD-B30M36  January 1996
'''


from part import PartModel, PartFactory

class DS8641(PartFactory):

    ''' DS8641 Quad Unified Bus Tranceiver '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned tmp;
		|
		|	TRACE(
		|	    << " e_ " << BUS_EN_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " i " << BUS_IN_TRACE()
		|	);
		|	if (!PIN_EN0=> && !PIN_EN1=>) {
		|		BUS_IN_READ(tmp);
		|		tmp ^= BUS_B_MASK;
		|		BUS_B_WRITE(tmp);
		|	} else {
		|		BUS_B_Z();
		|	}
		|	BUS_B_READ(tmp);
		|	tmp ^= BUS_B_MASK;
		|	BUS_OUT_WRITE(tmp);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("8641", PartModel("8641", DS8641))
    part_lib.add_part("8641X8", PartModel("8641X8", DS8641))
    part_lib.add_part("8641X17", PartModel("8641X17", DS8641))
