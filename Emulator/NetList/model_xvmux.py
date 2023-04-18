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
   Vector of NAND
   ==============
'''


from part import PartModel, PartFactory

class XVMUX(PartFactory):

    ''' Vector of NAND '''

    def private(self):
        ''' private variables '''
        for  i in "ab":
            yield from self.event_or(
                i + "_event",
                "BUS_%s" % i.upper(),
                "BUS_S",
            )

    def state(self, file):
        file.fmt('''
		|	bool once;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t a, b, s, q = 0, m;
		|	unsigned u;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_S_READ(s);
		|
		|	m = 1;
		|	for (u = 0; u < BUS_A_WIDTH; u++) {
		|		if (s & m)
		|			q |= b & m;
		|		else
		|			q |= a & m;
		|		m <<= 1;
		|	}
		|	BUS_Q_WRITE(q);
		|	TRACE (
		|	    << "a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " s " << BUS_S_TRACE()
		|	    << " q " << std::hex << q
		|	);
		|	if (!s)
		|		next_trigger(a_event);
		|	else if (s == BUS_S_MASK)
		|		next_trigger(b_event);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMUX232", PartModel("XMUX232", XVMUX))
