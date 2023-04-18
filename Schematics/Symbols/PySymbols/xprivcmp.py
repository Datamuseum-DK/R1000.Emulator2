#!/usr/bin/env python3

''' TYP priv-comparator '''

from chip import Chip, FChip, ChipSig

class XPRIVCMP(FChip):

    ''' TYP priv-comparator '''

    symbol_name = "XPRIVCMP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 63))
        self.sig_left(ChipSig("-->+", "AOM"))
        self.sig_left(ChipSig("-->+", "BOM"))
        self.sig_left(ChipSig("-->+", "ABM"))
        self.sig_left(ChipSig("-->+", "BBM"))
        self.sig_right(ChipSig("+<--", "B", 0, 63))
        self.sig_right(ChipSig("+-->", "NAMES"))
        self.sig_right(ChipSig("+-->", "PATH"))
        self.sig_right(ChipSig("+-->", "AOP"))
        self.sig_right(ChipSig("+-->", "BOP"))
        self.sig_right(ChipSig("+-->", "IOP"))
        self.sig_right(ChipSig("+-->", "DP"))

        self.finish()

def register():
    yield XPRIVCMP()


