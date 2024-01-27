#!/usr/bin/env python3

''' TYP UIR.RAND decode '''

from chip import Chip, FChip, ChipSig

class XTRAND(FChip):

    ''' TYP UIR.RAND decode '''

    symbol_name = "XTRAND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RAND", 0, 3))

        self.sig_right(ChipSig("+-->", "ALU", 0, 2))
        self.sig_right(ChipSig("+-->", "INCL"))
        self.sig_right(ChipSig("+-->", "DECL"))
        self.sig_right(ChipSig("+-->", "SPLTC"))
        self.sig_right(ChipSig("+-->", "CATOL"))
        self.sig_right(ChipSig("+-->", "CBTOL"))
        self.sig_right(ChipSig("+-->", "CATOB"))
        self.sig_right(ChipSig("+-->", "CABL"))
        self.sig_right(ChipSig("+-->", "DIV"))
        self.sig_right(ChipSig("+-->", "LOAD"))
        self.sig_right(ChipSig("+-->", "SPPR"))
        self.sig_right(ChipSig("+-->", "CLSYB"))
        self.sig_right(ChipSig("+-->", "ADMW"))

        self.finish()

def register():
    yield XTRAND()


