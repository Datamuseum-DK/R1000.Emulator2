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
   TYP Privacy Comparator
   ======================

'''

from part import PartModel, PartFactory

class XPRIVCMP(PartFactory):
    ''' TYP Privacy Comparator '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t a, b;
		|	bool names, tmp, path;
		|	bool aop, bop, iop;
		|	bool a34, a35, b34, b35, dp;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	names = (a >> 32) == (b >> 32);
		|	tmp = ((a >> 7) & 0xfffff) == ((b >> 7) & 0xfffff);
		|	path = !(tmp && names);
		|#define BITN(x, n) ((x >> (63 - n)) & 1)
		|	a34 = BITN(a, 34);
		|	a35 = BITN(a, 35);
		|	b34 = BITN(b, 34);
		|	b35 = BITN(b, 35);
		|	dp = !(a35 && b35);
		|	aop = !(a35 && (PIN_AOM=> || a34));
		|	bop = !(b35 && (PIN_BOM=> || b34));
		|	iop = !(
		|		(PIN_ABM=> && PIN_BBM=>) ||
		|		(PIN_BBM=> && a34) ||
		|		(PIN_ABM=> && b34) ||
		|		(a34 && a35 && b34 && b35)
		|	);
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
		|	    << " aom " << PIN_AOM
		|	    << " bom " << PIN_BOM
		|	    << " abm " << PIN_ABM
		|	    << " bbm " << PIN_BBM
		|	    << " a34 " << a34
		|	    << " a35 " << a35
		|	    << " b34 " << b34
		|	    << " b35 " << b35
		|	    << " - n " << names
		|	    << " p " << path
		|	    << " a " << aop
		|	    << " b " << bop
		|	    << " i " << iop
		|	    << " d " << dp
		|	);
		|	PIN_NAMES<=(names);
		|	PIN_PATH<=(path);
		|	PIN_AOP<=(aop);
		|	PIN_BOP<=(bop);
		|	PIN_IOP<=(iop);
		|	PIN_DP<=(dp);
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XPRIVCMP", PartModel("XPRIVCMP", XPRIVCMP))
