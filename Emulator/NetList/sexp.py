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
S-Expressions
'''

import sys

class SExp():
    ''' Painfully primitive s-exp handling '''
    def __init__(self, name, *vals):
        self.name = name
        self.quoted = False
        if len(vals) == 1 and vals[0] is None:
            self.members = None
        else:
            self.members = []
            for i in vals:
                self += i

    def __str__(self):
        if self.members is None:
            return self.name
        return "(" + self.name + " <%d>)" % len(self.members)

    def __iadd__(self, child):
        if isinstance(child, str):
            child = SExp(child, None)
        assert isinstance(child, SExp)
        self.members.append(child)
        return self

    def __isub__(self, child):
        self.members.remove(child)
        return self

    def __len__(self):
        if self.members is None:
            return 0
        return len(self.members)

    def __getitem__(self, idx):
        return self.members[idx]

    def pop(self, idx):
        ''' pop a member '''
        return self.members.pop(idx)

    def __iter__(self):
        yield from self.members

    def find(self, name):
        ''' iter members named ... '''
        names = name.split(".", 1)
        for i in self:
            if i.name == names[0]:
                if len(names) == 1:
                    yield i
                else:
                    yield from i.find(names[1])

    def find_first(self, name):
        ''' find the first member named ... '''
        for i in self.find(name):
            return i

    def parse(self, src, start=0):
        ''' Parse sexp string '''
        begin = start

        while src[begin] in " \t\n":
            begin += 1

        if src[begin] == '"':
            end = begin + 1
            while True:
                while src[end] not in '\\"':
                    end += 1
                if src[end] == '"':
                    end += 1
                    break
                assert src[end:end+2] in ('\\\\', '\\"', '\\n')
                end += 2
            self.name = src[begin + 1:end - 1]
            self.quoted = True
            self.members = None
            return end

        if src[begin] != '(':
            end = begin
            while src[end] not in " \t\n)":
                end += 1
            self.name = src[begin:end]
            self.members = None
            return end

        begin += 1
        end = begin
        while src[end] not in " \t\n)":
            end += 1
        self.name = src[begin:end]
        while end < len(src):
            while src[end] in " \t\n":
                end += 1
                if end == len(src):
                    return end + 1
            if src[end] == ')':
                break
            sexp = SExp(None)
            end = sexp.parse(src, end)
            self += sexp
        return end + 1

    def requote(self):
        ''' Reapply quotes if string '''
        if self.quoted:
            return '"' + self.name + '"'
        return self.name

    def serialize(self, indent="  "):
        ''' Serialize recursively '''

        if self.members is None:
            yield self.requote()
        elif len(self.members) == 0:
            yield '(' + self.name + ')'
        elif sum(len(x) for x in self.members):
            yield '(' + self.name
            for i in self.members:
                for j in i.serialize(indent):
                    yield indent + j
            yield ')'
        else:
            i = ' '.join(x.requote() for x in self.members)
            yield '(' + self.name + ' ' + i + ')'

def main():
    ''' Beautification pipe '''
    sexp = SExp(None)
    sexp.parse(sys.stdin.read())
    sys.stdout.write("\n".join(x for x in sexp.serialize()))

if __name__ == "__main__":
    main()
