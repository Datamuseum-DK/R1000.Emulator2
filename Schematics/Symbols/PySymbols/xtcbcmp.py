#!/usr/bin/env python3

''' IOC TCB comparator '''

from chip import Chip, FChip, ChipSig

class XTCBCMP(FChip):

    ''' IOC TCB comparator '''

    symbol_name = "XTCBCMP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TYP", 0, 63))
        self.sig_left(ChipSig("-->+", "TOP", 0, 3))

        self.sig_right(ChipSig("+-->", "BELOW"))
        self.sig_right(ChipSig("+-->", "PFR"))

        self.finish()

def register():
    yield XTCBCMP()
