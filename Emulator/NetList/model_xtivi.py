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
   FIU TIVI decoder
   ================

'''

from part import PartModel, PartFactory

class XTIVI(PartFactory):
    ''' FIU TIVI decoder '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned tvoe = 0xff;
		|
		|	unsigned tivi;
		|	BUS_TIVI_READ(tivi);
		|
		|	switch(tivi & 3) {
		|	case 0x0: tvoe &= 0xf7; break;
		|	case 0x1: tvoe &= 0xfb; break;
		|	case 0x2: tvoe &= 0xfd; break;
		|	case 0x3: tvoe &= 0xfe; break;
		|	}
		|
		|	switch(tivi & 0xc) {
		|	case 0x0: tvoe &= 0x7f; break;
		|	case 0x4: tvoe &= 0xbf; break;
		|	case 0x8: tvoe &= 0xdf; break;
		|	case 0xc:
		|		tvoe &= 0xef;
		|		tvoe |= 0x0f;
		|		break;
		|	}
		|	if (!(tvoe & 0x40)) {
		|		tvoe &= 0x7f;
		|	}
		|	if (!(tvoe & 0x02)) {
		|		tvoe &= 0xf7;
		|	}
		|	output.tvoe = tvoe;
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTIVI", PartModel("XTIVI", XTIVI))
