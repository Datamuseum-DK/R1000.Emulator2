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

    def state(self, file):
        file.fmt('''
		|	bool names, path, aop, bop, iop;
		|	uint64_t ofreg;
		|	bool okm;
		|	bool aeql;
		|	bool aeqb;
		|	bool beql;
		|	bool able;
		|	bool clce;
		|	bool clev;
		|	bool sysu;
		|	unsigned bbit;
		|	unsigned bbuf;
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

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_NAMES<=(state->names);
		|		PIN_PATH<=(state->path);
		|		PIN_AOP<=(state->aop);
		|		PIN_BOP<=(state->bop);
		|		PIN_IOP<=(state->iop);
		|		PIN_OKM<=(state->okm);
		|		PIN_AEQL<=(state->aeql);
		|		PIN_BEQL<=(state->beql);
		|		PIN_AEQB<=(state->aeqb);
		|		PIN_ABLE<=(state->able);
		|		PIN_CLCE<=(state->clce);
		|		PIN_CLEV<=(state->clev);
		|		PIN_SYSU<=(state->sysu);
		|		BUS_BBIT_WRITE(state->bbit);
		|		BUS_BBUF_WRITE(state->bbuf);
		|	}
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
		|	aop = !(a35 && (aopm || a34));
		|	bop = !(b35 && (bopm || b34));
		|
		|	iop = !(
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
		|	bool aeql = (a & 0x7f) != l;
		|	bool aeqb = (a & 0x7f) != (b & 0x7f);
		|	bool beql = (b & 0x7f) != l;
		|	bool able = !(aeql | aeqb);
		|
		|	unsigned mask_a = state->prom[l] >> 1;
		|	unsigned okpat_a = state->prom[l + 256] >> 1;
		|	bool oka = (0x7f ^ (mask_a & (b & 0x7f))) != okpat_a;
		|
		|	unsigned mask_b = state->prom[l + 128] >> 1;
		|	unsigned okpat_b = state->prom[l + 384] >> 1;
		|	bool okb = (0x7f ^ (mask_b & (b & 0x7f))) != okpat_b;
		|
		|	bool okm = !(oka & okb);
		|
		|	bool clce = (ucod >> 1) != 0xf;
		|
		|	bool ucatol = (ucod >> 4) & 1;
		|	bool ucatob = (ucod >> 3) & 1;
		|	bool ucbtol = (ucod >> 2) & 1;
		|	bool ucabl = (ucod >> 1) & 1;
		|	bool clsysb = (ucod >> 0) & 1;
		|	bool clev = !(
		|	    (!ucatol & !aeql) ||
		|	    (!ucatob & !aeqb) ||
		|	    (!ucbtol & !beql) ||
		|	    (!ucabl & !aeqb & !beql)
		|	);
		|	bool sysu = !(clsysb | !beql);
		|
		|	unsigned bbit = 0;
		|	bbit |= ((b >> BUS_B_LSB(0)) & 1) << 6;
		|	bbit |= ((b >> BUS_B_LSB(21)) & 1) << 5;
		|	bbit |= ((b >> BUS_B_LSB(36)) & 0x1f) << 0;
		|
		|	unsigned bbuf = b & 7;
		|
		|	TRACE(
		|	    << " a " << BUS_A_TRACE()
		|	    << " b " << BUS_B_TRACE()
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
		|
		|	if (names != state->names ||
		|	    path != state->path ||
		|	    aop != state->aop ||
		|	    bop != state->bop ||
		|	    iop != state->iop ||
		|	    aeql != state->aeql ||
		|	    aeqb != state->aeqb ||
		|	    beql != state->beql ||
		|	    able != state->able ||
		|	    okm != state->okm ||
		|	    clce != state->clce ||
		|	    clev != state->clev ||
		|	    sysu != state->sysu ||
		|	    bbit != state->bbit ||
		|	    bbuf != state->bbuf
		|	) {
		|		state->ctx.job = 1;
		|		state->names = names;
		|		state->path = path;
		|		state->aop = aop;
		|		state->bop = bop;
		|		state->iop = iop;
		|		state->aeql = aeql;
		|		state->aeqb = aeqb;
		|		state->beql = beql;
		|		state->able = able;
		|		state->okm = okm;
		|		state->clce = clce;
		|		state->clev = clev;
		|		state->sysu = sysu;
		|		state->bbit = bbit;
		|		state->bbuf = bbuf;
		|		next_trigger(5, SC_NS);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XPRIVCMP", PartModel("XPRIVCMP", XPRIVCMP))
