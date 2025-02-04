#!/usr/bin/env python3

''' VAL Writable Control Store '''

from chip import Chip, FChip, ChipSig

class XVALWCS(FChip):

    ''' VAL Writable Control Store '''

    symbol_name = "XVALWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "UAD", 0, 13))

        self.sig_right(ChipSig("+-->", "UIR", 0, 39))
        self.sig_right(ChipSig("+-->", "ALD"))
        self.sig_right(ChipSig("+-->", "BLD"))

        self.finish()

def register():
    yield XVALWCS()


