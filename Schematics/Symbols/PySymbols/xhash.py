#!/usr/bin/env python3

''' 8x8 parity generator '''

from chip import Chip, FChip, ChipSig

class XHASH(FChip):

    ''' mem32 hash generator '''

    symbol_name = "XHASH"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "S", 0, 2))
        self.sig_left(ChipSig("-->+", "A", 0, 56))
        self.sig_left(ChipSig("-->+", "LDMAR"))
        self.sig_left(ChipSig("-->+", "STPCK"))
        self.sig_left(ChipSig("-->+", "Q4"))

        self.sig_right(ChipSig("+-->", "P", 0, 3))
        self.sig_right(ChipSig("+-->", "L", 0, 11))
        self.sig_right(ChipSig("+-->", "MW", 0, 5))

        self.finish()

def register():
    yield XHASH()
