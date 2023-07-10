#!/usr/bin/env python3

''' SEQ 34 Code Segment '''

from chip import Chip, FChip, ChipSig

class XCODSEG(FChip):

    ''' SEQ 34 Code Segment '''

    symbol_name = "XCODSEG"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "MCLK"))
        self.sig_left(ChipSig("-->+", "RCLK"))
        self.sig_left(ChipSig("-->+", "CSEL"))
        self.sig_left(ChipSig("-->+", "VAL", 0, 23))

        self.sig_right(ChipSig("+-->", "CSEG", 0, 23))

        self.finish(22)

def register():
    yield XCODSEG()


