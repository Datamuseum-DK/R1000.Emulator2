#!/usr/bin/env python3

''' FIU Rotators '''

from chip import Chip, FChip, ChipSig

class XFIUROT(FChip):

    ''' FIU Rotator Type side'''

    symbol_name = "XFIUROT"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TCLK"))
        self.sig_left(ChipSig("-->+", "RD", 0, 63))
        self.sig_left(ChipSig("-->+", "DF", 0, 63))

        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+<--", "FT"))
        self.sig_right(ChipSig("+<->", "DQT", 0, 63))

        self.sig_right(ChipSig("+<--", "ZLEN"))
        self.sig_right(ChipSig("+<--", "SBIT", 0, 6))
        self.sig_right(ChipSig("+<--", "EBIT", 0, 6))

        self.finish()


class XFIUROV(FChip):

    ''' FIU Rotator Value side '''

    symbol_name = "XFIUROV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "VCLK"))
        self.sig_left(ChipSig("-->+", "RD", 0, 63))
        self.sig_left(ChipSig("<->+", "DQF", 0, 63))

        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+<--", "FV"))
        self.sig_right(ChipSig("+<->", "DQV", 0, 63))

        self.sig_right(ChipSig("+<--", "ZLEN"))
        self.sig_right(ChipSig("+<--", "SBIT", 0, 6))
        self.sig_right(ChipSig("+<--", "EBIT", 0, 6))

        self.sig_right(ChipSig("+<--", "SIGN"))
        self.sig_right(ChipSig("+<--", "SEL", 0, 1))

        self.sig_right(ChipSig("+<--", "QFOE"))

        self.finish()

def register():
    yield XFIUROT()
    yield XFIUROV()


