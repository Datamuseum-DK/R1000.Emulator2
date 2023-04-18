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
   One board in the CPU
   ====================
'''

import os

from srcfile import Makefile
from scmod import SystemCModule

class Board(SystemCModule):

    ''' One board in the CPU '''

    def __init__(self, cpu, name):
        name = name.lower()
        self.cpu = cpu

        self.dstdir = os.path.join(cpu.workdir, name.capitalize())
        os.makedirs(self.dstdir, exist_ok=True)

        self.makefile = Makefile(self.dstdir + "/Makefile.inc")

        super().__init__(self.sc_path(name), self.makefile)
        self.sc_fixup(self)
        self.add_ctor_arg("struct planes", "planes", is_ptr=True)
        self.scm_cname_pfx = self.scm_lname + "->"

    def add_sheet(self, sheet_name):
        sheet = SystemCModule(
            self.sc_path(sheet_name),
            self.makefile,
        )
        self.sc_fixup(sheet)
        sheet.add_ctor_arg("struct planes", "planes", is_ptr=True)
        sheet.add_ctor_arg("struct «bbb»", "«bbb»", srcname="this", is_ptr=True)
        sheet.include(self.cpu.plane.sf_hh)
        sheet.include(self.sf_hh)
        self.add_child(sheet)
        sheet.cpu = self.cpu			# XXX: for parts factories

    def sc_path(self, basename):
        ''' Source path of a SCM on this board '''
        return os.path.join(self.dstdir + "/" + basename)

    def sc_fixup(self, scm):
        ''' Add board substitutions '''
        scm.add_subst("«bbb»", self.scm_lname)
        scm.add_subst("«BBB»", self.scm_uname)

    def produce(self):
        ''' ... '''
        os.makedirs(self.dstdir, exist_ok=True)

        super().produce()
        self.makefile.commit()
