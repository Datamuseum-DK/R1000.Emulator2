#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip, FChip, ChipSig

class XROTF(FChip):

    ''' FIU First Stage Rotator '''

    symbol_name = "XROTF"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQT", 0, 63))
        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_left(ChipSig("-->+", "OP", 0, 1))
        self.sig_left(ChipSig("-->+", "TCLK"))
        self.sig_left(ChipSig("-->+", "VCLK"))
        self.sig_left(ChipSig("-->+", "FT"))
        self.sig_left(ChipSig("-->+", "FV"))
        self.sig_left(ChipSig("-->+", "SEL", 0, 1))

        self.sig_right(ChipSig("+<--", "RDSRC"))
        self.sig_right(ChipSig("+<--", "LFRC", 0, 1))
        self.sig_right(ChipSig("+<--", "LCLK"))
        self.sig_right(ChipSig("+-->", "LFRG", 0, 6))
        self.sig_right(ChipSig("+<--", "FSRC"))
        self.sig_right(ChipSig("+<--", "LSRC"))
        self.sig_right(ChipSig("+<--", "ORSR"))
        self.sig_right(ChipSig("+<--", "OCLK"))
        self.sig_right(ChipSig("+-->", "OREG", 0, 6))
        self.sig_right(ChipSig("+<--", "OSRC"))
        self.sig_right(ChipSig("+-->", "XWRD"))

        self.sig_right(ChipSig("+<--", "H1"))
        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "LDMDR"))
        self.sig_right(ChipSig("+<--", "SCLKE"))
        self.sig_right(ChipSig("+<--", "AO", 0, 6))
        self.sig_right(ChipSig("+<--", "OL", 0, 6))
        self.sig_right(ChipSig("+<--", "LFL", 0, 6))

        self.finish()

def register():
    yield XROTF()
