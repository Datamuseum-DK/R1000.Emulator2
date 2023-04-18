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
   F138 1-of-8 decoder/demultiplexer
   =================================

   Ref: Philips IC15 1991 Feb 14
'''


from part import PartModel, PartFactory

class F138(PartFactory):

    ''' F138 1-of-8 decoder/demultiplexer '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr, ena;
		|
		|	BUS_S_READ(adr);
		|	BUS_D_READ(ena);
		|	if (ena != 4)
		|		adr |= 8;
		|	TRACE(
		|	    << " s "
		|	    << BUS_S_TRACE()
		|	    << " e "
		|	    << BUS_D_TRACE()
		|	    << " | "
		|	    << std::hex << adr
		|	);
		|''')
        for n in range(7, -1, -1):
            if "Y%d_" % n in self.comp.nodes:
                file.fmt('	PIN_Y%d_<=(adr != %d);\n' % (n, n))

class F154(PartFactory):

    ''' F138 1-of-8 decoder/demultiplexer '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	unsigned adr;
		|
		|	BUS_S_READ(adr);
		|	if (PIN_E1=> || PIN_E2=>)
		|		adr |= 16;
		|	TRACE(
		|	    << " s "
		|	    << BUS_S_TRACE()
		|	    << " e1 "
		|	    << PIN_E1?
		|	    << " e2 "
		|	    << PIN_E2?
		|	    << " | "
		|	    << std::hex << adr
		|	);
		|''')
        for n in range(15, -1, -1):
            if "Y%d_" % n in self.comp.nodes:
                file.fmt('	PIN_Y%d_<=(adr != %d);\n' % (n, n))

class ModelF138(PartModel):
    ''' Eliminate unused outputs '''

    def assign(self, comp, part_lib):
        if False:
            # Not obvious if this will be faster
            for node in list(comp.nodes.values()):
                if node.pin.name[0] == "Y" and len(node.net) == 1:
                    print("F138", len(node.net), node)
                    node.remove()
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("F138", ModelF138("F138", F138))
    part_lib.add_part("F154", ModelF138("F154", F154))
