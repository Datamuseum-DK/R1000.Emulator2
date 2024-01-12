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
   VAL FIU conditions 
   ==================

'''

from part import PartModel, PartFactory

class XVFCND(PartFactory):
    ''' VAL FIU conditions '''

    autopin = True

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|
		|	output.fcond = false;
		|	unsigned zero = 0;
		|	switch (output.fcsel) {
		|	case 0:
		|		output.fcond = !PIN_ACO=>;
		|		break;
		|	case 1:
		|	case 3:
		|		output.fcond = PIN_LVAL=>;
		|		break;
		|	case 2:
		|		output.fcond = PIN_BBD0=>;
		|		break;
		|	case 4:
		|		BUS_AZ_READ(zero);
		|		output.fcond = (zero == 0xff);
		|		break;
		|	case 6:
		|		BUS_AZ_READ(zero);
		|		output.fcond = (zero != 0xff);
		|		break;
		|
		|	default:
		|		output.fcond = true;
		|		break;
		|	}
		|	output.fcond = !output.fcond;
		|
		|	unsigned sel;
		|	BUS_SEL_READ(sel);
		|
		|	output.fcsel = 0;
		|
		|	if (!(sel & 0x02))
		|		output.fcsel |= 0x4;
		|
		|	if ((sel & 0x2) && (PIN_BAD0=> ^ PIN_BBD0=>))
		|		output.fcsel |= 0x2;
		|
		|	if ((sel & 3) == 1)
		|		output.fcsel |= 0x2;
		|
		|	if (sel & 0x10)
		|		output.fcsel |= 0x1;
		|
		|	if ((sel & 0x06) == 0x06)
		|		output.fcsel |= 0x1;
		|
		|	if (PIN_SNK=>) {
		|		output.fcsel = 0x7;
		|	}
		|''')

    def doit_idle(self, file):
        file.fmt('''
		|	if (PIN_SNK=> && output.fcsel == 7) {
		|		next_trigger(PIN_SNK.negedge_event());
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVFCND", PartModel("XVFCND", XVFCND))
