#!/usr/bin/env python3

''' FIU Rotators '''

from chip import Chip, FChip, ChipSig

class XFIUROT(FChip):

    ''' FIU Rotator Type side'''

    symbol_name = "XFIUROT"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RCLK"))
        self.sig_left(ChipSig("-->+", "RD", 0, 63))
        self.sig_left(ChipSig("-->+", "DFI", 0, 63))

        self.sig_right(ChipSig("+<--", "QROE"))
        self.sig_right(ChipSig("+<--", "TVF"))
        self.sig_right(ChipSig("+<->", "DQR", 0, 63))

        self.sig_right(ChipSig("+<--", "ZLEN"))
        self.sig_right(ChipSig("+<--", "SBIT", 0, 6))
        self.sig_right(ChipSig("+<--", "EBIT", 0, 6))

        self.finish()


class XFIUROV(FChip):

    ''' FIU Rotator Value side '''

    symbol_name = "XFIUROV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RCLK"))
        self.sig_left(ChipSig("-->+", "RD", 0, 63))
        self.sig_left(ChipSig("<->+", "DQFI", 0, 63))

        self.sig_right(ChipSig("+<--", "QROE"))
        self.sig_right(ChipSig("+<--", "TVF"))
        self.sig_right(ChipSig("+<->", "DQR", 0, 63))

        self.sig_right(ChipSig("+<--", "ZLEN"))
        self.sig_right(ChipSig("+<--", "SBIT", 0, 6))
        self.sig_right(ChipSig("+<--", "EBIT", 0, 6))

        self.sig_right(ChipSig("+<--", "SIGN"))
        self.sig_right(ChipSig("+<--", "SEL", 0, 1))

        self.sig_right(ChipSig("+<--", "QFIOE"))

        self.sig_right(ChipSig("+<--", "PDIAG"))
        self.sig_right(ChipSig("+<--", "FIPOE"))
        self.sig_right(ChipSig("+===", "FIP", 0, 7))

        self.finish()

def register():
    yield XFIUROT()
    yield XFIUROV()


