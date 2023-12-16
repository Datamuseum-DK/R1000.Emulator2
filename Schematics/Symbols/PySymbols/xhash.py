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
        self.sig_left(ChipSig("-->+", "T", 0, 3))
        self.sig_left(ChipSig("-->+", "TE"))

        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "R"))
        self.sig_right(ChipSig("+<--", "M", 0, 1))
        self.sig_right(ChipSig("+<--", "TRC", 0, 11))
        self.sig_right(ChipSig("+-->", "P", 0, 3))
        self.sig_right(ChipSig("+-->", "L", 0, 11))
        self.sig_right(ChipSig("+-->", "TAG", 0, 13))

        self.finish()

def register():
    yield XHASH()
