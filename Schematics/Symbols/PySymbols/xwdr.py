#!/usr/bin/env python3

''' Write Data Register '''

from chip import Chip, FChip, ChipSig

class XWDR(FChip):

    ''' Write Data Register '''

    symbol_name = "XWDR"

    def __init__(self):
        super().__init__()
        self.sig_left(ChipSig("-->+", "DB", 0, 63))
        self.sig_right(ChipSig("+-->", "QB", 0, 63))

        self.sig_left(ChipSig("-->+", "DP", 0, 7))
        self.sig_right(ChipSig("+-->", "QP", 0, 7))

        self.sig_left(ChipSig("-->+", "LOADWDR"))
        self.sig_left(ChipSig("-->+", "SCLKEN"))
        self.sig_left(ChipSig("-->+", "DIAGWDREN"))
        self.sig_left(ChipSig("-->+", "DIAGWDRS0"))
        self.sig_left(ChipSig("-->+", "DIAGWDRS1"))
        self.sig_left(ChipSig("-->+", "SCANWDR"))
        self.sig_left(ChipSig("-->+", "CLK"))

        self.sig_right(ChipSig("o<->", "DIAG", 0, 7))

        self.finish()

def register():
    yield XWDR()


