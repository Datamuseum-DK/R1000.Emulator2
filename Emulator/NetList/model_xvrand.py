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
   VAL UIR.RAND decode
   ===================

'''

from part import PartModel, PartFactory

class XVRAND(PartFactory):
    ''' VAL UIR.RAND decode '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned rand;
		|	BUS_RAND_READ(rand);
		|
		|	if (rand < 8) {
		|		output.alu = 7;
		|	} else {
		|		output.alu = 15 - rand;
		|	}
		|	output.incl = rand != 0x1;
		|	output.decl = rand != 0x2;
		|	output.spltc = rand != 0x4;
		|	output.cntz = rand != 0x5;
		|	output.glit = rand != 0x6;
		|	output.div = rand != 0xb;
		|	output.stmul = rand != 0xc;
		|	output.prl16 = rand != 0xd;
		|	output.prl32 = rand != 0xe;
		|	output.sneak = (rand != 0x3) && (rand != 0x6);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVRAND", PartModel("XVRAND", XVRAND))
