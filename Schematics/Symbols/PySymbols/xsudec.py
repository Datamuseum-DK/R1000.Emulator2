#!/usr/bin/env python3

''' SEQ uins decode '''

from chip import Chip, FChip, ChipSig

class XSUDEC(FChip):

    ''' SEQ uins decode '''

    symbol_name = "XSUDEC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "COND"))
        self.sig_left(ChipSig("-->+", "LCOND"))
        self.sig_left(ChipSig("-->+", "BADH"))
        self.sig_left(ChipSig("-->+", "BRTIM", 0, 1))
        self.sig_left(ChipSig("-->+", "BRTYP", 0, 3))
        self.sig_left(ChipSig("-->+", "MEVENT"))
        self.sig_left(ChipSig("-->+", "UEVENT"))

        self.sig_left(ChipSig("-->+", "BRBH0"))
        self.sig_left(ChipSig("-->+", "BRBH1"))
        self.sig_left(ChipSig("-->+", "BRBH3"))

        self.sig_left(ChipSig("-->+", "SCLKEN"))

        self.sig_right(ChipSig("+-->", "UASEL"))
        self.sig_right(ChipSig("+-->", "GSEL", 0, 1))

        self.sig_right(ChipSig("+-->", "WDISP"))
        self.sig_right(ChipSig("+-->", "CASEN"))
        self.sig_right(ChipSig("+-->", "RTN"))
        self.sig_right(ChipSig("+-->", "PUSHBR"))
        self.sig_right(ChipSig("+-->", "PUSH"))

        self.sig_right(ChipSig("+-->", "ROM", 0, 7))

        self.finish()

def register():
    yield XSUDEC()


