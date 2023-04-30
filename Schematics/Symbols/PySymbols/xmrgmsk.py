#!/usr/bin/env python3

''' FIU Merge Mask '''

from chip import Chip, FChip, ChipSig

class XMRGMSK(FChip):

    ''' FIU Merge Mask '''

    symbol_name = "XMRGMSK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SBIT", 0, 6))
        self.sig_left(ChipSig("-->+", "EBIT", 0, 6))
        self.sig_left(ChipSig("-->+", "ZL"))

        self.sig_right(ChipSig("+-->", "TMSK", 0, 63))
        self.sig_right(ChipSig("+-->", "VMSK", 0, 63))

        self.finish()

def register():
    yield XMRGMSK()


