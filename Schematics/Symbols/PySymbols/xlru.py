#!/usr/bin/env python3

''' MEM32 LRU logic '''

from chip import Chip, FChip, ChipSig

class XLRU(FChip):

    ''' MEM32 LRU logic '''

    symbol_name = "XLRU"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "LATE"))
        self.sig_left(ChipSig("-->+", "AB"))
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "CYC1"))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "TAG", 0, 5))
        self.sig_left(ChipSig("-->+", "NMAT"))
        self.sig_left(ChipSig("-->+", "H1"))

        self.sig_right(ChipSig("+-->", "HIT"))
        self.sig_right(ChipSig("+<--", "LOWB"))
        self.sig_right(ChipSig("+<--", "PHYS", 0, 3))

        self.finish()

def register():
    yield XLRU()
