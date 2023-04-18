#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
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
   REGISTER FILES
   ==============

'''

from part import PartModel, PartFactory

class XRFTA(PartFactory):

    ''' TYP RF A '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_AW_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_WE.pos()"
        yield "PIN_RD.pos()"
        yield "BUS_A_SENSITIVE()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0, a, a2;
		|	uint64_t data = 0;
		|
		|	if (PIN_WE.posedge() && !PIN_CS=>) {
		|		BUS_D_READ(data);
		|		BUS_AW_READ(adr);
		|		state->ram[adr] = data;
		|	} else if (PIN_WE.posedge()) {
		|		printf("TYP.A supressed write\\n");
		|	}
		|	adr = 0;
		|	BUS_A_READ(a);
		|	if (a == 0x28) {
		|		BUS_CNT_READ(data);
		|		data |= (BUS_Q_MASK & ~0x3ffULL);
		|	} else if (a == 0x29) {
		|		data = BUS_Q_MASK;
		|	} else if (a == 0x2a) {
		|		data = BUS_Q_MASK;
		|	} else if (a == 0x2b) {
		|		data = BUS_Q_MASK;
		|	} else if (a == 0x2c) {
		|		BUS_CNT_READ(adr);
		|		data = state->ram[adr];
		|	} else {
		|		if (!(a & 0x20)) {
		|			BUS_FRM_READ(a2);
		|			adr |= a2 << 5;
		|		}
		|		adr |= (a & 0x10);
		|		if ((a & 0x30) == 0x20) {
		|			BUS_TOS_READ(a2);
		|			adr |= a2;
		|		} else {
		|			adr |= (a & 0xf);
		|		}
		|		data = state->ram[adr];
		|	}
		|	BUS_Q_WRITE(data);
		|
		|	TRACE(
		|	   << " we " << PIN_WE?
		|	   << " cs " << PIN_CS?
		|	   << " aw " << BUS_AW_TRACE()
		|	   << " d " << BUS_D_TRACE()
		|	   << " rd " << PIN_RD?
		|	   << " a " << BUS_A_TRACE()
		|	   << " cnt " << BUS_CNT_TRACE()
		|	   << " frm " << BUS_AW_TRACE()
		|	   << " tos " << BUS_TOS_TRACE()
		|	   << " q " << BUS_Q_TRACE()
		|	);
		|''')


class XRFTB(PartFactory):

    ''' TYP RF B '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_AW_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_WE.pos()"
        yield "PIN_RD.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0, b = 0, a2;
		|	uint64_t data = 0;
		|	const char *what = "?";
		|
		|	if (PIN_WE.posedge() && !PIN_CS=>) {
		|		BUS_D_READ(data);
		|		BUS_AW_READ(adr);
		|		state->ram[adr] = data;
		|		what = "W";
		|	} else if (PIN_WE.posedge()) {
		|		printf("TYP.B supressed write\\n");
		|	} else {
		|		BUS_B_READ(b);
		|		if (b == 0x29 && PIN_TRCV=>) {
		|			BUS_TYP_READ(data);
		|			data ^= BUS_TYP_MASK;
		|			what = "T";
		|		} else if (b == 0x2c) {
		|			BUS_CNT_READ(adr);
		|			data = state->ram[adr];
		|			what = "C";
		|		} else {
		|			if (!(b & 0x20)) {
		|				BUS_FRM_READ(adr);
		|				adr <<= 5;
		|			}
		|			adr |= b & 0x10;
		|			if ((b & 0x30) != 0x20) {
		|				adr |= (b & 0xf);
		|			} else if ((b & 0x3c) == 0x28) {
		|				BUS_CSA_READ(a2);
		|				adr |= a2;
		|			} else {
		|				BUS_TOS_READ(a2);
		|				adr |= a2;
		|			}
		|			data = state->ram[adr];
		|			what = "R";
		|		}
		|		BUS_Q_WRITE(data);
		|	}
		|
		|	TRACE(
		|	    << what
		|	    << " cs " << PIN_CS
		|	    << " we^ " << PIN_WE.posedge()
		|	    << " aw " << BUS_AW_TRACE()
		|	    << " rd^ " << PIN_RD.posedge()
		|	    << " b " << BUS_B_TRACE()
		|	    << " frm " << BUS_FRM_TRACE()
		|	    << " csa " << BUS_CSA_TRACE()
		|	    << " tos " << BUS_TOS_TRACE()
		|	    << " cnt " << BUS_CNT_TRACE()
		|	    << " trcv " << PIN_TRCV
		|	    << " typ " << BUS_TYP_TRACE()
		|	    << " q " << BUS_Q_TRACE()
		|	);
		|''')

class XRFVA(PartFactory):

    ''' VAL RF A '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_AW_WIDTH];
		|	uint64_t last;
		|	const char *what;
		|''')

    def sensitive(self):
        yield "PIN_CS"
        yield "PIN_WE"
        yield "PIN_RD"
        yield "BUS_A_SENSITIVE()"

    def extra(self, file):
        super().extra(file)
        file.fmt('''
		|static const char *READING = "r";
		|static const char *WRITING = "w";
		|static const char *ZZZING = "z";
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0, a, a2;
		|	uint64_t data = 0;
		|
		|	BUS_A_READ(a);
		|	if (PIN_CS=>) {
		|		if (state->what == READING) {
		|		} else if (state->what == WRITING) {
		|			BUS_AW_READ(adr);
		|			BUS_D_READ(data);
		|			state->ram[adr] = data;
		|		}
		|		next_trigger(PIN_CS.negedge_event());
		|		state->what = ZZZING;
		|	} else if (!PIN_WE=>) {
		|		BUS_D_READ(data);
		|		BUS_AW_READ(adr);
		|		state->ram[adr] = data;
		|		state->what = WRITING;
		|	} else {
		|		if (state->what == WRITING) {
		|			BUS_AW_READ(adr);
		|			BUS_D_READ(data);
		|			state->ram[adr] = data;
		|		}
		|		if (a == 0x2c) {
		|			BUS_CNT_READ(adr);
		|			data = state->ram[adr];
		|		} else {
		|			adr = 0;
		|			if (!(a & 0x20)) {
		|				BUS_FRM_READ(adr);
		|				adr <<= 5;
		|			}
		|			adr |= (a & 0x10);
		|			if ((a & 0x30) == 0x20) {
		|				BUS_TOS_READ(a2);
		|				adr |= a2;
		|			} else {
		|				adr |= (a & 0x0f);
		|			}
		|			data = state->ram[adr];
		|		}
		|		if (state->what != READING || data != state->last) {
		|			BUS_Q_WRITE(data);
		|			state->last = data;
		|		}
		|		state->what = READING;
		|	}
		|	BUS_A_READ(a);
		|	if (a == 0x28) {
		|		PIN_AOE<=(true);
		|		PIN_LOOPOE<=(false);
		|		PIN_MULTOE<=(true);
		|		PIN_ZEROOE<=(true);
		|	} else if (a == 0x29) {
		|		PIN_AOE<=(true);
		|		PIN_LOOPOE<=(true);
		|		PIN_MULTOE<=(false);
		|		PIN_ZEROOE<=(true);
		|	} else if (a == 0x2a) {
		|		PIN_AOE<=(true);
		|		PIN_LOOPOE<=(true);
		|		PIN_MULTOE<=(true);
		|		PIN_ZEROOE<=(false);
		|	} else if (a == 0x2b) {
		|		PIN_AOE<=(true);
		|		PIN_LOOPOE<=(true);
		|		PIN_MULTOE<=(true);
		|		PIN_ZEROOE<=(true);
		|	} else {
		|		PIN_AOE<=(false);
		|		PIN_LOOPOE<=(true);
		|		PIN_MULTOE<=(true);
		|		PIN_ZEROOE<=(true);
		|	}
		|	
		|
		|	TRACE(
		|	    << state->what
		|	    << " cs " << PIN_CS?
		|	    << " we " << PIN_WE?
		|	    << " aw " << BUS_AW_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	    << " rd " << PIN_RD?
		|	    << " a " << BUS_A_TRACE()
		|	    << " cnt " << BUS_CNT_TRACE()
		|	    << " frm " << BUS_FRM_TRACE()
		|	    << " tos " << BUS_TOS_TRACE()
		|	    << " q " << BUS_Q_TRACE()
		|	);
		|''')



class XRFVB(PartFactory):

    ''' VAL RF B '''

    def state(self, file):
        file.fmt('''
		|	uint64_t ram[1<<BUS_AW_WIDTH];
		|''')

    def sensitive(self):
        yield "PIN_WE.pos()"
        yield "PIN_RD.pos()"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr = 0, a2;
		|	unsigned b = 0;
		|	uint64_t data = 0, val;
		|	const char *what = "?";
		|
		|	if (!PIN_CS=>) {
		|		BUS_B_READ(b);	// NB: inverted
		|
		|		if (b < 0x20) {
		|			BUS_FRM_READ(adr);
		|			adr <<= 5;
		|		}
		|
		|		adr |= b & 0x10;
		|
		|		what = "r";
		|		if ((b & 0x30) != 0x20) {
		|			adr |= b & 0x0f;
		|		} else if ((b & 0x2c) == 0x28) {
		|			BUS_CSA_READ(a2);
		|			adr |= a2;
		|		} else if (b == 0x2c) {
		|			BUS_CNT_READ(adr);
		|			what = "c";
		|		} else {
		|			BUS_TOS_READ(a2);
		|			adr |= a2;
		|		}
		|
		|		data = state->ram[adr];
		|		if (b == 0x29 && (PIN_LHIT=> || PIN_VALDRV)) {
		|			BUS_VAL_READ(data);
		|			data ^= BUS_VAL_MASK;
		|			what = "v";
		|		} else if (!PIN_GETLIT=>) {
		|			BUS_VAL_READ(val);
		|			val ^= BUS_VAL_MASK;
		|			data &= 0xffffffffffffff00ULL;
		|			data |= val & 0xffULL;
		|			what = "l";
		|		}
		|		BUS_Q_WRITE(data);
		|	}
		|
		|	if (PIN_WE.posedge() && !PIN_CS=>) {
		|		BUS_D_READ(data);
		|		BUS_AW_READ(adr);
		|		state->ram[adr] = data;
		|		what = "w";
		|	} else if (PIN_WE.posedge()) {
		|		printf("VAL supressed write\\n");
		|	}
		|
		|	TRACE(
		|	    << what
		|	    << " we^ " << PIN_WE.posedge()
		|	    << " cs " << PIN_CS?
		|	    << " aw " << BUS_AW_TRACE()
		|	    << " d " << BUS_D_TRACE()
		|	    << " rd^ " << PIN_RD.posedge()
		|	    << " b " << BUS_B_TRACE()
		|	    << " cnt " << BUS_CNT_TRACE()
		|	    << " frm " << BUS_FRM_TRACE()
		|	    << " csa " << BUS_CSA_TRACE()
		|	    << " tos " << BUS_TOS_TRACE()
		|	    << " getlit " << PIN_GETLIT?
		|	    << " lhit " << PIN_LHIT?
		|	    << " valdrv " << PIN_VALDRV?
		|	    << " val " << BUS_VAL_TRACE()
		|	    << " q " << BUS_Q_TRACE()
		|	);
		|''')


def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XRFTA", PartModel("XRFTA", XRFTA))
    part_lib.add_part("XRFTB", PartModel("XRFTB", XRFTB))
    part_lib.add_part("XRFVA", PartModel("XRFVA", XRFVA))
    part_lib.add_part("XRFVB", PartModel("XRFVB", XRFVB))
