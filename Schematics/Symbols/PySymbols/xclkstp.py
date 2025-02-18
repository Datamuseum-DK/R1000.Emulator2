#!/usr/bin/env python3

''' Clock Stop '''

from chip import Chip, FChip, ChipSig

class XCLKSTP(FChip):

    ''' Clock Stop '''

    symbol_name = "XCLKSTP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q3"))

        self.sig_left(ChipSig("-->+", "DIAG", 0, 2))

        self.sig_left(ChipSig("-->+", "STOP", 0, 6))

        self.sig_right(ChipSig("+-->", "CLKRUN"))

        self.sig_right(ChipSig("+-->", "ICLK"))
        self.sig_right(ChipSig("+-->", "SCLK"))

        self.finish()

class XCLKSTPTV(FChip):

    ''' Clock Stop '''

    symbol_name = "XCLKSTPTV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q3"))

        self.sig_left(ChipSig("-->+", "DIAG", 0, 2))

        self.sig_left(ChipSig("-->+", "STOP", 0, 6))
        self.sig_left(ChipSig("-->+", "CSAWR"))

        self.sig_right(ChipSig("+-->", "SFSTP"))
        self.sig_right(ChipSig("+-->", "FREEZ"))
        self.sig_right(ChipSig("+-->", "RAMRUN"))

        self.finish()

def register():
    yield XCLKSTP()
    yield XCLKSTPTV()


