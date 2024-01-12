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
   VAL UIR.A decode
   ================

'''

from part import PartModel, PartFactory

class XVADEC(PartFactory):
    ''' VAL UIR.A decode '''

    autopin = True

    def sensitive(self):
        yield "PIN_Q1"
        yield "PIN_AODON"

    def private(self):
        ''' private variables '''
        yield from self.event_or(
            "idle_event",
            "PIN_AODON",
            "PIN_Q1.posedge_event()",
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        file.fmt('''
		|	unsigned a;
		|	BUS_A_READ(a);
		|	output.a = true;
		|	output.loop = true;
		|	output.prod = true;
		|	output.zero = true;
		|	if (!PIN_AODON=>) {
		|		output.a = false;
		|	} else if (!PIN_Q1=>) {
		|		output.a = false;
		|	} else if (a == 0x28) {
		|		output.loop = false;
		|	} else if (a == 0x29) {
		|		output.prod = false;
		|	} else if (a == 0x2a) {
		|		output.zero = false;
		|	} else if (a == 0x2b) {
		|	} else {
		|		output.a = false;
		|	}
		|''')
    def doit_idle(self, file):

        file.fmt('''
		|	if (!output.a) {
		|		next_trigger(idle_event);
		|	}
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XVADEC", PartModel("XVADEC", XVADEC))
