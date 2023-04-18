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
   128bit ECC checker/generator
   ============================

'''

from part import PartModel, PartFactory

CBITS = '''
           TYP:0                                                     TYP:63 VAL:0                                                     VAL:63 CHECKBIT
    ECCG16 --------------------------------++++++++++++++++++++++++++++++++ --------------------------------++++++++++++++++++++++++++++++++ +--------
    ECCG17 ++++++++++++++++++++++++++++++++-------------------------------- --------------------------------++++++++++++++++++++++++++++++++ -+-------
    ECCG28 ++++++++-----++---+++-+--+++--+-++++++++-----++---+++-+--+++--+- ++++++++-------+-----+-+--+-+-+----++---+-+-+--++++---++++-+---- --+------
    ECCG29 +++++++++++++-++++---+-------+--+++++++++++++-++++---+-------+-- -+------++++++++-------++----++-----+++++--+-++----+---+--++---+ ---+-----
    ECCG44 ++-----+++++++++--++--+++---+-++++-----+++++++++--++--+++-----++ ---+---+----+++---++++--++++------------++++++++---++++------++- ----+----
    ECCG45 -----++++--+---++++++++++++----+-----++++--+---++++++++++++-+--+ --+--++----+--+-++++++++-----+---++----+--------++++++++----+--+ -----+---
    ECCG46 +-++--+-++--+---++----+-+++++++++-++--+-++--+---++----+-++++++++ ----+-+--++------++---+-+++++++++-++--+--+----++--+-+----++-++-- ------+--
    ECCG61 -++-++----+-++-++-+-++-++-++++---++-++----+-++-++-+-++-++-++++-- +---++-++-+-+--++---+-+--+-----+++---+----+--+---+---+--++++++++ -------+-
    ECCG62 ---++----+++-++--+-+++-+-+-+++++---++----+++-++--+-+++-+-+-+++++ ++++----++-+-+--++-+-------++--+++++++++-+-++---+-------+-----+- --------+
'''


class XECC64(PartFactory):

    ''' 128bit ECC checker/generator '''

    def state(self, file):
        ''' Extra state variable '''

        file.write("\tuint64_t typ_mask;\n")
        file.write("\tuint64_t val_mask;\n")
        file.write("\tbool invert;\n")

    def init(self, file):
        ''' Extra initialization '''

        invert = [0, 0, 0, 0, 1, 1, 1, 0, 0]
        cbit = 0
        pfx = ""
        for line in CBITS.split("\n"):
            flds = line.replace('-', '0').replace('+', '1').split()
            if len(flds) != 4 or len(flds[1]) != 64:
                continue
            typ = int(flds[1], 2)
            val = int(flds[2], 2)
            file.write('\t' + pfx + 'if (!strcmp(arg, "ECCB%d")) {\n' % cbit)
            file.write('\t\tstate->typ_mask = 0x%x;\n' % typ)
            file.write('\t\tstate->val_mask = 0x%x;\n' % val)
            file.write('\t\tstate->invert = %d;\n' % invert[cbit])
            pfx = "} else "
            cbit += 1

        file.fmt('''
		|	} else {
		|		cout << this->name() << " :: " << arg << "\\n";
		|		exit(3);
		|	}
		|''')

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	uint64_t typ, val, out;
		|
		|	BUS_T_READ(typ);
		|	typ &= state->typ_mask;
		|	BUS_V_READ(val);
		|	val &= state->val_mask;
		|	out = typ ^ val;
		|	out = (out ^ (out >> 32)) & 0x00000000ffffffff;
		|	out = (out ^ (out >> 16)) & 0x000000000000ffff;
		|	out = (out ^ (out >> 8)) & 0x00000000000000ff;
		|	out = (out ^ (out >> 4)) & 0x000000000000000f;
		|	out = (out ^ (out >> 2)) & 0x0000000000000003;
		|	out = (out ^ (out >> 1)) & 0x0000000000000001;
		|	out ^= PIN_I=>;
		|	out ^= state->invert;
		|
		|	TRACE(
		|	    << " t " << BUS_T_TRACE()
		|	    << " v " << BUS_V_TRACE()
		|	    << " i " << PIN_I?
		|	    << " o " << out
		|	);
		|
		|	PIN_O<=(out);
		|
		|''')

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("XECC64", PartModel("XECC64", XECC64))
