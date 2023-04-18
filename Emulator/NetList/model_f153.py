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
   F153 Dual 4-Input Multiplexer
   =============================

   Ref: Fairchild DS009482 April 1988 Revised September 2000
'''


from part import PartModel, PartFactory

class F153(PartFactory):

    ''' F153 Dual 4-Input Multiplexer '''

    def private(self):
        ''' private variables '''
        for  i in "abcd":
            yield from self.event_or(
                i + "_event",
                "BUS_%s" % i.upper(),
                "BUS_S",
                "BUS_E",
            )

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint tmp = 0, val, ena;
		|
		|	BUS_S_READ(tmp);
		|
		|	switch (tmp) {
		|	case 0:
		|		BUS_A_READ(val);
		|		next_trigger(a_event);
		|		break;
		|	case 1:
		|		BUS_B_READ(val);
		|		next_trigger(b_event);
		|		break;
		|	case 2:
		|		BUS_C_READ(val);
		|		next_trigger(c_event);
		|		break;
		|	case 3:
		|		BUS_D_READ(val);
		|		next_trigger(d_event);
		|		break;
		|	}
		|
		|	BUS_E_READ(ena);
		|	val &= ~ena;
		|
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " c " << BUS_C_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	    << " e " << BUS_E_TRACE()
		|	    << " s " << BUS_S_TRACE()
		|	    << " | " << val
		|	);
		|	BUS_Y_WRITE(val);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F153", PartModel("F153", F153))
