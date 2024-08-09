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
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "LOP", 0, 9))
        self.sig_left(ChipSig("-->+", "ZSCK"))
        self.sig_left(ChipSig("-->+", "UIA", 0, 5))
        self.sig_left(ChipSig("-->+", "MSTRT"))
        self.sig_left(ChipSig("-->+", "MSRC", 0, 3))
        self.sig_left(ChipSig("-->+", "MDST", 0, 1))
        self.sig_left(ChipSig("-->+", "B", 0, 63))

        self.sig_right(ChipSig("+-->", "C", 0, 63))
        self.sig_right(ChipSig("+<--", "VAL", 0, 63))
        self.sig_right(ChipSig("+<--", "COND"))
        self.sig_right(ChipSig("+<--", "CSEL", 0, 2))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "WE"))
        self.sig_right(ChipSig("+<--", "ADR", 0, 9))
        self.sig_right(ChipSig("+-->", "A", 0, 63))

        self.finish()

def register():
    yield XVCMUX()


