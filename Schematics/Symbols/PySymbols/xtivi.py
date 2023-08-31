#!/usr/bin/env python3

''' FIU TIVI decoder '''

from chip import Chip, FChip, ChipSig

class XTIVI(FChip):

    ''' FIU TIVI decoder '''

    symbol_name = "XTIVI"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "EN"))
        self.sig_left(ChipSig("-->+", "TIVI", 0, 3))

        self.sig_right(ChipSig("+-->", "TVOE", 0, 7))

        self.finish()

def register():
    yield XTIVI()


