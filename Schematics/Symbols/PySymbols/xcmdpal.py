#!/usr/bin/env python3

''' MEM32 CMDPAL '''

from chip import Chip, FChip, ChipSig

class XCMDPAL(FChip):

    ''' MEM32 CMDPAL '''

    symbol_name = "XCMDPAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "MCMD", 0, 3))
        self.sig_left(ChipSig("-->+", "CCNT"))
        self.sig_left(ChipSig("-->+", "ABRT"))

        self.sig_right(ChipSig("+-->", "CMD", 0, 3))
        self.sig_right(ChipSig("+-->", "MC2N"))
        self.sig_right(ChipSig("+-->", "CYO"))
        self.sig_right(ChipSig("+-->", "CYT"))

        self.finish()

def register():
    yield XCMDPAL()


