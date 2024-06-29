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
		|	bool p_mcyc2_nxt = PIN_MC2N;
		|	unsigned dbusmode;
		|	BUS_DBMD_READ(dbusmode);
		|	bool p_seta_sel = PIN_SETA;
		|	bool p_setb_sel = PIN_SETB;
		|	if (PIN_Q4.posedge()) {
		|		output.tadin =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_seta_sel)) ||
		|		    (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		    (  dbusmode == 0 || dbusmode == 2 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7 );
		|		output.tbdin =
		|		    (  cmd == 0xa && dbusmode == 0xa && (!p_setb_sel)) ||
		|		    (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		    (  dbusmode == 8 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7 ) ||
		|		    (  dbusmode == 2 );
		|		output.intas =
		|		    !(
		|		        (dbusmode == 1 || dbusmode == 3) ||
		|		        (dbusmode == 4)
		|		    );
		|		output.extsl =
		|		    !(
		|		        (dbusmode == 1) || 
		|		        (dbusmode == 6 || dbusmode == 7)
		|		    );
		|		output.intan =
		|		    !(
		|		        (  (cmd == 0xa || cmd == 0xb) && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_seta_sel)) ||
		|		        (  (cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  dbusmode == 0 ) || 
		|			(  4 <= dbusmode && dbusmode <= 7 ) ||
		|		        (  dbusmode == 2 || dbusmode == 3 )
		|		    );
		|		output.intbn =
		|		    !(
		|		        (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa && (!p_setb_sel)) ||
		|		        (  cmd == 0xb && (!p_mcyc2_nxt) && dbusmode == 1   && (!p_setb_sel)) ||
		|		        (  (cmd == 0xd || cmd == 0xf) && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  cmd == 0x7 && (!p_mcyc2_nxt) && dbusmode == 1 ) ||
		|		        (  dbusmode == 8 ) ||
		|		        (  4 <= dbusmode && dbusmode <= 7) || 
		|		        (  dbusmode == 3 )
		|		    );
		|		output.taoe =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 &&   p_setb_sel ) ||
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa &&   p_setb_sel ) ||
		|		    (  (cmd == 0x6 || cmd == 0x7)   && (!p_mcyc2_nxt) && dbusmode == 1 &&   p_setb_sel ) ||
		|		    (  dbusmode == 8 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7) ||
		|		    (  dbusmode == 2 );
		|		output.tboe =
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_setb_sel)) ||
		|		    (  cmd == 0xa && (!p_mcyc2_nxt) && dbusmode == 0xa && (!p_setb_sel)) ||
		|		    (  (cmd == 0x6 || cmd == 0x7) && (!p_mcyc2_nxt) && dbusmode == 1 && (!p_setb_sel)) ||
		|		    (  dbusmode == 0 || dbusmode == 2 ) || 
		|		    (  4 <= dbusmode && dbusmode <= 7);
		|		output.droen =
		|		    (dbusmode == 2);
		|		output.intbs =
		|		    !(
		|		        (dbusmode == 1 || dbusmode == 3) || 
		|		        (dbusmode == 5)
		|		    );
		|		output.tadin = !output.tadin;
		|		output.tbdin = !output.tbdin;
		|		output.droen = !output.droen;
		|		output.intas = !output.intas;
		|		output.intbs = !output.intbs;
		|		output.extsl = !output.extsl;
		|		output.intan = !output.intan;
		|		output.intbn = !output.intbn;
		|	}
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XBUSPAL", PartModel("XBUSPAL", XBUSPAL))
