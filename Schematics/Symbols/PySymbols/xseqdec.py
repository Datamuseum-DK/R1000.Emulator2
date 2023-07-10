#!/usr/bin/env python3

''' SEQ Decode RAM '''

from chip import Chip, FChip, ChipSig

class XSEQDEC(FChip):

    ''' SEQ Decode RAM '''

    symbol_name = "XSEQDEC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DISP", 0, 15))
        self.sig_left(ChipSig("-->+", "DCNT", 0, 7))
        self.sig_left(ChipSig("-->+", "DIAG", 0, 7))
        self.sig_left(ChipSig("-->+", "DGCS"))
        self.sig_left(ChipSig("-->+", "MODE", 0, 1))
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "DWOE"))
        self.sig_left(ChipSig("-->+", "ICC", 0, 3))
        self.sig_left(ChipSig("-->+", "EMAC", 0, 7))
        self.sig_left(ChipSig("-->+", "CDDG"))
        self.sig_left(ChipSig("-->+", "IMX"))
        self.sig_left(ChipSig("-->+", "VAL", 0, 15))
        self.sig_left(ChipSig("-->+", "TCLK"))
        self.sig_left(ChipSig("-->+", "BCLK"))
        self.sig_left(ChipSig("-->+", "TMX"))

        self.sig_right(ChipSig("+-->", "BSEL"))
        self.sig_right(ChipSig("+-->", "DPER"))
        self.sig_right(ChipSig("+-->", "SCAN", 0, 3))
        self.sig_right(ChipSig("+-->", "UAD", 0, 15))
        self.sig_right(ChipSig("+-->", "DEC", 0, 7))
        self.sig_right(ChipSig("+-->", "CCL", 0, 3))
        self.sig_right(ChipSig("+-->", "EMP"))
        self.sig_right(ChipSig("+-->", "DSP", 0, 15))

        self.finish()

def register():
    yield XSEQDEC()


