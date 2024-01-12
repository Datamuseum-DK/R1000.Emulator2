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
   F182 Carry Lookahead Generator
   ==============================

   Ref: Fairchild DS009492 April 1988 Revised June 2002
   See also: http://www.righto.com/2017/03/inside-vintage-74182-alu-chip-how-it.html
'''

from part import PartModel, PartFactory

class F182(PartFactory):

    ''' F182 Carry Lookahead Generator '''

    autopin = True

    def extra(self, file):
        file.include("Components/tables.h")

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	unsigned adr = 0;
		|
		|	if (PIN_CI=>) adr |= 1 << 8;
		|	if (PIN_G3=>) adr |= 1 << 7;
		|	if (PIN_P3=>) adr |= 1 << 6;
		|	if (PIN_G2=>) adr |= 1 << 5;
		|	if (PIN_P2=>) adr |= 1 << 4;
		|	if (PIN_G1=>) adr |= 1 << 3;
		|	if (PIN_P1=>) adr |= 1 << 2;
		|	if (PIN_G0=>) adr |= 1 << 1;
		|	if (PIN_P0=>) adr |= 1 << 0;
		|	unsigned val = lut182[adr];
		|	output.co = 0;
		|	if (val & 0x10) output.co |= 1;
		|	if (val & 0x08) output.co |= 2;
		|	if (val & 0x04) output.co |= 4;
		|	output.cg =(val >> 1) & 0x1;
		|	output.cp =val & 0x1;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F182", PartModel("F182", F182))
