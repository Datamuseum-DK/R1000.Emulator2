#!/usr/bin/env python3

''' IOP's 128KX32 RAM '''

from chip import Chip, FChip, ChipSig

class XCPURAM(FChip):

    ''' R1000 access to IOP RAM '''

    def __init__(self):
        self.symbol_name = "XCPURAM"
        super().__init__()

        self.sig_left(ChipSig("-->+", "ITYP", 0, 63))
        self.sig_right(ChipSig("+===", "OTYP", 0, 31))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "SCLK"))
        self.sig_right(ChipSig("+<--", "INCA"))
        self.sig_right(ChipSig("+<--", "LDA"))
        self.sig_right(ChipSig("+-->", "OFLO"))
        self.sig_right(ChipSig("+<--", "WR"))
        self.sig_right(ChipSig("+<--", "RD"))

        self.finish()

def register():
    yield XCPURAM()


