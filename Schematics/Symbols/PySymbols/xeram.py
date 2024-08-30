#!/usr/bin/env python3

''' 9 bit 1MBIT DRAM '''

from chip import Chip, FChip, ChipSig

class XERAM(FChip):

    ''' 9 bit 1MBIT DRAM '''

    symbol_name = "XERAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 9))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "CAS"))
        self.sig_left(ChipSig("-->+", "RAS"))
        self.sig_left(ChipSig("-->+", "DCK"))
        self.sig_left(ChipSig("-->+", "ICK"))
        self.sig_left(ChipSig("-->+", "OE"))

        self.sig_right(ChipSig("+<->", "DQ", 0, 8))

        self.finish(17)

class XBRAM(FChip):

    ''' 9 bit 1MBIT DRAM '''

    symbol_name = "XBRAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "CAS"))
        self.sig_left(ChipSig("-->+", "RAS"))
        self.sig_left(ChipSig("-->+", "DCK"))
        self.sig_left(ChipSig("-->+", "SET", 0, 1))
        self.sig_left(ChipSig("-->+", "CL", 0, 11))
        self.sig_left(ChipSig("-->+", "WD", 0, 5))

        self.sig_right(ChipSig("+<--", "ICK"))
        self.sig_right(ChipSig("+<--", "QCOE"))
        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_right(ChipSig("+<->", "DQC", 0, 8))
        self.sig_level()
        self.sig_left(ChipSig("<->+", "DQT", 0, 63))
        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.finish()

def register():
    yield XERAM()
    yield XBRAM()
