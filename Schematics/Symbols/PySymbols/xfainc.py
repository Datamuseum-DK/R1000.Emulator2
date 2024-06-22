#!/usr/bin/env python3

''' FIU Address increment '''

from chip import Chip, FChip, ChipSig

class XFAINC(FChip):

    ''' FIU Address increment '''

    symbol_name = "XFAINC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "PXING"))
        self.sig_left(ChipSig("-->+", "SELPG"))
        self.sig_left(ChipSig("-->+", "SELIN"))
        self.sig_left(ChipSig("-->+", "INMAR"))
        self.sig_left(ChipSig("-->+", "PGMOD"))
        self.sig_left(ChipSig("-->+", "MARO", 0, 24))
        self.sig_left(ChipSig("-->+", "DPAR"))

        self.sig_right(ChipSig("+-->", "INCO", 0, 5))
        self.sig_right(ChipSig("+-->", "PXNX"))
        self.sig_right(ChipSig("+-->", "NTOP"))
        self.sig_right(ChipSig("+-->", "WEZ"))
        self.sig_right(ChipSig("+-->", "INCP"))

        self.finish()

def register():
    yield XFAINC()


