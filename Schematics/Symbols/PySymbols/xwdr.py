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

        self.sig_left(ChipSig("-->+", "LOADWDR"))
        self.sig_left(ChipSig("-->+", "SCLKEN"))
        self.sig_left(ChipSig("-->+", "DIAGWDREN"))
        self.sig_left(ChipSig("-->+", "DIAGWDRS0"))
        self.sig_left(ChipSig("-->+", "DIAGWDRS1"))
        self.sig_left(ChipSig("-->+", "CLK"))

        self.finish()

def register():
    yield XWDR()


