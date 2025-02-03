#!/usr/bin/env python3

''' TYP Writable Control Store '''

from chip import Chip, FChip, ChipSig

class XTYPWCS(FChip):

    ''' TYP Writable Control Store '''

    symbol_name = "XTYPWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "UAD", 0, 13))

        self.sig_right(ChipSig("+-->", "FPDT"))

        self.finish()

def register():
    yield XTYPWCS()


