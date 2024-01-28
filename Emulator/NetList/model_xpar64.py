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
   8x8 parity checker
   ==================

'''


from part import PartModel, PartFactory

class XPAR64(PartFactory):
    ''' 8x8 parity checker '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''


        super().doit(file)

        file.fmt('''
		|	uint64_t tmp, total = 0, par = 0;
		|
		|	BUS_I_READ(tmp);
		|	par = odd_parity64(tmp);
		|	if (PIN_ODD=>)
		|		par ^= 0xff;
		|	output.p = par;
		|	total = odd_parity(par);
		|
		|	TRACE(
		|	    << " i " << BUS_I_TRACE()
		|	    << " p " << std::hex << par
		|	    << " a " << total
		|	);
		|
		|	output.pall = total & 1;
		|
		|''')

class XPAR32(PartFactory):

    ''' 4x8 parity checker '''

    # XXX: autopin fails XPAR32

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint32_t tmp, total = 0, par = 0;
		|
		|	BUS_I_READ(tmp);
		|	tmp = (tmp ^ (tmp >> 4)) & 0x0f0f0f0f;
		|	tmp = (tmp ^ (tmp >> 2)) & 0x03030303;
		|	tmp = (tmp ^ (tmp >> 1)) & 0x01010101;
		|
		|	if (PIN_ODD=>)
		|		tmp ^= 0x01010101;
		|
		|	if (tmp & (1ULL<<24)) par |= 0x8;
		|	if (tmp & (1ULL<<16)) par |= 0x4;
		|	if (tmp & (1ULL<<8)) par |= 0x2;
		|	if (tmp & (1ULL<<0)) par |= 0x1;
		|	BUS_P_WRITE(par);
		|
		|	total = (tmp ^ (tmp >> 16)) & 0x0101;
		|	total = (total ^ (total >> 8)) & 0x01;
		|
		|	if (PIN_ODD=>)
		|		total ^= 0x1;
		|
		|	TRACE(
		|	    << " i " << BUS_I_TRACE()
		|	    << " p " << std::hex << par
		|	    << " a " << total
		|	);
		|
		|	PIN_PALL<=(total & 1);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XPAR32", PartModel("XPAR32", XPAR32))
    part_lib.add_part("XPAR64", PartModel("XPAR64", XPAR64))
