#!/usr/bin/env python3

''' VAL UIR.RAND decode '''

from chip import Chip, FChip, ChipSig

class XVRAND(FChip):

    ''' VAL UIR.RAND decode '''

    symbol_name = "XVRAND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RAND", 0, 3))

        self.sig_right(ChipSig("+-->", "ALU", 0, 2))
        self.sig_right(ChipSig("+-->", "INCL"))
        self.sig_right(ChipSig("+-->", "DECL"))
        self.sig_right(ChipSig("+-->", "CNTZ"))
        self.sig_right(ChipSig("+-->", "DIV"))
        self.sig_right(ChipSig("+-->", "SNEAK"))

        self.finish()

def register():
    yield XVRAND()


