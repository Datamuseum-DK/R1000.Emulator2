#!/usr/bin/env python3

''' FIU Merge MUX '''

from chip import Chip, FChip, ChipSig

class XMRGMUX(FChip):

    ''' FIU Merge MUX '''

    symbol_name = "XMRGMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "VI", 0, 63))
        self.sig_left(ChipSig("-->+", "FI", 0, 63))

        self.sig_right(ChipSig("+<--", "SIGN"))
        self.sig_right(ChipSig("+<--", "SEL", 0, 1))
        self.sig_right(ChipSig("+-->", "VMUX", 0, 63))

        self.finish()

def register():
    yield XMRGMUX()


