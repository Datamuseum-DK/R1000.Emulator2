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
   FIU Address increment
   =====================

'''

from part import PartModel, PartFactory

class XFAINC(PartFactory):
    ''' FIU Address increment '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned mar_offset;
		|	BUS_MARO_READ(mar_offset);
		|	bool inc_mar = PIN_INMAR=>;
		|	bool page_xing = PIN_PXING=>;
		|	bool sel_pg_xing = PIN_SELPG=>;
		|	bool sel_incyc_px = PIN_SELIN=>;
		|
		|	unsigned marbot = mar_offset & 0x1f;
		|	unsigned inco = marbot;
		|	if (inc_mar && inco != 0x1f)
		|		inco += 1;
		|	inco |= mar_offset & 0x20;
		|	output.inco = inco;
		|	output.incp = odd_parity(inco);
		|	if (PIN_DPAR=>)
		|		output.incp ^= 1;
		|
		|	output.pxnx = (
		|		(page_xing && sel_pg_xing && sel_incyc_px) ||
		|		(!page_xing && sel_pg_xing && sel_incyc_px && inc_mar && marbot == 0x1f)
		|	);
		|
		|	output.wez = (mar_offset & 0x3f) == 0;
		|
		|	output.ntop = !	(marbot > 0x10) && (mar_offset & 0x20);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFAINC", PartModel("XFAINC", XFAINC))
