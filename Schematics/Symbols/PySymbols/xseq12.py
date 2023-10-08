#!/usr/bin/env python3

''' SEQ 12 Noodle Logic '''

from chip import Chip, FChip, ChipSig

class XSEQ12(FChip):

    ''' SEQ 12 Noodle Logic '''

    symbol_name = "XSEQ12"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "MD"))
        self.sig_left(ChipSig("-->+", "MSD", 0, 2))
        self.sig_left(ChipSig("-->+", "UTOS"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "IRDS", 1, 2))
        self.sig_left(ChipSig("-->+", "TYP", 0, 31))
        self.sig_left(ChipSig("-->+", "TCLK"))
        self.sig_left(ChipSig("-->+", "TOSS"))
        self.sig_left(ChipSig("-->+", "RWE"))
        self.sig_left(ChipSig("-->+", "RADR", 0, 3))
        self.sig_left(ChipSig("-->+", "SGEXT"))
        self.sig_left(ChipSig("-->+", "DSP", 0, 15))
        self.sig_left(ChipSig("-->+", "CTL", 0, 2))
        self.sig_left(ChipSig("-->+", "CMR"))
        self.sig_left(ChipSig("-->+", "FIU", 0, 31))
        self.sig_left(ChipSig("-->+", "SVCLK"))
        self.sig_left(ChipSig("-->+", "PDCLK"))
        self.sig_left(ChipSig("-->+", "STCLK"))
        self.sig_left(ChipSig("-->+", "TOPLD"))
        self.sig_left(ChipSig("-->+", "LSTPD"))

        self.sig_right(ChipSig("+-->", "NRAM"))
        self.sig_right(ChipSig("+-->", "TNAM"))
        self.sig_right(ChipSig("+-->", "VNAM"))
        self.sig_right(ChipSig("+-->", "COUT"))
        self.sig_right(ChipSig("+-->", "ROFS", 0, 19))
        self.sig_right(ChipSig("+-->", "OB", 0, 19))

        self.finish()

def register():
    yield XSEQ12()


