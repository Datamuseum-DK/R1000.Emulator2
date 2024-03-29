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
   F181 4-bit Arithemtic Logic Unit
   ================================

   Ref: Fairchild DS009491 April 1988 Revised January 2004
   See also: http://www.righto.com/2017/03/inside-vintage-74181-alu-chip-how-it.html
'''

from part import PartModel, PartFactory

class F181(PartFactory):

    ''' F181 4-bit Arithemtic Logic Unit '''

    autopin = True

    def extra(self, file):
        file.include("Components/tables.h")

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned idx = 0, tmp;
		|
		|	if (PIN_CI=>) idx |= 1 << 13;
		|	if (PIN_M=>) idx |= 1 << 12;
		|	BUS_A_READ(tmp);
		|	idx |= (tmp << 8);
		|	BUS_B_READ(tmp);
		|	idx |= (tmp << 4);
		|	BUS_S_READ(tmp);
		|	idx |= tmp;
		|	unsigned val = lut181[idx];
		|	output.y = val >> 4;
		|	output.p = (val & 0x04);
		|	output.co = (val & 0x02);
		|	output.g = (val & 0x01);
		|''')

        if self.comp["AeqB"].pin.type.hiz:
            file.fmt('''
		|	if (val & 0x08) {
		|		output.z_aeqb = true;
		|		output.aeqb = true;
		|	} else {
		|		output.z_aeqb = false;
		|		output.aeqb = false;
		|	}
		|''')
        else:
            file.fmt('''
		|	if (val & 0x08) {
		|		output.aeqb = true;
		|	} else {
		|		output.aeqb = false;
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F181", PartModel("F181", F181))
