#!/usr/bin/env python3

''' MEM32 TSPAR generation '''

from chip import Chip, FChip, ChipSig

class XTSPAR(FChip):

    ''' MEM32 TSPAR generation '''

    symbol_name = "XTSPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "MD0"))
        self.sig_left(ChipSig("-->+", "DIS"))

        self.sig_right(ChipSig("+-->", "EOE"))
        self.sig_right(ChipSig("+-->", "LOE"))

        self.finish()

def register():
    yield XTSPAR()


