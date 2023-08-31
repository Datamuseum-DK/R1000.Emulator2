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
   FIU Rotators
   ============

'''

from part import PartModel, PartFactory

class XFIUROTV(PartFactory):
    ''' FIU Rotators '''

    def private(self):
        ''' private variables '''
        yield from self.event_or(
           "fiu_event",
           "PIN_RCLK.posedge_event()",
           "PIN_TVOOE",
           "PIN_TVF",
           "BUS_FII",
        )

    def state(self, file):
        file.fmt('''
		|	uint64_t reg;
		|	uint64_t tvo;
		|	bool tvoz;
		|''')
        if "FIUROV" in self.name:
            file.fmt('''
		|	uint64_t fip;
		|	bool fipz;
		|	uint64_t fio;
		|	bool fioz;
		|''')

    def sensitive(self):
        if "FIUROT" in self.name:
            yield "PIN_RCLK.pos()"
            yield "PIN_TVOOE"
            yield "PIN_TVF"
        else:
            yield from super().sensitive()

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        if "FIUROT" in self.name:
             file.add_subst("«rot_typ»", "true")
        else:
             file.add_subst("«rot_typ»", "false")

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		if (state->tvoz) {
		|			BUS_TVO_Z();
		|		} else {
		|			BUS_TVO_WRITE(state->tvo);
		|		}
		|#ifdef BUS_FIO_WRITE
		|		if (state->fioz) {
		|			BUS_FIO_Z();
		|		} else {
		|			BUS_FIO_WRITE(state->fio);
		|		}
		|		if (state->fipz) {
		|			BUS_FIP_Z();
		|		} else {
		|			BUS_FIP_WRITE(state->fip);
		|		}
		|#endif
		|	}
		|
		|	bool pos = PIN_RCLK.posedge();
		|
		|	uint64_t vmsk = 0, tmsk = 0;
		|	if (PIN_ZLEN=>) {
		|		unsigned sbit, ebit;
		|		BUS_SBIT_READ(sbit);
		|		BUS_EBIT_READ(ebit);
		|
		|		if (ebit == sbit) {
		|			if (ebit < 64) {
		|				tmsk = 1ULL << (63 - ebit);
		|				vmsk = 0;
		|			} else {
		|				tmsk = 0;
		|				vmsk = 1ULL << (127 - ebit);
		|			} 
		|		} else {
		|			uint64_t inv = 0;
		|			unsigned sb = sbit, eb = ebit;
		|			if (eb < sb) {
		|				sb = ebit + 1;
		|				eb = sbit - 1;
		|				inv = ~(uint64_t)0;
		|			}
		|			if (sb < 64)
		|				tmsk = (~(uint64_t)0) >> sb;
		|			if (eb < 63)
		|				tmsk ^= (~(uint64_t)0) >> (eb + 1);
		|			if (eb > 63)
		|				vmsk = (~(uint64_t)0) << (127 - eb);
		|			if (sb > 64)
		|				vmsk ^= (~(uint64_t)0) << (128 - sb);
		|			tmsk ^= inv;
		|			vmsk ^= inv;
		|		}
		|	}
		|
		|	uint64_t tii = 0;
		|#ifndef BUS_SEL_READ
		|	BUS_TVI_READ(tii);
		|#else
		|	unsigned sel;
		|	bool sign;
		|
		|	BUS_SEL_READ(sel);
		|
		|	switch(sel) {
		|	case 0:
		|	case 1:
		|		sign = PIN_SIGN=>;
		|		if (sign)
		|			tii = BUS_TVI_MASK;
		|		break;
		|	case 2:
		|		BUS_TVI_READ(tii);
		|		break;
		|	case 3:
		|		BUS_FII_READ(tii);
		|		tii ^= BUS_FII_MASK;
		|		break;
		|	}
		|
		|#endif
		|
		|	uint64_t rdata;
		|	BUS_RD_READ(rdata);
		|
		|	uint64_t out = 0;
		|	if («rot_typ») {
		|		out = (rdata & tmsk);
		|		out |= (tii & (tmsk ^ BUS_TVI_MASK));
		|	} else {
		|		out = (rdata & vmsk);
		|		out |= (tii & (vmsk ^ BUS_TVI_MASK));
		|	}
		|
		|	uint64_t reg = state->reg;
		|	if (pos) {
		|		reg = out;
		|	}
		|
		|	bool tvoz = PIN_TVOOE=>;
		|	bool tvf = PIN_TVF=>;
		|
		|	uint64_t tvo = state->tvo;
		|	if (!tvoz and !tvf) {
		|		BUS_FII_READ(tvo);
		|		tvo ^= BUS_FII_MASK;
		|	} else if (!tvoz) {
		|		tvo = state->reg;
		|	}
		|#ifdef BUS_FIO_WRITE
		|	bool fipz = PIN_FIPOE=>;
		|	uint8_t fip = state->fip;
		|	if (!fipz) {
		|		fip = odd_parity64(out);
		|		if (PIN_PDIAG=>)
		|			fip ^= 0xff;
		|	}
		|	bool fioz = PIN_FIOOE=>;
		|	uint64_t fio = state->fio;
		|	if (!fioz) {
		|		fio = out ^ BUS_FIO_MASK;
		|	}
		|	if (
		|		fio != state->fio ||
		|		fioz != state->fioz ||
		|		fip != state->fip ||
		|		fipz != state->fipz ||
		|#else
		|	if (
		|#endif
		|	    reg != state->reg ||
		|	    tvoz != state->tvoz ||
		|	    tvo != state->tvo
		|	) {
		|		state->ctx.job = 1;
		|		state->tvoz = tvoz;
		|		state->reg = reg;
		|		state->tvo = tvo;
		|#ifdef BUS_FIO_WRITE
		|		state->fio = fio;
		|		state->fioz = fioz;
		|		state->fip = fip;
		|		state->fipz = fipz;
		|#endif
		|		next_trigger(10, SC_NS);
		|	} else if («rot_typ» && !PIN_TVF=>) {
		|		next_trigger(fiu_event);
		|	}
		|#if 0
		|#ifdef BUS_FIO_WRITE
		|	BUS_FIO_WRITE(out);
		|#endif
		|	uint8_t fpar = odd_parity64(out);
		|	if (PIN_PDIAG=>)
		|		fpar ^= 0xff;
		|	BUS_FIP_WRITE(fpar);
		|#endif
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XFIUROT", PartModel("XFIUROT", XFIUROTV))
    part_lib.add_part("XFIUROV", PartModel("XFIUROV", XFIUROTV))
