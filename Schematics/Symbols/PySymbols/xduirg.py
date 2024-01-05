#!/usr/bin/env python3

''' Diagnostic Prom '''

from chip import Chip, FChip, ChipSig

class XDUIRG(FChip):

    ''' Diagnostic Prom '''

    symbol_name = "XDUIRG"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "A", 0, 7))

        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+-->", "D", 0, 7))

        self.finish()

def register():
    yield XDUIRG()


