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

import sys
import os
import glob
import importlib

sys.path.append("./PySymbols")

import chip

class Symbol():
    ''' A single symbol '''

    def __lt__(self, other):
        return self.name < other.name

class PySymbol(Symbol):
    ''' A Python KiCad symbol '''

    def __init__(self, filename, sym):
        self.filename = filename
        self.sym = sym
        self.name = sym.symbol_name

    def __iter__(self):
        yield from self.sym.kicad_symbol()

def main():

    sym_list = []

    for filename in glob.glob("PySymbols/*.py"):
        bn = os.path.basename(filename)[:-3]
        if bn == "chip":
            continue
        mod = importlib.import_module(bn)
        for sym in mod.register():
            sym_list.append(PySymbol(bn, sym))

    with open("R1000.kicad_sym", "w") as file:
        file.write('(kicad_symbol_lib (version 20211014) (generator PHK115)\n')
    
        for sym in sorted(sym_list):
            for line in sym:
                file.write(line.rstrip() + "\n")
    
        file.write(')\n')

if __name__ == "__main__":
    main()
