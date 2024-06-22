#!/usr/bin/env python3

''' FIU Hash RAM '''

from chip import Chip, FChip, ChipSig

class XFHRAM(FChip):

    ''' FIU Hash RAM '''

    symbol_name = "XFHRAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SPC", 0, 2))
        self.sig_left(ChipSig("-->+", "OFF", 0, 24))
        self.sig_left(ChipSig("-->+", "NAM", 0, 31))
        self.sig_right(ChipSig("+<--", "BIG"))
        self.sig_right(ChipSig("+<--", "WE"))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "D", 0, 23))
        self.sig_right(ChipSig("+-->", "Q", 0, 11))

        self.finish()

def register():
    yield XFHRAM()


