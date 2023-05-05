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
   Plot time-lines from trace records
   ==================================
'''

import sys

MAXVAR = 10

PERIOD = 200
STEP = 5
BUCKETS = (PERIOD // STEP)

def scale():
    h0 = []
    h1 = []
    h2 = []
    for i in range(0, 200, 5):
        j = "%03d" % i
        h0.append(j[0])
        h1.append(j[1])
        h2.append(j[2])
    yield " ".join(h0)
    yield " ".join(h1)
    yield " ".join(h2)

class State():
    def __init__(self):
        self.zseen = False
        self.xseen = False
        self.vals = set()

    def __repr__(self):
        return " ".join((
            "<ST",
            str(self.zseen),
            str(self.xseen),
            *sorted(self.vals),
            ">"
	))

    def __eq__(self, other):
        return self.zseen == other.zseen and self.xseen == other.xseen and self.vals == other.vals

    def add_val(self, val):
        self.zseen |= 'Z' in val
        self.xseen |= 'X' in val
        if len(self.vals) < MAXVAR:
            self.vals.add(val)

    def render(self):
        if len(self.vals) == 1 and '1' in self.vals:
            return ('▬▬', '▬▬')
        if len(self.vals) == 1 and '0' in self.vals:
            return ('──', '──')
        if len(self.vals) == 1 and 'Z' in self.vals:
            return ('ZZ', 'ZZ')
        if self.xseen:
            return ('xx', 'xx')
        if self.zseen:
            return ('zz', 'zz')
        return ('╳░', '░░')

class Field():
    def __init__(self):
        self.when = {}
        self.brutto = None

    def chew(self, time, val):
        state = self.when.get(time)
        if not state:
            state = State()
            self.when[time] = state
        state.add_val(val)

    def cleanup(self):
        ''' Collaps identical sequential states '''
        brutto = list(sorted(self.when.items()))
        n = 0
        while n + 1 < len(brutto):
            if brutto[n][1] == brutto[n+1][1]:
                brutto.pop(n + 1)
            else:
                n += 1
        self.brutto = brutto

    def report(self, file):
        self.cleanup()

        vals = set()
        variance = 0
        for when, what in self.brutto:
            variance = max(variance, len(what.vals))
            vals |= what.vals
        first = self.brutto[0][0]
        last = self.brutto[-1][0]

        if len(vals) == 1:
            # constant, probably label
            file.write("  = " + list(vals)[0] + "\n")
            return

        txt = ['??'] * BUCKETS
        for n, i in enumerate(self.brutto):
            when, what = i
            if n + 1 < len(self.brutto):
                end = self.brutto[n+1][0]
            else:
                end = PERIOD + self.brutto[0][0]
            first, second = what.render()
            for j in range(when // STEP, end // STEP):
                txt[j % BUCKETS] = first
                first = second
        file.write("\t\t" + "".join(txt) + "\n")
        return

        if variance == 1 and len(vals) == 2 and '0' in vals and '1' in vals:
            # binary
            pwhen = 0
            pwhat = ""
            txt = ""
            for when, what in self.brutto:
                for i in range(pwhen, when, 5):
                    txt += pwhat
                pwhen = when
                if '0' in what.vals:
                    pwhat = "──"
                else:
                    pwhat = "▬▬"
            for i in range(pwhen, 200, 5):
                txt += pwhat
            for i in range(0, first, 5):
                txt = pwhat + txt
            file.write("\t\t" + txt + "\n")
            return

        maxwid = max(len(x) for x in vals)

        txt = ['░░'] * 40
        for when, what in self.brutto:
            if len(what.vals) == 1:
                what = list(what.vals)[0]
                if what == '1':
                    txt[when // 5] = "▬▬"
                elif what == '0':
                    txt[when // 5] = "──"
                elif len(what) == 1:
                    txt[when // 5] = what + "┄"
                else:
                    txt[when // 5] = "╟─"
            elif what.xseen:
                txt[when // 5] = '╳▉'
            elif what.zseen:
                txt[when // 5] = '╳▒'
            else:
                txt[when // 5] = '╳░'
        file.write("\t\t" + "".join(txt) + "\n")

class Component():
    def __init__(self, ident):
        self.ident = ident
        self.flds = []

    def __lt__(self, other):
        return self.ident < other.ident

    def chew(self, line):
        for n, fld in enumerate(line[4:]):
            if n >= len(self.flds):
                 self.flds.append(Field())
            self.flds[n].chew(line[2], fld)

    def report(self, file):
        file.write("\n" + self.ident + "\n")
        file.write('=' * len(self.ident) + "\n")
        for i in scale():
            file.write("\t\t" + i + "\n")
        
        for fld in self.flds:
            fld.report(file)
 


class Main():
    def __init__(self, filename):
        self.filename = filename
        self.comps = {}
        self.ingest()
        self.report()

    def ingest(self):
        n = 0
        for i in open(self.filename):
            n += 1
            if not n % 100000:
                 print(n, len(self.comps))
            if " Exec " in i:
                continue
            if " SC " not in i:
                continue
            if "PROC" in i:
                continue
            if "FIRMWARE" in i:
                continue
            j = i.split()
            if len(j) < 2 or j[1] != "SC":
                continue
            key = j[3] + "::%d" % len(j)
            comp = self.comps.get(key)
            if not comp:
                comp = Component(key)
                self.comps[key] = comp
            j[0] = int(j[2])
            if j[0] < 100000:
                continue
            j[1] = j[0] // 200
            j[2] = j[0] % 200
            comp.chew(j)

    def report(self, file=None):
        if not file:
            file = sys.stdout
        for comp in sorted(self.comps.values()):
            comp.report(file)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        Main("_r1000.trace")    
    else:
        for fn in sys.argv[1:]:
            Main(fn)
