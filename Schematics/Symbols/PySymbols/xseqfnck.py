#!/usr/bin/env python3

''' SEQ Field Num Check '''

from chip import Chip, FChip, ChipSig

class XSEQFNCK(FChip):

    ''' SEQ Field Num Check '''

    symbol_name = "XSEQFNCK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "VAL", 0, 23))
        self.sig_left(ChipSig("-->+", "CURI", 0, 15))
        self.sig_left(ChipSig("-->+", "FCHR"))
        self.sig_left(ChipSig("-->+", "ENFU"))

        self.sig_right(ChipSig("+-->", "FNER"))
        self.sig_right(ChipSig("+-->", "FERR"))

        self.finish()

def register():
    yield XSEQFNCK()


