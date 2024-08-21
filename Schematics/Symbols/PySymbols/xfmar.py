#!/usr/bin/env python3

''' FIU MAR &co '''

from chip import Chip, FChip, ChipSig

class XFMAR(FChip):

    ''' FIU MAR &co '''

    symbol_name = "XFMAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "QSPCOE"))
        self.sig_left(ChipSig("<->+", "DQSPC", 0, 2))
        self.sig_left(ChipSig("-->+", "QADROE"))
        self.sig_left(ChipSig("<->+", "DQADR", 0, 63))
        self.sig_left(ChipSig("-->+", "LMAR"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "CLK2X"))
        self.sig_left(ChipSig("-->+", "OREG", 0, 6))
        self.sig_left(ChipSig("-->+", "CTCLK"))
        self.sig_left(ChipSig("-->+", "CSA", 0, 2))
        self.sig_left(ChipSig("-->+", "COCLK"))

        self.sig_right(ChipSig("+<--", "QVIOE"))
        self.sig_right(ChipSig("+===", "DQVI", 0, 63))

        self.sig_right(ChipSig("+-->", "MSPC", 0, 2))
        self.sig_right(ChipSig("+-->", "NMATCH"))
        self.sig_right(ChipSig("+-->", "LCTP"))

        self.sig_left(ChipSig("-->+", "BIG"))
        self.sig_left(ChipSig("-->+", "PXING"))
        self.sig_left(ChipSig("-->+", "SELPG"))
        self.sig_left(ChipSig("-->+", "SELIN"))
        self.sig_left(ChipSig("-->+", "INMAR"))
        self.sig_left(ChipSig("-->+", "PGMOD"))
        self.sig_right(ChipSig("+-->", "LINE", 0, 11))
        self.sig_right(ChipSig("+-->", "WEZ"))
        self.sig_right(ChipSig("+-->", "NTOP"))
        self.sig_right(ChipSig("+-->", "PXNX"))

        self.sig_left(ChipSig("-->+", "PRED"))
        self.sig_left(ChipSig("-->+", "SCLK"))
        self.sig_left(ChipSig("-->+", "OCLK"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "NMAT"))
        self.sig_left(ChipSig("-->+", "CNV", 0, 3))
        self.sig_right(ChipSig("+-->", "OOR"))
        self.sig_right(ChipSig("+-->", "HOFS", 0, 3))
        self.sig_right(ChipSig("+-->", "INRG"))
        self.sig_right(ChipSig("+-->", "CHIT"))

        self.finish()

def register():
    yield XFMAR()


