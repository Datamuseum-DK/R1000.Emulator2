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
   TYP Kind Matching
   =================

'''

from part import PartModel, PartFactory

class XTKIND(PartFactory):
    ''' TYP Kind Matching '''

    def state(self, file):
        file.fmt('''
		|	bool okm;
		|	bool aeql;
		|	bool aeqb;
		|	bool beql;
		|	bool able;
		|	bool clce;
		|	bool clev;
		|	bool sysu;
		|	uint8_t prom[512];
		|''')

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->prom, sizeof state->prom,
		|	    "PA059-01");
		|''')
        super().init(file)


    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		PIN_OKM<=(state->okm);
		|		PIN_AEQL<=(state->aeql);
		|		PIN_BEQL<=(state->beql);
		|		PIN_AEQB<=(state->aeqb);
		|		PIN_ABLE<=(state->able);
		|		PIN_CLCE<=(state->clce);
		|		PIN_CLEV<=(state->clev);
		|		PIN_SYSU<=(state->sysu);
		|	}
		|
		|	unsigned a, b, l, uc;
		|	BUS_A_READ(a);
		|	BUS_B_READ(b);
		|	BUS_CLIT_READ(l);
		|	BUS_UC_READ(uc);
		|
		|	bool aeql = a != l;
		|	bool aeqb = a != b;
		|	bool beql = b != l;
		|	bool able = !(aeql | aeqb);
		|
		|	unsigned mask_a = state->prom[l] >> 1;
		|	unsigned okpat_a = state->prom[l + 256] >> 1;
		|	bool oka = (0x7f ^ (mask_a & b)) != okpat_a;
		|
		|	unsigned mask_b = state->prom[l + 128] >> 1;
		|	unsigned okpat_b = state->prom[l + 384] >> 1;
		|	bool okb = (0x7f ^ (mask_b & b)) != okpat_b;
		|
		|	bool okm = !(oka & okb);
		|
		|	bool clce = (uc >> 1) != 0xf;
		|
		|	bool ucatol = (uc >> 4) & 1;
		|	bool ucatob = (uc >> 3) & 1;
		|	bool ucbtol = (uc >> 2) & 1;
		|	bool ucabl = (uc >> 1) & 1;
		|	bool clsysb = (uc >> 0) & 1;
		|	bool clev = !(
		|	    (!ucatol & !aeql) ||
		|	    (!ucatob & !aeqb) ||
		|	    (!ucbtol & !beql) ||
		|	    (!ucabl & !aeqb & !beql)
		|	);
		|	bool sysu = !(clsysb | !beql);
		|
		|	if (aeql != state->aeql ||
		|	    aeqb != state->aeqb ||
		|	    beql != state->beql ||
		|	    able != state->able ||
		|	    okm != state->okm ||
		|	    clce != state->clce ||
		|	    clev != state->clev ||
		|	    sysu != state->sysu
		|	) {
		|		state->aeql = aeql;
		|		state->aeqb = aeqb;
		|		state->beql = beql;
		|		state->able = able;
		|		state->okm = okm;
		|		state->clce = clce;
		|		state->clev = clev;
		|		state->sysu = sysu;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|	}
		|	
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XTKIND", PartModel("XTKIND", XTKIND))
