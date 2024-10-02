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
   MEM32 page 30
   =============

'''

from part import PartModel, PartFactory

class XM30(PartFactory):
    ''' MEM32 page 30 '''

    def state(self, file):
        file.fmt('''
		|	bool cas_a, cas_b;
		|''')

    def sensitive(self):
        yield "PIN_CLK.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|#define CMD_PMW	(1<<0xf)	// PHYSICAL_MEM_WRITE
		|#define CMD_PMR	(1<<0xe)	// PHYSICAL_MEM_READ
		|#define CMD_LMW	(1<<0xd)	// LOGICAL_MEM_WRITE
		|#define CMD_LMR	(1<<0xc)	// LOGICAL_MEM_READ
		|#define CMD_C01	(1<<0xb)	// COPY 0 TO 1
		|#define CMD_MTT	(1<<0xa)	// MEMORY_TO_TAGSTORE
		|#define CMD_C10	(1<<0x9)	// COPY 1 TO 0
		|#define CMD_SFF	(1<<0x8)	// SET HIT FLIP FLOPS
		|#define CMD_PTW	(1<<0x7)	// PHYSICAL TAG WRITE
		|#define CMD_PTR	(1<<0x6)	// PHYSICAL TAG READ
		|#define CMD_INI	(1<<0x5)	// INITIALIZE MRU
		|#define CMD_LTR	(1<<0x4)	// LOGICAL TAG READ
		|#define CMD_NMQ	(1<<0x3)	// NAME QUERY
		|#define CMD_LRQ	(1<<0x2)	// LRU QUERY
		|#define CMD_AVQ	(1<<0x1)	// AVAILABLE QUERY
		|#define CMD_IDL	(1<<0x0)	// IDLE
		|
		|	if (state->ctx.job & 2) {
		|		state->ctx.job &= ~2;
		|		PIN_CASA<=(state->cas_a);
		|		PIN_CASB<=(state->cas_b);
		|		return;
		|	}
		|
		|	if (PIN_CLK.posedge()) {
		|		unsigned cmd;
		|		BUS_CMD_READ(cmd);
		|	unsigned bcmd = 1 << cmd;
		|#define CMDS(x) ((bcmd & (x)) != 0)
		|
		|		bool h1 = PIN_H1=>;
		|		bool mcyc2 = PIN_MC=>;
		|		bool mcyc2_next = PIN_MCN=>;
		|		bool ahit = PIN_AHIT=>;
		|		bool bhit = PIN_BHIT=>;
		|		bool late_abort = PIN_LAB=>;
		|
		|		bool cas_a = !(
		|		    (CMDS(CMD_LMR|CMD_PMR) && !h1 && !mcyc2_next) ||
		|		    (CMDS(CMD_LMW|CMD_PMW) && h1 && !mcyc2 && !ahit && !late_abort)
		|		);
		|		bool cas_b = !(
		|		    (CMDS(CMD_LMR|CMD_PMR) && !h1 && !mcyc2_next) ||
		|		    (CMDS(CMD_LMW|CMD_PMW) && h1 && !mcyc2 && !bhit && !late_abort)
		|		);
		|
		|		if (
		|		    cas_a != state->cas_a ||
		|		    cas_b != state->cas_b
		|		) {
		|			state->ctx.job |= 2;
		|			state->cas_a = cas_a;
		|			state->cas_b = cas_b;
		|			next_trigger(35, sc_core::SC_NS);
		|		}
		|
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XM30", PartModel("XM30", XM30))
