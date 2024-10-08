#!/usr/bin/env python3

''' MEM32 page 30 '''

from chip import Chip, FChip, ChipSig

class XM30(FChip):

    ''' MEM32 page 30 '''

    symbol_name = "XM30"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "MCN"))
        self.sig_left(ChipSig("-->+", "MC"))
        self.sig_left(ChipSig("-->+", "AHIT"))
        self.sig_left(ChipSig("-->+", "BHIT"))
        self.sig_left(ChipSig("-->+", "LAB"))

        self.sig_right(ChipSig("+-->", "CASA"))
        self.sig_right(ChipSig("+-->", "CASB"))

        self.finish()

def register():
    yield XM30()


