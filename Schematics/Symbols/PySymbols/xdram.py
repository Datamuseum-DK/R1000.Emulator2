#!/usr/bin/env python3

''' 64 bit 1MBIT DRAM '''

from chip import Chip, FChip, ChipSig

class XDRAM(FChip):

    ''' 64 bit 1MBIT DRAM '''

    symbol_name = "XDRAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 9))
        self.sig_left(ChipSig("-->+", "OE"))
        self.sig_left(ChipSig("-->+", "CAS"))
        self.sig_left(ChipSig("-->+", "RAS"))

        self.sig_right(ChipSig("+<->", "DQ", 0, 63))

        self.finish()

class XFRAM(FChip):

    ''' 64 bit 1MBIT DRAM '''

    symbol_name = "XFRAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 9))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "CAS"))
        self.sig_left(ChipSig("-->+", "RAS"))
        self.sig_left(ChipSig("-->+", "DCK"))
        self.sig_left(ChipSig("-->+", "ICK"))
        self.sig_left(ChipSig("-->+", "OE"))

        self.sig_right(ChipSig("+<->", "DQ", 0, 63))

        self.finish(17)

def register():
    yield XDRAM()
    yield XFRAM()
