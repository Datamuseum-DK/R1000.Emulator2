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

    autopin = True

    def state(self, file):
        file.fmt('''
		|	uint64_t ofreg;
		|	uint8_t prom[512];
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom, sizeof state->prom,
		|	    "PA059-01");
		|''')
        super().init(file)

    def sensitive(self):
        yield "BUS_A_SENSITIVE()"
        yield "BUS_B_SENSITIVE()"
        yield "BUS_CLIT_SENSITIVE()"
        yield "BUS_UCOD_SENSITIVE()"
        yield "PIN_OFC.pos()"
        yield "PIN_Q4"
        yield "PIN_UEN"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t a, b;
		|	bool tmp;
		|	bool a34, a35, b34, b35, dp;
		|
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	output.names = (a >> 32) == (b >> 32);
		|	tmp = ((a >> 7) & 0xfffff) == ((b >> 7) & 0xfffff);
		|	output.path = !(tmp && output.names);
		|#define BITN(x, n) ((x >> (63 - n)) & 1)
		|	a34 = BITN(a, 34);
		|	a35 = BITN(a, 35);
		|	b34 = BITN(b, 34);
		|	b35 = BITN(b, 35);
		|	dp = !(a35 && b35);
		|
		|	if (PIN_OFC.posedge()) {
		|		state->ofreg = b >> 32;
		|	}		
		|
		|	bool aopm = (a >> 32) == state->ofreg;
		|	bool bopm = (b >> 32) == state->ofreg;
		|	bool abim = !(!aopm | dp);
		|	bool bbim = !(!bopm | dp);
		|
		|	output.aop = !(a35 && (aopm || a34));
		|	output.bop = !(b35 && (bopm || b34));
		|
		|	output.iop = !(
		|		(abim && bbim) ||
		|		(bbim && a34) ||
		|		(abim && b34) ||
		|		(a34 && a35 && b34 && b35)
		|	);
		|
		|	unsigned l, ucod;
		|	BUS_CLIT_READ(l);
		|	BUS_UCOD_READ(ucod);
		|
		|	output.aeql = (a & 0x7f) != l;
		|	output.aeqb = (a & 0x7f) != (b & 0x7f);
		|	output.beql = (b & 0x7f) != l;
		|	output.able = !(output.aeql | output.aeqb);
		|
		|	unsigned mask_a = state->prom[l] >> 1;
		|	unsigned okpat_a = state->prom[l + 256] >> 1;
		|	bool oka = (0x7f ^ (mask_a & (b & 0x7f))) != okpat_a;
		|
		|	unsigned mask_b = state->prom[l + 128] >> 1;
		|	unsigned okpat_b = state->prom[l + 384] >> 1;
		|	bool okb = (0x7f ^ (mask_b & (b & 0x7f))) != okpat_b;
		|
		|	output.okm = !(oka & okb);
		|
		|	bool clce = (ucod >> 1) != 0xf;
		|
		|	bool ucatol = (ucod >> 4) & 1;
		|	bool ucatob = (ucod >> 3) & 1;
		|	bool ucbtol = (ucod >> 2) & 1;
		|	bool ucabl = (ucod >> 1) & 1;
		|	bool clsysb = (ucod >> 0) & 1;
		|	bool clev = !(
		|	    (!ucatol & !output.aeql) ||
		|	    (!ucatob & !output.aeqb) ||
		|	    (!ucbtol & !output.beql) ||
		|	    (!ucabl & !output.aeqb & !output.beql)
		|	);
		|	bool sysu = !(clsysb | !output.beql);
		|
		|	output.bbit = 0;
		|	output.bbit |= ((b >> BUS_B_LSB(0)) & 1) << 6;
		|	output.bbit |= ((b >> BUS_B_LSB(21)) & 1) << 5;
		|	output.bbit |= ((b >> BUS_B_LSB(36)) & 0x1f) << 0;
		|
		|	output.bbuf = b & 7;
		|
		|	unsigned priv_chk;
		|	BUS_UPVC_READ(priv_chk);
		|
		|	if (PIN_Q4.posedge()) {
		|		if (PIN_DMODE=>) {
		|			// nothing
		|		} else if (!PIN_SCKEN=>) {
		|			// nothing
		|		} else if (priv_chk == 7) {
		|			// nothing
		|		} else {
		|			output.ppriv = PIN_SPPRV=>;
		|		}
		|	}
		|
		|	bool micros_en = PIN_UEN=>;
		|
		|	unsigned selcond;
		|	if (output.ppriv && micros_en) {
		|		selcond = 0x80 >> priv_chk;
		|		selcond ^= 0xff;
		|	} else {
		|		selcond = 0xff;
		|	}
		|
		|	if (PIN_Q4.negedge()) {
		|		output.ue = BUS_UE_MASK;
		|
		|		if (micros_en && selcond == 0xbf && output.iop)
		|			output.ue &= ~0x20;	// T.BIN_OP.UE~
		|
		|		if (micros_en && selcond == 0x7f && output.path && output.iop)
		|			output.ue &= ~0x10;	// T.BIN_EQ.UE~
		|
		|		if (micros_en && clev && clce)
		|			output.ue &= ~0x08;	// T.CLASS.UE~
		|
		|		if (micros_en && selcond == 0xef && output.aop)
		|			output.ue &= ~0x04;	// T.TOS1_OP.UE~
		|		if (micros_en && selcond == 0xfb && output.bop)
		|			output.ue &= ~0x04;	// T.TOS1_OP.UE~
		|
		|		if (micros_en && selcond == 0xdf && output.aop)
		|			output.ue &= ~0x02;	// T.TOS_OP.UE~
		|		if (micros_en && selcond == 0xf7 && output.bop)
		|			output.ue &= ~0x02;	// T.TOS_OP.UE~
		|
		|		if (micros_en && sysu)
		|			output.ue &= ~0x01;	// T.CHK_SYS.UE~
		|	}
		|
		|	output.t0stp = true;
		|	if (micros_en && sysu)
		|		output.t0stp = false;
		|	if (micros_en && clce && clev)
		|		output.t0stp = false;
		|	if (micros_en && output.path && output.iop && selcond == 0x7f)
		|		output.t0stp = false;
		|
		|	output.t1stp = true;
		|	if (selcond == 0xbf && output.iop)
		|		output.t1stp = false;
		|	if ((selcond == 0xef || selcond == 0xdf) && output.aop)
		|		output.t1stp = false;
		|	if ((selcond == 0xf7 || selcond == 0xfb) && output.bop)
		|		output.t1stp = false;
		|
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XPRIVCMP", PartModel("XPRIVCMP", XPRIVCMP))
