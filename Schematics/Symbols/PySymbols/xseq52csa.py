#!/usr/bin/env python3

''' SEQ 52 CSA '''

from chip import Chip, FChip, ChipSig

class XSEQ52CSA(FChip):

    ''' SEQ 52 CSA '''

    symbol_name = "XSEQ52CSA"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "NVE", 0, 3))
        self.sig_left(ChipSig("-->+", "DEC", 0, 4))

        self.sig_right(ChipSig("+-->", "UFL"))
        self.sig_right(ChipSig("+-->", "OFL"))
        self.sig_right(ChipSig("+-->", "CSA", 0, 3))
        self.finish()

def register():
    yield XSEQ52CSA()


