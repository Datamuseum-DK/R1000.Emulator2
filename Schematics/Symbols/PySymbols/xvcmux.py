#!/usr/bin/env python3

''' VAL C-bus mux '''

from chip import Chip, FChip, ChipSig

class XVCMUX(FChip):

    ''' VAL C-bus mux '''

    symbol_name = "XVCMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "FIU", 0, 63))
        self.sig_left(ChipSig("-->+", "ALU", 0, 63))
        self.sig_left(ChipSig("-->+", "SEL", 0, 1))
        self.sig_left(ChipSig("-->+", "CSRC"))
        self.sig_left(ChipSig("-->+", "CSPL"))
        self.sig_left(ChipSig("-->+", "DGMS"))
        self.sig_left(ChipSig("-->+", "DGCO"))
        self.sig_left(ChipSig("-->+", "FPA"))
        self.sig_left(ChipSig("<--+", "P", 0, 7))
        self.sig_left(ChipSig("-->+", "CLK"))

        self.sig_right(ChipSig("+-->", "C", 0, 63))
        self.sig_right(ChipSig("+<--", "WDR", 0, 63))
        self.sig_right(ChipSig("+<--", "COND"))
        self.sig_right(ChipSig("+<--", "CSEL", 0, 2))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "WE"))
        self.sig_right(ChipSig("+<--", "A", 0, 9))

        self.finish()

def register():
    yield XVCMUX()


