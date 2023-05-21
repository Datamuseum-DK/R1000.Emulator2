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
   Calculate a hash for the code section of all experiments
   ========================================================

   The z_code/diagproc_fast_dload() hacks need to recoginize
   which experiment has been downloaded.

   The koopman32 hash calculated over all octets, starting
   from first instruction makes a good compact 'key'.

   This mapping is only valid from experiment-file to key
   value, as some experiments have identical instructions,
   or are identical across boards (TYP/VAL in particular).

   To make it easier to spot where confusion might arise,
   we sort the resulting list numerically by key.
'''

import sys

from r1000_dfs import R1kDisk
from r1000_dfs_experiments import Experiment, is_experiment

def koopman32(octets):
    ''' see:
        http://checksumcrc.blogspot.com/2023/05/koopman-checksum.html
        https://arxiv.org/abs/2304.13496
    '''
    retval = 0
    for i in octets:
        retval = ((retval << 32) + i) % 0xFFFFFFFB
    retval <<= 32
    retval %= 0xFFFFFFFB
    return retval

def main():
    '''
       Produce exp_hash.h on stdout.
       Give disk image file as command line argument
    '''
    disk0 = R1kDisk(filename=sys.argv[1])
    lst = []
    for dirent in sorted(disk0.dfs):
        if not is_experiment(dirent):
            continue
        exp = Experiment(dirent)
        start_adr = exp.octets[0]
        hashkey = koopman32(exp.octets[start_adr - 0x10:])
        lst.append((hashkey, dirent.name))
    print('#!/bin/env python3')
    print('# NB: Machine generated, see .../Emulator/Dfs/make_exp_hash.py')
    print('')
    for hashkey, filename in sorted(lst):
        txt = "#define " + filename.replace(".", "_") + "_HASH"
        while len(txt.expandtabs()) < 48:
            txt += '\t'
        print(txt + "0x%08x" % hashkey)

if __name__ == "__main__":
    main()
