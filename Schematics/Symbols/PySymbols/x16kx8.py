#!/usr/bin/env python3

''' 16KX8 SRAM'''

from chip import Chip, FChip, ChipSig

class X16KX8(FChip):

    ''' 16KX8 SRAM'''

    symbol_name = "X16KX8"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "D", 0, 7))
        self.sig_left(ChipSig("-->+", "A", 0, 13))

        self.sig_right(ChipSig("+===", "Q", 0, 7))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "WE"))

        self.finish()

def register():
    yield X16KX8()


