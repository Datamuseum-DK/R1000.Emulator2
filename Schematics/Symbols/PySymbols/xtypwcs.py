#!/usr/bin/env python3

''' TYP Writable Control Store '''

from chip import Chip, FChip, ChipSig

class XTYPWCS(FChip):

    ''' TYP Writable Control Store '''

    symbol_name = "XTYPWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DGI", 0, 7))
        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "USEL"))
        self.sig_left(ChipSig("-->+", "PDCY"))
        self.sig_left(ChipSig("-->+", "UAC", 0, 13))
        self.sig_left(ChipSig("-->+", "UAD", 0, 13))
        self.sig_left(ChipSig("-->+", "DUAS"))
        self.sig_left(ChipSig("-->+", "WE"))

        self.sig_right(ChipSig("+-->", "UIR", 0, 46))
        self.sig_right(ChipSig("+-->", "CLIT", 0, 6))
        self.sig_right(ChipSig("+-->", "ALD"))
        self.sig_right(ChipSig("+-->", "BLD"))
        self.sig_right(ChipSig("+-->", "FPDT"))

        self.finish()

def register():
    yield XTYPWCS()


