#!/usr/bin/env python3

''' MEM32 Tracing '''

from chip import Chip, FChip, ChipSig

class XMTRC(FChip):

    ''' MEM32 Tracing '''

    symbol_name = "XMTRC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLKQ2"))
        self.sig_left(ChipSig("-->+", "CLKQ4"))

        self.sig_left(ChipSig("-->+", "ROWE"))
        self.sig_left(ChipSig("-->+", "ROW", 0, 7))
        self.sig_left(ChipSig("-->+", "COLE"))
        self.sig_left(ChipSig("-->+", "COL", 0, 7))

        self.sig_right(ChipSig("+-->", "DR", 3, 10))

        self.finish()

def register():
    yield XMTRC()


