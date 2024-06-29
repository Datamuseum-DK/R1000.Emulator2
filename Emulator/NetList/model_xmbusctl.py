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
   MEM32 bus control
   =================

'''

# TEST_HIT_FLOPS tests [AB]_AHIT~ but not [AB]HIT~

from part import PartModel, PartFactory

class XMBUSCTL(PartFactory):
    ''' MEM32 bus control '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|
		|	bool buzz_off = !(PIN_DBUZZOF=>);
		|
		|	bool ext_hit = !(PIN_XHITA=> && PIN_XHITB=>);
		|	bool high_board = PIN_HIBOARD=>;
		|	bool d_drvmem = PIN_DDRVMEM=>;
		|	bool d_drvtag = PIN_DDRVTAG=>;
		|	bool b_tvdrv = PIN_TVDRV=>;
		|	bool b_vdrv = PIN_VDRV=>;
		|	bool ahit = PIN_AHIT=>;
		|	bool bhit = PIN_BHIT=>;
		|
		|	output.exthit = ext_hit;
		|
		|	output.typaoe = !(
		|		buzz_off &&
		|		!(
		|			ext_hit ||
		|			!bhit ||
		|			(ahit && high_board) ||
		|			(b_tvdrv && d_drvmem)
		|		)
		|	);
		|
		|	output.valaoe = !(
		|		buzz_off &&
		|		!(
		|			ext_hit ||
		|			!bhit ||
		|			(ahit && high_board) ||
		|			(b_tvdrv && d_drvmem && b_vdrv && d_drvtag)
		|		)
		|	);
		|
		|	output.typboe = !(
		|		buzz_off &&
		|		!(
		|			ext_hit ||
		|			bhit ||
		|			(b_tvdrv && d_drvmem)
		|		)
		|	);
		|
		|	output.valboe = !(
		|		buzz_off &&
		|		!(
		|			ext_hit ||
		|			bhit ||
		|			(b_tvdrv && d_drvmem && b_vdrv && d_drvtag)
		|		)
		|	);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XMBUSCTL", PartModel("XMBUSCTL", XMBUSCTL))
