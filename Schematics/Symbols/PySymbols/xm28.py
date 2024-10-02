#!/usr/bin/env python3

''' MEM32 page 28 '''

from chip import Chip, FChip, ChipSig

class XM28(FChip):

    ''' MEM32 page 28 '''

    symbol_name = "XM28"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "Q1"))
        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "MC2"))
        self.sig_left(ChipSig("-->+", "LOBRD"))
        self.sig_left(ChipSig("-->+", "PSET", 0, 3))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "AEH"))
        self.sig_left(ChipSig("-->+", "ALH"))
        self.sig_left(ChipSig("-->+", "BEH"))
        self.sig_left(ChipSig("-->+", "BLH"))
        self.sig_left(ChipSig("-->+", "EHIT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))

        self.sig_right(ChipSig("+-->", "BAHT"))
        self.sig_right(ChipSig("+-->", "BBHT"))
        self.sig_right(ChipSig("+===", "SETA"))
        self.sig_right(ChipSig("+===", "SETB"))

        self.sig_right(ChipSig("+-->", "DAA1D"))
        self.sig_right(ChipSig("+-->", "DAA2D"))
        self.sig_right(ChipSig("+-->", "DA2SL"))

        self.sig_right(ChipSig("+-->", "T12Y"))
        self.sig_right(ChipSig("+-->", "T13Y"))

        self.finish()

def register():
    yield XM28()


