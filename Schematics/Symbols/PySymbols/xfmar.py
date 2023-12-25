#!/usr/bin/env python3

''' FIU MAR &co '''

from chip import Chip, FChip, ChipSig

class XFMAR(FChip):

    ''' FIU MAR &co '''

    symbol_name = "XFMAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "YSPCOE"))
        self.sig_left(ChipSig("<->+", "BSPC", 0, 2))
        self.sig_left(ChipSig("-->+", "YADROE"))
        self.sig_left(ChipSig("<->+", "BADR", 0, 63))
        self.sig_left(ChipSig("-->+", "YDIAGOE"))
        self.sig_left(ChipSig("<->+", "BDIAG", 0, 7))
        self.sig_left(ChipSig("-->+", "MSEL", 0, 1))
        self.sig_left(ChipSig("-->+", "LMAR"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "CLK2X"))
        self.sig_left(ChipSig("-->+", "OREG", 0, 6))
        self.sig_left(ChipSig("-->+", "INC", 0, 5))
        self.sig_left(ChipSig("-->+", "DGPAR"))
        self.sig_left(ChipSig("-->+", "CTCLK"))
        self.sig_left(ChipSig("-->+", "CSA", 0, 2))
        self.sig_left(ChipSig("-->+", "COCLK"))

        self.sig_right(ChipSig("+<--", "VIOE"))
        self.sig_right(ChipSig("+===", "VI", 0, 63))

        self.sig_right(ChipSig("+-->", "PAR", 0, 7))
        self.sig_right(ChipSig("+-->", "MADR", 0, 63))
        self.sig_right(ChipSig("+-->", "CTPAR", 0, 7))
        self.sig_right(ChipSig("+-->", "NMATCH"))
        self.sig_right(ChipSig("+-->", "CLD"))
        self.sig_right(ChipSig("+-->", "CCNT"))
        self.sig_right(ChipSig("+-->", "LCTP"))
        self.sig_right(ChipSig("+-->", "CTO", 0, 19))

        self.finish()

def register():
    yield XFMAR()


