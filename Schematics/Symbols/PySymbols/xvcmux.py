#!/usr/bin/env python3

''' VAL C-bus mux '''

from chip import Chip, FChip, ChipSig

class XVCMUX(FChip):

    ''' VAL C-bus mux '''

    symbol_name = "XVCMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("===+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_right(ChipSig("+===", "ADR", 0, 63))
        self.sig_right(ChipSig("+<--", "ADROE"))

        # self.sig_left(ChipSig("-->+", "ALU", 0, 63))
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
        self.sig_left(ChipSig("-->+", "ACH", 0, 4))
        self.sig_left(ChipSig("-->+", "ACL", 0, 4))
        self.sig_left(ChipSig("-->+", "CI"))
        self.sig_left(ChipSig("<--+", "COM"))
        self.sig_left(ChipSig("<--+", "COH"))
        self.sig_left(ChipSig("<--+", "ZERO", 0, 7))
        self.sig_left(ChipSig("-->+", "RAND", 0, 3))
        self.sig_left(ChipSig("-->+", "LBOT"))
        self.sig_left(ChipSig("-->+", "LTOP"))
        self.sig_left(ChipSig("-->+", "LPOP"))
        self.sig_left(ChipSig("-->+", "CSAO", 0, 3))
        self.sig_left(ChipSig("-->+", "CSAH"))
        self.sig_left(ChipSig("-->+", "CSAW"))
        self.sig_left(ChipSig("-->+", "ALOOP"))
        self.sig_left(ChipSig("-->+", "BLOOP"))

        self.sig_right(ChipSig("+<--", "COND"))
        self.sig_right(ChipSig("+<--", "CSEL", 0, 2))
        self.sig_right(ChipSig("+<--", "AWE"))

        self.sig_right(ChipSig("+-->", "AMSB"))
        self.sig_right(ChipSig("+-->", "BMSB"))
        self.sig_right(ChipSig("+-->", "CMSB"))

        self.sig_right(ChipSig("+-->", "ALUR", 0, 2))
        self.sig_right(ChipSig("+-->", "CNTZ"))
        self.sig_right(ChipSig("+-->", "DIV"))
        self.sig_right(ChipSig("+-->", "SNEAK"))
        self.sig_right(ChipSig("+-->", "CNT", 0, 9))
        self.sig_right(ChipSig("+-->", "CNTOV"))
        self.sig_right(ChipSig("+-->", "CWE"))
        self.sig_right(ChipSig("+-->", "WEN"))

        self.finish()

def register():
    yield XVCMUX()


