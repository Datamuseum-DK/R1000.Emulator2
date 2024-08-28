#!/usr/bin/env python3

''' SEQ lex '''

from chip import Chip, FChip, ChipSig

class XSLEX(FChip):

    ''' SEQ lex level stuff '''

    symbol_name = "XSLEX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SCLK"))
        self.sig_right(ChipSig("+-->", "LXCN"))

        self.sig_left(ChipSig("-->+", "RES", 0, 3))

        self.sig_left(ChipSig("-->+", "LRN", 0, 2))

        self.finish()

def register():
    yield XSLEX()


