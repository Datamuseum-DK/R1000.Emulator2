#!/usr/bin/env python3

''' MEM32 CNTRPAL '''

from chip import Chip, FChip, ChipSig

class XCNTRPAL(FChip):

    ''' MEM32 CNTRPAL '''

    symbol_name = "XCNTRPAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "RFSH"))
        self.sig_left(ChipSig("-->+", "DIAG", 0, 3))
        self.sig_left(ChipSig("-->+", "DCNT", 0, 4))
        self.sig_left(ChipSig("-->+", "OVFI"))

        self.sig_right(ChipSig("+-->", "OVFO"))
        self.sig_right(ChipSig("+-->", "TRA", 0, 3))
        self.sig_right(ChipSig("+-->", "CEN"))

        self.finish()

def register():
    yield XCNTRPAL()


