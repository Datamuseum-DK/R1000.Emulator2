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
   Multiplexers to replace HiZ busses
   ==================================
'''

from part import PartModel, PartFactory

class XBusMux(PartFactory):

    ''' HiZ Bus Multiplexer '''

    autopin = True

    def __init__(self, ident, length, width):
        super().__init__(ident)
        self.length = length
        self.width = width

    def private(self):
        ''' private variables '''
        j = []
        for i in range(self.width):
            j.append("PIN_OE%c" % (65 + i))
            yield from self.event_or(
                "%c_event" % (65 + i),
                "BUS_I%c" % (65 + i),
                *j
            )
        yield from self.event_or(
            "no_event",
            *j
        )

    def doit(self, file):
        ''' The meat of the doit() function '''

        pfx = ""
        for i in range(self.width):
            file.fmt('\t' + pfx + 'if (!PIN_OE%c=>) {\n' % (i + 65))
            pfx = "} else "
            file.fmt('\t\tBUS_I%c_READ(output.q);\n' % (i + 65))
            file.fmt('\t\tidle_next = &%c_event;\n' % (i + 65))

        file.fmt('''
		|	} else {
		|		output.q = BUS_Q_MASK;
		|		next_trigger(no_event);
		|	}
		|''')


class ModelXBusMux(PartModel):
    ''' HiZ bus mux '''

    def __init__(self, length, width):
        super().__init__("XBUSMUX%dX%d" % (length, width))
        self.length = length
        self.width = width

    def configure(self, comp, part_lib):
        sig = self.make_signature(comp)
        ident = self.name + "_" + sig
        if ident not in part_lib:
            part_lib.add_part(ident, XBusMux(ident, self.length, self.width))
        comp.part = part_lib[ident]

def register(part_lib):
    ''' Register component model '''

    for i in range(65):
        for j in range(16):
            part_lib.add_part("XBUSMUX%dX%d" % (i, j), ModelXBusMux(i, j))
