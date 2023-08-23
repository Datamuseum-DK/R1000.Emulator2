#!/usr/bin/env python3

''' VAL conditions '''

from chip import Chip, FChip, ChipSig

class XVCOND(FChip):

    ''' VAL conditions '''

    symbol_name = "XVCOND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SEL", 0, 6))
        self.sig_left(ChipSig("-->+", "CCLK"))
        self.sig_left(ChipSig("-->+", "SCLK"))
        self.sig_left(ChipSig("-->+", "C0H"))
        self.sig_left(ChipSig("-->+", "C1A"))
        self.sig_left(ChipSig("-->+", "OVRE"))
        self.sig_left(ChipSig("-->+", "C1C"))
        self.sig_left(ChipSig("-->+", "C1H"))
        self.sig_left(ChipSig("-->+", "C2D"))
        self.sig_left(ChipSig("-->+", "BAD0"))
        self.sig_left(ChipSig("-->+", "BBD0"))
        self.sig_left(ChipSig("-->+", "ISBN"))
        self.sig_left(ChipSig("-->+", "SELA"))
        self.sig_left(ChipSig("-->+", "LCN", 0, 9))
        self.sig_left(ChipSig("-->+", "AZ", 0, 7))

        self.sig_right(ChipSig("+-->", "VCOND", 0, 2))
        self.sig_right(ChipSig("+-->", "LVCND"))
        self.sig_right(ChipSig("+-->", "MBIT"))

        self.finish()

def register():
    yield XVCOND()


