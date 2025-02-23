#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip, FChip, ChipSig

class FIU(FChip):

    ''' FIU First Stage Rotator '''

    symbol_name = "FIU"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))

        self.finish(19)

def register():
    yield FIU()


