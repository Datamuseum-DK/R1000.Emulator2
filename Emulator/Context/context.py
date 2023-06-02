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
   Pull activation counts out of shared memory
   -------------------------------------------

   Can be used as a class to build tools or stand alone.

   Standalone usage is:

      python3 Context/context.py <name of _r1000.ctx file> [delta-t]

   If delta-t is specified, only activations during that many seconds
   are reported, otherwise activations from start of simulation is reported.

   The three numeric columns are:

       * Average activations per micro-cycle
       * Activations
       * Fraction of total activations

'''

import sys
import time

import re
import struct

class Context():

    ''' Pull context records out of shared memory '''

    def __init__(self, file=None):
        self.ident = None
        self.activations = None
        self.length = None
        self.body = None
        if file:
            self.from_file(file)

    def __lt__(self, other):
        return self.ident < other.ident

    def from_file(self, file):
        ''' return the next activation record '''
        buf = file.read(128)
        if len(buf) != 128:
            raise EOFError
        hdr = struct.unpack("<LLQLL104s", buf)
        if not hdr[3]:
            raise EOFError
        if hdr[3] != 0x6e706c8e:
            raise ValueError
        self.length = hdr[4]
        self.activations = hdr[2]
        self.ident = hdr[5].rstrip(b'\x00').decode("utf-8")
        self.body = file.read(self.length - 128)
        return self

    def __repr__(self):
        return self.ident

def contexts(filename=None, regex=None):
    ''' Filter activation records by regexp '''
    if filename is None:
        filename = sys.argv[1]
    if regex is not None:
        regex = re.compile(regex)
    with open(filename, "rb") as file:
        while True:
            try:
                ctx = Context(file)
            except EOFError:
                return
            if not regex or regex.search(ctx.ident):
                yield ctx

def main():
    ''' Default main function '''
    nact = 0
    lines = []
    summ = {}
    ucycles = None
    filename = sys.argv[1]
    snapshot = {}

    if len(sys.argv) > 2:
        duration = int(sys.argv[2])
        for ctx in contexts(filename=filename):
            snapshot[ctx.ident] = ctx.activations
        time.sleep(duration)

    for ctx in contexts(filename=filename):
        i = ctx.activations
        delta = snapshot.get(ctx.ident)
        if delta:
            i -= delta
        if ucycles is None and "CLKGEN" in ctx.ident:
            ucycles = i / 14
        nact += i
        lines.append((i, str(ctx)))
        j = "page " + ctx.ident.split(".")[1]
        summ[j] = summ.get(j, 0) + i
        j = "board " + ctx.ident.split(".")[1].split('_')[0]
        summ[j] = summ.get(j, 0) + i


    for i, j in summ.items():
        lines.append((j, i))

    for i, ctx in sorted(lines):
        if i:
            print(
                "%8.3f" % (i / ucycles),
                "%12d" % i,
                "%7.4f" % (i / nact),
                ctx
            )
    print(
        "%8.3f" % (nact / ucycles),
        "%12d" % nact,
        "%7.4f" % (nact / nact),
        "Total"
    )
    print("UCYCLES %.1f" % ucycles)

if __name__ == "__main__":
    main()
