#!/usr/bin/env python3

''' FIU CSA compare '''

from chip import Chip, FChip, ChipSig

class XCSACMP(FChip):

    ''' FIU CSA compare '''

    symbol_name = "XCSACMP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "PRED"))
        self.sig_left(ChipSig("-->+", "SCLK"))
        self.sig_left(ChipSig("-->+", "OCLK"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "NMAT"))
        self.sig_left(ChipSig("-->+", "DSEL"))
        self.sig_left(ChipSig("-->+", "DNVE"))
        self.sig_left(ChipSig("-->+", "CNV", 0, 3))
        self.sig_left(ChipSig("-->+", "A", 0, 19))
        self.sig_left(ChipSig("-->+", "B", 0, 19))

        self.sig_right(ChipSig("+-->", "OOR"))
        self.sig_right(ChipSig("+-->", "HOFS", 0, 3))
        self.sig_right(ChipSig("+-->", "INRG"))
        self.sig_right(ChipSig("+-->", "CHIT"))

        self.finish()

def register():
    yield XCSACMP()


