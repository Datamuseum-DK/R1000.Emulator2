#!/usr/bin/env python3

''' VAL complete multiplier '''

from chip import Chip, FChip, ChipSig

class XMULT(FChip):

    ''' VAL complete multiplier '''

    symbol_name = "XMULT"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 63))
        self.sig_left(ChipSig("-->+", "B", 0, 63))

        self.sig_right(ChipSig("+===", "P", 0, 63))
        self.sig_right(ChipSig("o<--", "OE"))
        self.sig_right(ChipSig("+<--", "START"))
        self.sig_right(ChipSig("+<--", "SRC", 0, 3))
        self.sig_right(ChipSig("+<--", "Q2"))
        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "DST", 0, 1))

        self.finish()

def register():
    yield XMULT()


