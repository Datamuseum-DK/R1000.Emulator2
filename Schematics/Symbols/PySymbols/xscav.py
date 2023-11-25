#!/usr/bin/env python3

''' SEQ Scavenger '''

from chip import Chip, FChip, ChipSig

class XSCAV(FChip):

    ''' SEQ Scavenger '''

    symbol_name = "XSCAV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "MSP", 0, 2))
        self.sig_left(ChipSig("-->+", "A", 0, 9))

        self.sig_right(ChipSig("+-->", "SD"))
        self.sig_right(ChipSig("+-->", "SP"))
        self.sig_right(ChipSig("+<--", "VIQOE"))
        self.sig_level()
        self.sig_left(ChipSig("-->+", "VID", 0, 7))
        self.sig_right(ChipSig("+===", "VIQ", 0, 7))

        self.finish()

def register():
    yield XSCAV()


