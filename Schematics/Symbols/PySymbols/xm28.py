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
        self.sig_left(ChipSig("-->+", "DEABT"))
        self.sig_left(ChipSig("-->+", "EABT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))
        self.sig_left(ChipSig("-->+", "DLABT"))
        self.sig_left(ChipSig("-->+", "DDISA"))
        self.sig_left(ChipSig("-->+", "TRDR", 1, 2))
        self.sig_left(ChipSig("-->+", "LAR", 2, 3))

        self.sig_right(ChipSig("+-->", "PHAE"))
        self.sig_right(ChipSig("+-->", "PHAL"))
        self.sig_right(ChipSig("+-->", "PHBE"))
        self.sig_right(ChipSig("+-->", "PHBL"))
        self.sig_right(ChipSig("+-->", "AHT"))
        self.sig_right(ChipSig("+-->", "BAHT"))
        self.sig_right(ChipSig("+-->", "BHT"))
        self.sig_right(ChipSig("+-->", "BBHT"))
        self.sig_right(ChipSig("+===", "SETA"))
        self.sig_right(ChipSig("+===", "SETB"))
        self.sig_right(ChipSig("+-->", "TXEOE"))
        self.sig_right(ChipSig("+-->", "TXLOE"))
        self.sig_right(ChipSig("+-->", "TXOEN"))
        self.sig_right(ChipSig("+-->", "TXXWE"))
        self.sig_right(ChipSig("+-->", "TXEWE"))
        self.sig_right(ChipSig("+-->", "TXLWE"))
        self.sig_right(ChipSig("+-->", "TGACE"))
        self.sig_right(ChipSig("+-->", "TGBCE"))
        self.sig_right(ChipSig("+-->", "TSC14"))
        self.sig_right(ChipSig("+-->", "SETAS"))
        self.sig_right(ChipSig("+-->", "SETBS"))
        self.sig_right(ChipSig("+-->", "PHT26"))
        self.sig_right(ChipSig("+-->", "DFHIT"))
        self.sig_right(ChipSig("+-->", "RCLKE"))
        self.sig_right(ChipSig("+-->", "ABORT"))
        self.sig_right(ChipSig("+-->", "EABRT"))
        self.sig_right(ChipSig("+-->", "LABRT"))

        self.sig_right(ChipSig("+-->", "DAA1D"))
        self.sig_right(ChipSig("+-->", "DBA1D"))
        self.sig_right(ChipSig("+-->", "DAA2D"))
        self.sig_right(ChipSig("+-->", "DBA2D"))
        self.sig_right(ChipSig("+-->", "DA2SL"))

        self.finish()

def register():
    yield XM28()


