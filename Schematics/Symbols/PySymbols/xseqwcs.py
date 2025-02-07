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
        self.sig_left(ChipSig("-->+", "SFSTP"))

        self.sig_right(ChipSig("+-->", "UIR", 0, 26))

        self.finish()

def register():
    yield XSEQWCS()


