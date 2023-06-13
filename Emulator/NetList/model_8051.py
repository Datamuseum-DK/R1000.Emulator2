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
   I8051 CPU
   ===========

'''

from part import PartModel, PartFactory

class I8051(PartFactory):

    ''' I8051 CPU'''

    def sensitive(self):
        yield "PIN_RST"
        yield "PIN_XTAL2.pos()"

    def extra(self, file):
        super().extra(file)
        self.scm.sf_cc.include("Diag/diagproc.h")

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tstruct diagproc_context dctx;\n")
        file.write("\tstruct scm_8051_state *state;\n")
        file.write("\tstruct diagproc *diagproc;\n")
        file.write("\tunsigned cycle;\n")

    def init(self, file):
        ''' Extra initialization '''

        file.fmt('''
		|	state->diagproc =
		|	    DiagProcCreate(this->name(), arg, &state->ctx.do_trace);
		|	assert(state->diagproc != NULL);
		|	state->cycle = 0;
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        # The meat of the doit() function lives in a separate file so
        # that fidling with it does not require a rerun of the python code.

        self.scm.sf_cc.include("Diag/diag_sc_8051.cc")

class Model8051(PartModel):
    ''' i8051'''

    def __init__(self, *args):
        super().__init__(*args)

    def assign(self, comp, part_lib):
        for node in comp:
            if node.pin.name in (
                "XTAL1",
                "PSENnot",
                # "TXD",
                "T0",
            ):
                node.remove()

        for node in comp:
            if node.pin.name in (
                "TXD",
                "RDnot",
                "INT0not",
                "INT1not",
            ):
                node.pin.set_role("bidirectional")
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("8051", Model8051("8051", I8051))
