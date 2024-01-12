#!/usr/bin/env python3

''' VAL UIR.A decode '''

from chip import Chip, FChip, ChipSig

class XVADEC(FChip):

    ''' VAL UIR.A decode '''

    symbol_name = "XVADEC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q1"))
        self.sig_left(ChipSig("-->+", "AODON"))
        self.sig_left(ChipSig("-->+", "A", 0, 5))

        self.sig_right(ChipSig("+-->", "A"))
        self.sig_right(ChipSig("+-->", "LOOP"))
        self.sig_right(ChipSig("+-->", "PROD"))
        self.sig_right(ChipSig("+-->", "ZERO"))

        self.finish()

def register():
    yield XVADEC()


