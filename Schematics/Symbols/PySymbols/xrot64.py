#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip, FChip, ChipSig

class XROTF(FChip):

    ''' FIU First Stage Rotator '''

    symbol_name = "XROTF"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TI", 0, 63))
        self.sig_left(ChipSig("-->+", "VI", 0, 63))

        self.sig_left(ChipSig("-->+", "AO", 0, 6))
        self.sig_left(ChipSig("-->+", "OL", 0, 6))
        self.sig_left(ChipSig("-->+", "LFL", 0, 6))
        self.sig_left(ChipSig("-->+", "OP", 0, 1))

        self.sig_right(ChipSig("+===", "Q", 0, 63))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+-->", "SGNB"))
        self.sig_right(ChipSig("+<--", "LFRC", 0, 1))
        self.sig_right(ChipSig("+<--", "LCLK"))
        self.sig_right(ChipSig("+-->", "LFRG", 0, 6))
        self.sig_right(ChipSig("+<--", "FSRC"))
        self.sig_right(ChipSig("+<--", "LSRC"))
        self.sig_right(ChipSig("+-->", "ZL"))
        self.sig_right(ChipSig("+<--", "OCE"))
        self.sig_right(ChipSig("+<--", "ORSR"))
        self.sig_right(ChipSig("+-->", "CKPN"))
        self.sig_right(ChipSig("+<--", "OCLK"))
        self.sig_right(ChipSig("+-->", "OREG", 0, 6))
        self.sig_right(ChipSig("+<--", "OSRC"))
        self.sig_right(ChipSig("+-->", "XWRD"))
        self.sig_right(ChipSig("+-->", "SBIT", 0, 6))
        self.sig_right(ChipSig("+-->", "EBIT", 0, 6))

        self.finish()

def register():
    yield XROTF()
