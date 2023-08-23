#!/usr/bin/env python3

''' TYP priv-comparator '''

from chip import Chip, FChip, ChipSig

class XPRIVCMP(FChip):

    ''' TYP priv-comparator '''

    symbol_name = "XPRIVCMP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 63))
        self.sig_left(ChipSig("-->+", "OFC"))
        self.sig_left(ChipSig("-->+", "CLIT", 0, 6))
        self.sig_left(ChipSig("-->+", "UCOD", 0, 4))

        self.sig_right(ChipSig("+<--", "B", 0, 63))
        self.sig_right(ChipSig("+-->", "NAMES"))
        self.sig_right(ChipSig("+-->", "PATH"))
        self.sig_right(ChipSig("+-->", "AOP"))
        self.sig_right(ChipSig("+-->", "BOP"))
        self.sig_right(ChipSig("+-->", "IOP"))

        self.sig_right(ChipSig("+-->", "OKM"))
        self.sig_right(ChipSig("+-->", "AEQL"))
        self.sig_right(ChipSig("+-->", "AEQB"))
        self.sig_right(ChipSig("+-->", "BEQL"))
        self.sig_right(ChipSig("+-->", "ABLE"))
        self.sig_right(ChipSig("+-->", "CLCE"))
        self.sig_right(ChipSig("+-->", "CLEV"))
        self.sig_right(ChipSig("+-->", "SYSU"))
        self.sig_right(ChipSig("+-->", "BBIT", 0, 6))
        self.sig_right(ChipSig("+-->", "BBUF", 0, 2))

        self.finish()

def register():
    yield XPRIVCMP()


