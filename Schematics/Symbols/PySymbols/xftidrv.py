#!/usr/bin/env python3

''' FIU TI driver '''

from chip import Chip, FChip, ChipSig

class XFTIDRV(FChip):

    ''' FIU TI driver '''

    symbol_name = "XFTIDRV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "D", 0, 31))
        self.sig_left(ChipSig("-->+", "OE"))

        self.sig_right(ChipSig("+===", "Q", 0, 31))

        self.finish()

def register():
    yield XFTIDRV()


