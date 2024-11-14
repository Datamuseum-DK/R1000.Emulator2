#!/usr/bin/env python3

''' SEQ Writeable Control Store '''

from chip import Chip, FChip, ChipSig

class XSEQWCS(FChip):

    ''' SEQ Writeable Control Store '''

    symbol_name = "XSEQWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "UA", 0, 13))
        self.sig_left(ChipSig("-->+", "UM", 0, 1))
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "HLR"))
        self.sig_left(ChipSig("-->+", "SCE"))
        self.sig_left(ChipSig("-->+", "DSP0"))
        self.sig_left(ChipSig("-->+", "PDCK"))
        self.sig_left(ChipSig("-->+", "LMAC"))

        self.sig_left(ChipSig("<--+", "R", 0, 15))

        self.sig_right(ChipSig("+-->", "UIR", 0, 41))
        self.sig_right(ChipSig("+-->", "HALT"))
        self.sig_right(ChipSig("+-->", "LLM"))
        self.sig_right(ChipSig("+-->", "LLMI"))
        self.sig_right(ChipSig("+-->", "MDSP"))
        self.sig_right(ChipSig("+-->", "LEXI"))
        self.sig_right(ChipSig("+-->", "RAS", 0, 1))

        self.finish()

def register():
    yield XSEQWCS()


