#!/usr/bin/env python3

''' Micro Stack '''

from chip import Chip, FChip, ChipSig

class XUSTK(FChip):

    ''' Micro Stack '''

    symbol_name = "XUSTK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "STKEN"))
        self.sig_left(ChipSig("-->+", "WRITE"))
        self.sig_left(ChipSig("-->+", "CNTENA"))
        self.sig_left(ChipSig("-->+", "SEL", 0, 1))

        self.sig_left(ChipSig("-->+", "Q3COND"))
        self.sig_left(ChipSig("-->+", "LATCHED"))

        self.sig_left(ChipSig("-->+", "CURU", 0, 13))

        self.sig_left(ChipSig("-->+", "FIU", 0, 15))
        self.sig_left(ChipSig("-->+", "BRNCH", 0, 13))
        
        self.sig_right(ChipSig("+-->", "TOPU", 0, 15))
        self.sig_right(ChipSig("+<--", "CSR"))
        self.sig_right(ChipSig("+<--", "STOP"))
        self.sig_right(ChipSig("+-->", "SSZ"))

        self.finish()

def register():
    yield XUSTK()


