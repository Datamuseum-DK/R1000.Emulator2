#!/usr/bin/env python3

''' MEM32 BUSPAL '''

from chip import Chip, FChip, ChipSig

class XBUSPAL(FChip):

    ''' MEM32 BUSPAL '''

    symbol_name = "XBUSPAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "CMD", 0, 3))
        self.sig_left(ChipSig("-->+", "MC2N"))
        self.sig_left(ChipSig("-->+", "DBMD", 0, 3))
        self.sig_left(ChipSig("-->+", "SETA"))
        self.sig_left(ChipSig("-->+", "SETB"))

        self.sig_right(ChipSig("+-->", "TADIR"))
        self.sig_right(ChipSig("+-->", "TBDIR"))
        self.sig_right(ChipSig("+-->", "INTB"))
        self.sig_right(ChipSig("+-->", "TAOE"))
        self.sig_right(ChipSig("+-->", "TBOE"))

        self.sig_right(ChipSig("+-->", "TADIN"))
        self.sig_right(ChipSig("+-->", "TBDIN"))
        self.sig_right(ChipSig("+-->", "INTAS"))
        self.sig_right(ChipSig("+-->", "INTBS"))
        self.sig_right(ChipSig("+-->", "INTAN"))
        self.sig_right(ChipSig("+-->", "INTBN"))
        self.sig_right(ChipSig("+-->", "DROEN"))
        self.sig_right(ChipSig("+-->", "EXTSL"))

        self.finish()

def register():
    yield XBUSPAL()


