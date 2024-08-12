#!/usr/bin/env python3

''' TYP/VAL B-side of RF '''

from chip import Chip, FChip, ChipSig

class XVBSIDE(FChip):

    ''' VAL B-side of RF '''

    symbol_name = "XVBSIDE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DV", 0, 63))
        self.sig_left(ChipSig("-->+", "C", 0, 63))

        self.sig_right(ChipSig("+-->", "B", 0, 63))
        self.sig_right(ChipSig("+<--", "Q2"))
        self.sig_right(ChipSig("+<--", "BWE"))
        self.sig_right(ChipSig("+<--", "H2"))
        self.sig_right(ChipSig("+<--", "BADR", 0, 9))
        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+-->", "BMSB"))

        self.sig_right(ChipSig("+<--", "UIRB", 0, 5))
        self.sig_right(ChipSig("+<--", "LHIT"))
        self.sig_right(ChipSig("+<--", "GETL"))

        self.finish()


class XTVBSIDE(FChip):

    ''' TYP/VAL B-side of RF '''

    symbol_name = "XTVBSIDE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQX", 0, 63))
        self.sig_left(ChipSig("-->+", "C", 0, 63))

        self.sig_right(ChipSig("+-->", "B", 0, 63))
        self.sig_right(ChipSig("+<--", "BLE"))
        self.sig_right(ChipSig("+<--", "BOE"))
        self.sig_right(ChipSig("+<--", "BOE7"))
        self.sig_right(ChipSig("+<--", "BROE"))
        self.sig_right(ChipSig("+<--", "BROE7"))
        self.sig_right(ChipSig("+<--", "RFWE"))
        self.sig_right(ChipSig("+<--", "RFCS"))
        self.sig_right(ChipSig("+<--", "A", 0, 9))
        self.sig_right(ChipSig("+<--", "QXOE"))
        self.sig_right(ChipSig("+-->", "BB0"))

        self.finish()

def register():
    yield XVBSIDE()
    yield XTVBSIDE()


