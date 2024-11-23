#!/usr/bin/env python3

''' VAL C-bus mux '''

from chip import Chip, FChip, ChipSig

class VAL(FChip):

    ''' VAL C-bus mux '''

    symbol_name = "VAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("===+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_left(ChipSig("-->+", "SEL", 0, 1))
        self.sig_left(ChipSig("-->+", "CSRC"))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "CCLK"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "ZSCK"))
        self.sig_left(ChipSig("-->+", "UIRA", 0, 5))
        self.sig_left(ChipSig("-->+", "UIRB", 0, 5))
        self.sig_left(ChipSig("-->+", "FRM", 0, 4))
        self.sig_left(ChipSig("-->+", "UIRC", 0, 5))
        self.sig_left(ChipSig("-->+", "MSRC", 0, 3))
        self.sig_left(ChipSig("-->+", "SPC", 0, 2))
        self.sig_left(ChipSig("-->+", "RAND", 0, 3))
        self.sig_left(ChipSig("-->+", "LBOT"))
        self.sig_left(ChipSig("-->+", "LTOP"))
        self.sig_left(ChipSig("-->+", "LPOP"))
        self.sig_left(ChipSig("-->+", "CSAO", 0, 3))
        self.sig_left(ChipSig("-->+", "CSAH"))
        self.sig_left(ChipSig("-->+", "CSAW"))
        self.sig_left(ChipSig("-->+", "ALOOP"))
        self.sig_left(ChipSig("-->+", "BLOOP"))
        self.sig_left(ChipSig("-->+", "AFNC", 0, 4))
        self.sig_left(ChipSig("-->+", "CSEL", 0, 6))
        self.sig_left(ChipSig("-->+", "AWE"))


        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_right(ChipSig("+===", "ADR", 0, 63))
        self.sig_right(ChipSig("+<--", "ADROE"))

        self.sig_right(ChipSig("+-->", "CNTZ"))
        self.sig_right(ChipSig("+-->", "CNTOV"))
        self.sig_right(ChipSig("+-->", "CWE"))
        self.sig_right(ChipSig("+-->", "VCNDA"))
        self.sig_right(ChipSig("+-->", "VCNDB"))
        self.sig_right(ChipSig("+-->", "VCNDC"))
        self.sig_right(ChipSig("+-->", "QBIT"))

        self.finish()

def register():
    yield VAL()


