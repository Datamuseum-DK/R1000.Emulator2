#!/usr/bin/env python3

''' MEM32 TAG comparator '''

from chip import Chip, FChip, ChipSig

class XTAGCMP(FChip):

    ''' MEM32 TAG comparator'''

    symbol_name = "XTAGCMP"

    def __init__(self):
        super().__init__()
        self.sig_left(ChipSig("-->+", "TA",0, 44))
        self.sig_left(ChipSig("-->+", "TS",0, 2))

        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+<--", "EQ"))
        self.sig_right(ChipSig("+<--", "E"))
        self.sig_right(ChipSig("+<--", "NM", 0, 31))
        self.sig_right(ChipSig("+<--", "PG", 0, 12))
        self.sig_right(ChipSig("+<--", "SP", 0, 2))
        self.sig_right(ChipSig("+-->", "NME"))
        self.sig_right(ChipSig("+-->", "OME"))
        self.sig_right(ChipSig("+-->", "NML"))
        self.sig_right(ChipSig("+-->", "OML"))

        self.finish()

def register():
    yield XTAGCMP()


