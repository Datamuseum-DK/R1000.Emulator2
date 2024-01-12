#!/usr/bin/env python3

''' TYP/VAL Counter '''

from chip import Chip, FChip, ChipSig

class XTVCNT(FChip):

    ''' TYP/VAL Counter '''

    symbol_name = "XTVCNT"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLKQ4"))
        self.sig_left(ChipSig("-->+", "SCLKEN"))
        self.sig_left(ChipSig("-->+", "UIR", 0, 5))
        self.sig_left(ChipSig("-->+", "DLD"))
        self.sig_left(ChipSig("-->+", "DCT"))
        self.sig_left(ChipSig("-->+", "DEN"))
        self.sig_left(ChipSig("-->+", "INC"))
        self.sig_left(ChipSig("-->+", "DEC"))
        self.sig_left(ChipSig("-->+", "DIV"))
        self.sig_left(ChipSig("-->+", "D", 0, 11))

        self.sig_right(ChipSig("+-->", "CO"))
        self.sig_right(ChipSig("+-->", "Q", 0, 9))

        self.finish()

def register():
    yield XTVCNT()


