#!/usr/bin/env python3

''' TYP/VAL A-bus driver '''

from chip import Chip, FChip, ChipSig

class XTVADR(FChip):

    ''' TYP/VAL A-bus driver '''

    symbol_name = "XTVADR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "ALU", 0, 63))
        self.sig_right(ChipSig("+===", "ADR", 0, 63))

        self.sig_left(ChipSig("-->+", "SPC", 0, 2))
        self.sig_left(ChipSig("-->+", "FRCPA"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "AEN"))

        self.sig_right(ChipSig("+-->", "ADRE"))
        self.sig_right(ChipSig("+<--", "ADROE"))

        self.finish()

def register():
    yield XTVADR()


