#!/usr/bin/env python3

''' SEQ FIU parity '''

from chip import Chip, FChip, ChipSig

class XFIUPAR(FChip):

    ''' SEQ FIU parity '''

    symbol_name = "XFIUPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "FIU", 0, 31))
        self.sig_left(ChipSig("-->+", "FIUP", 0, 7))

        self.sig_right(ChipSig("+-->", "FPERR"))

        self.finish()

def register():
    yield XFIUPAR()


