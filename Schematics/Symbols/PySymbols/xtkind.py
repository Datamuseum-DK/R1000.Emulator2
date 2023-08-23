#!/usr/bin/env python3

''' TYP Kind Matching '''

from chip import Chip, FChip, ChipSig

class XTKIND(FChip):

    ''' TYP Kind Matching '''

    symbol_name = "XTKIND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLIT", 0, 6))
        self.sig_left(ChipSig("-->+", "A", 0, 6))
        self.sig_left(ChipSig("-->+", "B", 0, 6))
        self.sig_left(ChipSig("-->+", "UC", 0, 4))

        self.sig_right(ChipSig("+-->", "OKM"))
        self.sig_right(ChipSig("+-->", "AEQL"))
        self.sig_right(ChipSig("+-->", "AEQB"))
        self.sig_right(ChipSig("+-->", "BEQL"))
        self.sig_right(ChipSig("+-->", "ABLE"))
        self.sig_right(ChipSig("+-->", "CLCE"))
        self.sig_right(ChipSig("+-->", "CLEV"))
        self.sig_right(ChipSig("+-->", "SYSU"))

        self.finish()

def register():
    yield XTKIND()


