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
        self.sig_left(ChipSig("-->+", "MC2N"))
        self.sig_left(ChipSig("-->+", "DRH"))
        self.sig_left(ChipSig("-->+", "HIGH"))
        self.sig_left(ChipSig("-->+", "PSET", 0, 3))
        self.sig_left(ChipSig("-->+", "DBM", 0, 3))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "AEH"))
        self.sig_left(ChipSig("-->+", "ALH"))
        self.sig_left(ChipSig("-->+", "BEH"))
        self.sig_left(ChipSig("-->+", "BLH"))
        self.sig_left(ChipSig("-->+", "EHIT"))

        self.sig_right(ChipSig("+-->", "PHAE"))
        self.sig_right(ChipSig("+-->", "PHAL"))
        self.sig_right(ChipSig("+-->", "PHBE"))
        self.sig_right(ChipSig("+-->", "PHBL"))
        self.sig_right(ChipSig("+-->", "AHT"))
        self.sig_right(ChipSig("+-->", "BAHT"))
        self.sig_right(ChipSig("+-->", "BHT"))
        self.sig_right(ChipSig("+-->", "BBHT"))
        self.sig_right(ChipSig("+===", "SET2"))
        self.sig_right(ChipSig("+===", "SET3"))

        self.finish()

def register():
    yield XM28()


