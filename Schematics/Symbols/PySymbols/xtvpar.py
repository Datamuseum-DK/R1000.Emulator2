#!/usr/bin/env python3

''' TV RF parity RAM'''

from chip import Chip, FChip, ChipSig

class XTVPAR(FChip):

    ''' TV RF parity RAM'''

    symbol_name = "XTVPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK2X"))
        self.sig_left(ChipSig("-->+", "CLKQ4"))
        self.sig_left(ChipSig("-->+", "AADR", 0, 9))
        self.sig_left(ChipSig("-->+", "BADR", 0, 9))
        self.sig_left(ChipSig("-->+", "CCHK", 0, 7))
        self.sig_left(ChipSig("-->+", "AWE"))
        self.sig_left(ChipSig("-->+", "BWE"))

        self.sig_right(ChipSig("+-->", "APAR", 0, 7))
        self.sig_right(ChipSig("+-->", "BPAR", 0, 7))

        self.finish()

def register():
    yield XTVPAR()


