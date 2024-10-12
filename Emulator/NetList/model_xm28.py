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
   MEM32 page 28
   =============

'''

# TEST_HIT_FLOPS tests [AB]_AHIT~ but not [AB]HIT~

from part import PartModel, PartFactory

class XM28(PartFactory):
    ''' MEM32 page28 '''

    autopin = True

    def state(self, file):
        file.fmt('''
		|	bool bhit, ahit;
		|	bool dradpal_p22;
		|	unsigned hits;
		|''')

    def sensitive(self):
        yield "PIN_CLK.neg()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|#define CMD_PMW	(1<<0xf)
		|#define CMD_PMR	(1<<0xe)
		|#define CMD_LMW	(1<<0xd)
		|#define CMD_LMR	(1<<0xc)
		|#define CMD_C01	(1<<0xb)
		|#define CMD_MTT	(1<<0xa)
		|#define CMD_C10	(1<<0x9)
		|#define CMD_SFF	(1<<0x8)
		|#define CMD_PTW	(1<<0x7)
		|#define CMD_PTR	(1<<0x6)
		|#define CMD_INI	(1<<0x5)
		|#define CMD_LTR	(1<<0x4)
		|#define CMD_NMQ	(1<<0x3)
		|#define CMD_LRQ	(1<<0x2)
		|#define CMD_AVQ	(1<<0x1)
		|#define CMD_IDL	(1<<0x0)
		|
		|	bool clk2x_neg = PIN_CLK.negedge();
		|	bool h1 = PIN_H1=>;
		|	bool q1pos = clk2x_neg && h1;
		|	bool aehit = PIN_AEH=>;
		|	bool alhit = PIN_ALH=>;
		|	bool behit = PIN_BEH=>;
		|	bool blhit = PIN_BLH=>;
		|	bool miss = aehit && alhit && behit && blhit;
		|	bool high_board = !PIN_LOBRD=>;
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|	unsigned bcmd = 1 << cmd;
		|#define CMDS(x) ((bcmd & (x)) != 0)
		|	bool mcyc2 = PIN_MC2=>;
		|
		|	unsigned pset;
		|	BUS_PSET_READ(pset);
		|
		|	if (clk2x_neg) {
		|		if (!mcyc2) {
		|			output.da2sl = false;
		|			if (state->dradpal_p22 && state->output.da2sl) {
		|				output.daa2d = behit && aehit;
		|			}
		|		} else if (q1pos) {
		|			output.da2sl = false;
		|			output.daa1d = false;
		|			output.daa2d = true;
		|		} else {	// q3pos
		|
		|			bool pht26 = !(
		|				((pset & 0xb) == 0xa &&  high_board) ||
		|				((pset & 0xb) == 0x2 && !high_board)
		|			);
		|
		|			output.da2sl = miss && CMDS(CMD_IDL|CMD_AVQ|CMD_LRQ|CMD_NMQ|CMD_LTR|CMD_INI|CMD_LMR|CMD_LMW);
		|
		|			output.daa1d = !miss;
		|
		|			output.daa2d = behit && aehit && (
		|			    ( !alhit ) ||
		|			    ( !blhit ) ||
		|			    ( pht26 ) ||
		|			    CMDS(CMD_IDL|CMD_AVQ|CMD_LRQ|CMD_NMQ|CMD_LTR|CMD_INI|CMD_LMR|CMD_LMW)
		|			);
		|		}
		|
		|		state->dradpal_p22 = mcyc2;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM28", PartModel("XM28", XM28))
