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
   Turn kicad netlist files into SystemC source code
   =================================================
'''

import sys
import os
import glob
import importlib

from srcfile import SrcFile, Makefile
from scmod import SystemCModule
from part import NoPart
from kicad_netlist import KiCadNetList

import planes

from pass_assign_part import PassAssignPart
from pass_net_config import PassNetConfig
from pass_part_config import PassPartConfig

MYSELF = os.path.basename(__file__)

class PartLib():
    ''' Library of parts from which components can be instantiated '''
    def __init__(self):
        self.parts = {}

    def __getitem__(self, key):
        return self.parts[key]

    def __contains__(self, key):
        return key in self.parts

    def __iter__(self):
        yield from sorted(self.parts.items())

    def add_part(self, name, part):
        if name not in self.parts:
            self.parts[name] = part

class R1000Cpu():

    ''' A R1000 CPU '''

    def __init__(self, workdir, branch, netlists):
        ''' ... '''
        self.workdir = workdir
        self.branch = branch
        self.netlists = netlists
        self.part_lib = PartLib()
        self.boards = []
        self.chassis_makefile = None
        self.nets = {}
        self.plane = None
        self.z_codes = []

        self.cdir = os.path.join(workdir, "Chassis")
        self.tstamp = os.path.join(self.cdir, "_timestamp")

        os.makedirs(self.cdir, exist_ok=True)

        if self.already_current():
            print("Already up to date")
            return

        bdir = os.path.dirname(__file__)
        for i in sorted(glob.glob(bdir + "/model_*py")):
            i = os.path.basename(i)[:-3]
            mod = importlib.import_module(i)
            mod.register(self.part_lib)

        self.add_part("GB", NoPart())
        self.add_part("GF", NoPart())
        self.add_part("Pull_Up", NoPart())
        self.add_part("Pull_Down", NoPart())

        self.chassis_makefile = Makefile(os.path.join(self.cdir, "Makefile.inc"))

        self.plane = planes.Planes(self)
        self.do_build()
        # exit(2)
        open(self.tstamp, "w").write("\n")
        with open("_part_ref", "w") as file:
            for i, j in self.part_lib:
                file.write(str(i) + " " + str(j) + " " + str(j.usecount) + " " + str(j.uses) + "\n")
          

    def add_board(self, board):
        ''' Add a board '''
        self.boards.append(board)

    def add_part(self, name, part):
        ''' Add a part to our catalog, if not already occupied '''
        self.part_lib.add_part(name, part)

    def add_z_code(self, comp, zcode):
        self.z_codes.append((zcode, comp))

    def sc_mod(self, basename):
        ''' Create SCM for parts '''
        return SystemCModule(os.path.join(self.cdir, basename), self.chassis_makefile)

    def already_current(self):
        ''' Check if generated files are newer than netlists '''
        try:
            t_old = os.stat(self.tstamp).st_mtime
        except FileNotFoundError:
            return False

        try:
            if os.stat("Makefile.local").st_mtime > t_old:
                print("Makefile.local", "triggers build")
                return False
        except FileNotFoundError:
            pass

        if os.stat(__file__).st_mtime > t_old:
            print(__file__, "triggers build")
            return False

        for filename in self.netlists:
            if os.stat(filename).st_mtime > t_old:
                print(filename, "triggers build")
                return False

        for fn in glob.glob("NetList/*.py"):
            if os.stat(fn).st_mtime > t_old:
                print(fn, "triggers build")
                return False

        return True

    def recurse(self, call_this, *args, **kwargs):
        ''' Recursively do something to all SystemCModules '''
        for board in self.boards:
            board.recurse(call_this, *args, **kwargs)

    def do_build(self):
        ''' ... '''

        for filename in self.netlists:
            print("Processing", filename)
            nlist = KiCadNetList(filename)
            nlist.build(self)

        # Establish canonical order
        self.boards.sort()

        self.plane.scm_cname_pfx = "planes->"

        self.plane.build_planes(self)

        PassAssignPart(self)

        PassNetConfig(self)

        PassPartConfig(self)

        self.plane.produce()

        for board in self.boards:
            board.produce()

        self.chassis_makefile.commit()

        self.emit_z_codes()

    def emit_z_codes(self):

        z_codes = SrcFile(self.cdir + "/z_codes.h")

        z_codes.write("\n#define Z_CODES(MACRO) \\\n")

        for z_code, comp in sorted(self.z_codes):
            z_codes.write('\tMACRO(' + z_code + ', "' + comp.ctx() + '") \\\n')

        z_codes.write('\n')

        for z_code, comp in sorted(self.z_codes):
            print(z_code, comp.ctx())
            z_codes.write('#define HAS_' + z_code.upper() + ' 1\n')
            z_codes.write('#define COMP_' + z_code.upper() + ' "%s"\n' % comp.ctx())

        z_codes.commit()

def main():
    ''' ... '''

    try:
        open("NetList/" + os.path.basename(__file__))
    except FileNotFoundError:
        sys.stderr.write("Must run %s from root of R1000.Emulator project\n" % MYSELF)
        sys.exit(2)

    if len(sys.argv) < 4:
        sys.stderr.write("Usage:\n\t%s <workdir> <branch> <KiCad netlist-file> …\n" % MYSELF)
        sys.exit(2)

    R1000Cpu(workdir = sys.argv[1], branch = sys.argv[2], netlists = sys.argv[3:])

if __name__ == "__main__":
    main()
