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
   MEM32 BUSPAL
   =============

'''

from part import PartModel, PartFactory

class XBUSPAL(PartFactory):
    ''' MEM32 BUSPAL '''

    autopin = True

    def sensitive(self):
        yield "PIN_Q4.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned cmd;
		|	BUS_CMD_READ(cmd);
		|	switch(cmd) {
		|	case 0x0:	// 0xf IDLE
		|	case 0x1:	// 0xe AVAILABLE QUERY
		|	case 0x2:	// 0xd LRU QUERY
		|	case 0x3:	// 0xc NAME QUERY
		|	case 0x4:	// 0xb LOGICAL TAG READ
		|	case 0x6:	// 0x9 PHYSICAL TAG READ
		|	case 0x7:	// 0x8 PHYSICAL TAG WRITE
		|	case 0xc:	// 0x3 LOGICAL MEM READ
		|	case 0xd:	// 0x2 LOGICAL MEM WRITE
		|	case 0xe:	// 0x1 PHYSICAL MEM READ
		|	case 0xf:	// 0x0 PHYSICAL MEM WRITE
		|		break;
		|	default:
		|		std::cerr << std::hex << "CMD " << cmd << "\\n";
		|		assert(cmd == 0x10);
		|		break;
		|	}
		|	bool p_mcyc2_nxt = PIN_MC2N;
		|
		|	// bool p_seta_sel = PIN_SETA;
		|	bool p_setb_sel = PIN_SETB;
		|	if (PIN_Q4.posedge()) {
		|		output.taoe =  (cmd == 0x6 || cmd == 0x7) && (!p_mcyc2_nxt)  &&   p_setb_sel;
		|		output.tboe =  (cmd == 0x6 || cmd == 0x7) && (!p_mcyc2_nxt)  && (!p_setb_sel);
		|		output.tadin = !(cmd == 0x7 && (!p_mcyc2_nxt));
		|		output.tbdin = !(cmd == 0x7 && (!p_mcyc2_nxt));
		|		output.intan = !((cmd == 0x7 || cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt));
		|		output.intbn = !((cmd == 0x7 || cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt));
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XBUSPAL", PartModel("XBUSPAL", XBUSPAL))
