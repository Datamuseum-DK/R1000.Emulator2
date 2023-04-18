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
   Various stuff
   =============
'''

def sortkey(word):
    '''
	Split input into runs of digits vs. non-digits and return
	a list with alternating strings and numbers ready for
        lexicograhic sorting:

            "/Page 2/IO.DO8" => ['/Page ', 2, '/IO.DO', 8]
            "/Page 21/IO.DO8" => ['/Page ', 21, '/IO.DO', 8]

    '''
    key = list([word[0]])
    for glyph in word[1:]:
        i = glyph.isdigit()
        j = key[-1][-1].isdigit()
        if i == j:
            key[-1] += glyph
        else:
            key.append(glyph)
    for i, j in enumerate(key):
        if j.isdigit():
            key[i] = int(j)
    return key

def signature(elem):
    ''' Build a signature string from elements '''
    retval = [elem[0]]
    i = 1
    j = 1
    for i in range(1, len(elem)):
        if elem[i] == retval[-1]:
            j += 1
        else:
            if j > 1:
                retval[-1] = retval[-1] + ("%d" % j)
            retval.append(elem[i])
            j = 1
    if j > 1:
        retval[-1] = retval[-1] + ("%d" % j)
    return "".join(retval)
