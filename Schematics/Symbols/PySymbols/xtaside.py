#!/usr/bin/env python3

''' TYP A-bus mux+latch '''

from chip import Chip, FChip, ChipSig

class XTASIDE(FChip):

    ''' Type A-bus mux+latch '''

    symbol_name = "XTASIDE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "LE"))
        self.sig_left(ChipSig("-->+", "AODIAG"))
        self.sig_left(ChipSig("-->+", "UA", 0, 5))
        self.sig_left(ChipSig("-->+", "LOOP", 0, 9))

        self.sig_left(ChipSig("-->+", "C", 0, 63))

        self.sig_right(ChipSig("+-->", "A", 0, 63))
        self.sig_right(ChipSig("+-->", "AB0"))

        self.finish()

def register():
    yield XTASIDE()


