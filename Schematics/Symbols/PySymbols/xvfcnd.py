#!/usr/bin/env python3

''' VAL FIU conditions '''

from chip import Chip, FChip, ChipSig

class XVFCND(FChip):

    ''' VAL FIU conditions '''

    symbol_name = "XVFCND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SEL", 0, 6))
        self.sig_left(ChipSig("-->+", "SNK"))
        self.sig_left(ChipSig("-->+", "BAD0"))
        self.sig_left(ChipSig("-->+", "BBD0"))
        self.sig_left(ChipSig("-->+", "ACO"))
        self.sig_left(ChipSig("-->+", "LVAL"))
        self.sig_left(ChipSig("-->+", "AZ", 0, 7))

        self.sig_right(ChipSig("+-->", "FCSEL", 0, 2))
        self.sig_right(ChipSig("+-->", "FCOND"))

        self.finish()

def register():
    yield XVFCND()


