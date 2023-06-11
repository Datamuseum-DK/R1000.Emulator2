#!/usr/bin/env python3

''' 8x8 parity generator '''

from chip import Chip, FChip, ChipSig

class XHASH(FChip):

    ''' mem32 hash generator '''

    symbol_name = "XHASH"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "S", 0, 2))
        self.sig_left(ChipSig("-->+", "A", 0, 55))

        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+-->", "H", 0, 11))

        self.finish()

def register():
    yield XHASH()
