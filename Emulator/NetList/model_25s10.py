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
   25S10 Four-Bit Shifter with Three-State Outputs
   ===============================================

   Ref: Am25s10 03611B
'''


from part import PartModel, PartFactory

class Am25S10(PartFactory):

    ''' 25S10 Four-Bit Shifter with Three-State Outputs '''

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        file.fmt('''
		|	bool output[4];
		|	unsigned sel;
		|''')

        if not self.comp["OE"].net.is_const():
            file.fmt('''
		|
		|	if (PIN_OE=>) {
		|		TRACE("Z");
		|		BUS_Y_Z();
		|		next_trigger(PIN_OE.negedge_event());
		|		return;
		|	}
		|''')
        elif self.comp["OE"].net.is_pu():
            file.fmt('''
		|		BUS_Y_Z();
		|		return;
		|''')

        file.fmt('''
		|	BUS_S_READ(sel);
		|	switch(sel) {
		|	case 0:
		|		output[0] = PIN_I0=>;
		|		output[1] = PIN_I1=>;
		|		output[2] = PIN_I2=>;
		|		output[3] = PIN_I3=>;
		|		break;
		|	case 1:
		|		output[0] = PIN_IM1=>;
		|		output[1] = PIN_I0=>;
		|		output[2] = PIN_I1=>;
		|		output[3] = PIN_I2=>;
		|		break;
		|	case 2:
		|		output[0] = PIN_IM2=>;
		|		output[1] = PIN_IM1=>;
		|		output[2] = PIN_I0=>;
		|		output[3] = PIN_I1=>;
		|		break;
		|	case 3:
		|		output[0] = PIN_IM3=>;
		|		output[1] = PIN_IM2=>;
		|		output[2] = PIN_IM1=>;
		|		output[3] = PIN_I0=>;
		|		break;
		|	}
		|	TRACE(
		|	    << " s " << BUS_S_TRACE()
		|	    << " oe_ " << PIN_OE?
		|	    << " i " << PIN_IM3? << PIN_IM2? << PIN_IM1? << BUS_I_TRACE()
		|	    << "|"
		|	    << output[0] << output[1] << output[2] << output[3]
		|	);
		|	PIN_Y0<=(output[0]);
		|	PIN_Y1<=(output[1]);
		|	PIN_Y2<=(output[2]);
		|	PIN_Y3<=(output[3]);
		|''')

class Model25S10(PartModel):
    ''' Am25S10 '''

    def assign(self, comp, part_lib):
        for node in comp:
            if node.pin.name[:2] == "I-":
                node.pin.name = "IM" + node.pin.name[2:]
        super().assign(comp, part_lib)

def register(part_lib):
    ''' Register component model '''

    part_lib.add_part("25S10", Model25S10("25S10", Am25S10))
