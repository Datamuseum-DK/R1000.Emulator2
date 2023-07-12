#!/usr/bin/env python3

''' TYP/VAL RF Parity Check '''

from chip import Chip, FChip, ChipSig

class XTVRFPAR(FChip):

    ''' TYP/VAL RF Parity Check '''

    symbol_name = "XTVRFPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SNEAK"))
        self.sig_left(ChipSig("-->+", "FIU", 0, 7))
        self.sig_left(ChipSig("-->+", "WDR", 0, 7))
        self.sig_left(ChipSig("-->+", "CCHK", 0, 7))

        self.sig_right(ChipSig("+-->", "PERR"))
        self.sig_right(ChipSig("+<--", "DGCO"))
        self.sig_right(ChipSig("+<--", "CSRC"))
        self.sig_right(ChipSig("+<--", "CSPL"))
        self.sig_right(ChipSig("+<--", "AP", 0, 7))

        self.finish()

def register():
    yield XTVRFPAR()


