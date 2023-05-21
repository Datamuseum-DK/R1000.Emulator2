#!/bin/env python3
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
   Python classes for experiment files
   ===================================
'''

class Param():
    ''' R1K experiment parameter '''

    def __init__(self, line):
        self.line = line
        assert line[0] == "P"
        self.loc = int(line[1:3], 16)
        self.dir = line[3]
        self.typ = line[4]
        self.len = int(line[5])
        self.name = line[6:].strip()

    def __repr__(self):
        return self.name + " (%02x %s %s %d)" % (self.loc, self.dir, self.typ, self.len)

class Experiment():
    ''' R1K DFS experiment file '''

    def __init__(self, dirent):
        self.name = dirent.name
        self.lines = dirent.read_text().splitlines()
        for line in self.lines:
            assert len(line) in (0, 2) or line[0] == 'P', line
        self.params = {}
        for param in (Param(line) for line in self.lines if line[:1] == "P"):
            self.params[param.name] = param
        self.octets = bytearray(int(line,16) for line in self.lines if len(line) == 2)

    def __str__(self):
        return '<Exp ' + self.name + '>'

    def __eq__(self, other):
        if self.octets != other.octets:
            return False
        if len(self.params) != len(other.params):
            return False
        for i, j in self.params.items():
            if str(j) != str(other.params.get(i)):
                return False
        return True

def is_experiment(dirent):
    ''' Is this an experiment file '''
    suffix = dirent.name.split(".")[-1]
    return suffix in ("VAL", "TYP", "SEQ", "FIU", "IOC", "MEM", "M32")
