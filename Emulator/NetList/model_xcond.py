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
   SEQ Condition Select
   ====================

'''

from part import PartModel, PartFactory

class XCOND(PartFactory):
    ''' SEQ Condition Select '''

    def state(self, file):
        file.fmt('''
		|	uint8_t elprom[512];
		|	unsigned condsel;
		|	bool is_e_ml;
		|	bool cond;
		|	bool q3cond;
		|	bool llcond;
		|''')

    def private(self):
        ''' private variables '''
        for i in range(16):
            if i == 4:
                yield from self.event_or(
                   "event_%x" % i,
                   "PIN_CXC.default_event()",
                   "PIN_CXF.default_event()",
                   "PIN_Q4.default_event()",
                   "BUS_ICOND",
                )
            else:
                yield from self.event_or(
                   "event_%x" % i,
                   "PIN_CX%X.default_event()" % i,
                   "PIN_Q4.default_event()",
                   "BUS_ICOND",
                )

    def init(self, file):
        file.fmt('''
		|	load_programmable(this->name(),
		|	    state->elprom, sizeof state->elprom,
		|	    "PA042-02");
		|''')
        super().init(file)

    def sensitive(self):
        yield "BUS_ICOND_SENSITIVE()"
        yield "PIN_Q4"

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	if (state->ctx.job) {
		|		state->ctx.job = 0;
		|		BUS_OCOND_WRITE(state->condsel ^ BUS_OCOND_MASK);
		|		PIN_E_ML<=(state->is_e_ml);
		|		PIN_CNDP<=(state->cond);
		|		PIN_CNDN<=(!state->cond);
		|		PIN_CQ3P<=(state->q3cond);
		|		PIN_CQ3N<=(!state->q3cond);
		|		PIN_CLLP<=(state->llcond);
		|		PIN_CLLN<=(!state->llcond);
		|	}
		|
		|	unsigned condsel;
		|	BUS_ICOND_READ(condsel);
		|
		|	uint8_t pa042 = state->elprom[condsel << 2];
		|	bool is_e_ml = (pa042 >> 7) & 1;
		|
		|	bool cond;
		|	sc_event_or_list *next = NULL;
		|	switch(state->condsel >> 3) {
		|''')

        for pin in range(16):
            if pin == 4:
                file.fmt('''
		|	case 0x%x: cond = !(PIN_CXC=> && PIN_CXF=>); next = &event_%x; break;
		|''' % (pin, pin))
            else:
                file.fmt('''
		|	case 0x%x: cond = PIN_CX%X=>; next = &event_%x; break;
		|''' % (pin, pin, pin))

        file.fmt('''
		|	}
		|
		|	bool q3cond = state->q3cond;
		|	bool llcond = state->llcond;
		|	if (!is_e_ml && PIN_Q4.negedge()) {
		|		q3cond = cond;
		|	}
		|	if (is_e_ml && !PIN_SCKE=> && PIN_Q4.posedge()) {
		|		llcond = cond;
		|	}
		|
		|	if (condsel != state->condsel ||
		|	    is_e_ml != state->is_e_ml ||
		|	    cond != state->cond ||
		|	    q3cond != state->q3cond ||
		|	    llcond != state->llcond) {
		|		state->condsel = condsel;
		|		state->is_e_ml = is_e_ml;
		|		state->cond = cond;
		|		state->q3cond = q3cond;
		|		state->llcond = llcond;
		|		state->ctx.job = 1;
		|		next_trigger(5, SC_NS);
		|		TRACE (
		|		    << std::hex
		|		    << " condsel " << condsel
		|		    << " e_ml " << is_e_ml
		|		    << " cond " << cond
		|		    << " q3cond " << q3cond
		|		    << " llcond " << llcond
		|		);
		|	} else {
		|		next_trigger(*next);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XCOND", PartModel("XCOND", XCOND))
