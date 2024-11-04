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

        self.sig_left(ChipSig("-->+", "OP", 0, 1))
        self.sig_left(ChipSig("-->+", "TCLK"))
        self.sig_left(ChipSig("-->+", "VCLK"))
        self.sig_left(ChipSig("-->+", "FT"))
        self.sig_left(ChipSig("-->+", "FV"))
        self.sig_left(ChipSig("-->+", "SEL", 0, 1))
        self.sig_left(ChipSig("-->+", "MCND", 0, 8))
        self.sig_left(ChipSig("-->+", "RFCK"))

        self.sig_left(ChipSig("-->+", "LMAR"))
        self.sig_left(ChipSig("-->+", "CLK2X"))
        self.sig_left(ChipSig("-->+", "CSA", 0, 2))
        self.sig_left(ChipSig("-->+", "SELPG"))
        self.sig_left(ChipSig("-->+", "SELIN"))
        self.sig_left(ChipSig("-->+", "INMAR"))
        self.sig_left(ChipSig("-->+", "PGMOD"))
        self.sig_left(ChipSig("-->+", "PRED"))
        self.sig_left(ChipSig("-->+", "CNV", 0, 3))
        self.sig_left(ChipSig("-->+", "MAROE"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "RDSRC"))
        self.sig_left(ChipSig("-->+", "LFRC", 0, 1))
        self.sig_left(ChipSig("-->+", "FSRC"))
        self.sig_left(ChipSig("-->+", "LSRC"))
        self.sig_left(ChipSig("-->+", "ORSR"))
        self.sig_left(ChipSig("-->+", "AO", 0, 6))

        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_right(ChipSig("+<->", "DQSPC", 0, 2))
        self.sig_right(ChipSig("+<--", "QSPCOE"))
        self.sig_right(ChipSig("+<->", "DQADR", 0, 63))
        self.sig_right(ChipSig("+<--", "QADROE"))

        self.sig_right(ChipSig("+<--", "OCLK"))
        self.sig_right(ChipSig("+-->", "OREG0"))
        self.sig_right(ChipSig("+<--", "OSRC"))
        self.sig_right(ChipSig("+-->", "XWRD"))

        self.sig_right(ChipSig("+<--", "LDMDR"))
        self.sig_right(ChipSig("+<--", "SCLKE"))
        self.sig_right(ChipSig("+<--", "OL", 0, 6))
        self.sig_right(ChipSig("+<--", "LFL", 0, 6))

        self.sig_right(ChipSig("+-->", "NMATCH"))

        self.sig_right(ChipSig("+-->", "LINE", 0, 11))
        self.sig_right(ChipSig("+-->", "WEZ"))
        self.sig_right(ChipSig("+-->", "NTOP"))
        self.sig_right(ChipSig("+-->", "PXNX"))

        self.sig_right(ChipSig("+-->", "OOR"))
        self.sig_right(ChipSig("+-->", "HOFS", 0, 3))
        self.sig_right(ChipSig("+-->", "INRG"))
        self.sig_right(ChipSig("+-->", "CHIT"))
        self.finish()

def register():
    yield XROTF()
