#!/usr/bin/env python3

''' SEQ Decode RAM '''

from chip import Chip, FChip, ChipSig

class XSEQDEC(FChip):

    ''' SEQ Decode RAM '''

    symbol_name = "XSEQDEC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DISP", 0, 15))
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "EMAC", 0, 6))
        self.sig_left(ChipSig("-->+", "IMX"))
        self.sig_left(ChipSig("<->+", "DQV", 0, 15))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "ILDRN"))
        self.sig_left(ChipSig("-->+", "DISPA"))
        self.sig_left(ChipSig("-->+", "FLIP"))
        self.sig_left(ChipSig("-->+", "QVOE"))

        self.sig_right(ChipSig("+-->", "UAD", 0, 15))
        self.sig_right(ChipSig("+-->", "DEC", 0, 7))
        self.sig_right(ChipSig("+-->", "CCL", 0, 3))
        self.sig_right(ChipSig("+-->", "EMP"))
        self.sig_right(ChipSig("+-->", "DSP", 0, 15))
        self.sig_right(ChipSig("+-->", "ME", 0, 6))

        self.finish()

def register():
    yield XSEQDEC()


