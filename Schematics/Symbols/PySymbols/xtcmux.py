#!/usr/bin/env python3

''' TYP C-bus mux '''

from chip import Chip, FChip, ChipSig

class XTCMUX(FChip):

    ''' TYP C-bus mux '''

    symbol_name = "XTCMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))
        self.sig_left(ChipSig("<->+", "DQT", 0, 63))
        self.sig_left(ChipSig("-->+", "QTOE"))

        # UWORD order 
        self.sig_left(ChipSig("-->+", "UIRA", 0, 5))
        self.sig_left(ChipSig("-->+", "UIRB", 0, 5))
        self.sig_left(ChipSig("-->+", "FRM", 0, 4))
        self.sig_left(ChipSig("-->+", "RAND", 0, 3))
        self.sig_left(ChipSig("-->+", "UIRC", 0, 5))
        self.sig_left(ChipSig("-->+", "SEL"))
        self.sig_left(ChipSig("-->+", "AFNC", 0, 4))
        self.sig_left(ChipSig("-->+", "CSRC"))

        # CLOCKS
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "CCLK"))
        self.sig_left(ChipSig("-->+", "LBOT"))
        self.sig_left(ChipSig("-->+", "LTOP"))
        self.sig_left(ChipSig("-->+", "LPOP"))
        self.sig_left(ChipSig("-->+", "CSAO", 0, 3))
        self.sig_left(ChipSig("-->+", "CSAH"))
        self.sig_left(ChipSig("-->+", "CSAW"))

        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "ALOOP"))
        self.sig_left(ChipSig("-->+", "BLOOP"))
        self.sig_left(ChipSig("-->+", "ACOND"))
        self.sig_left(ChipSig("-->+", "SPC", 0, 2))

        self.sig_right(ChipSig("+===", "ADR", 0, 63))
        self.sig_right(ChipSig("+<--", "ADROE"))

        self.sig_right(ChipSig("+-->", "A", 0, 63))
        self.sig_right(ChipSig("+-->", "AMSB"))
        self.sig_right(ChipSig("+-->", "B", 0, 63))

        self.sig_right(ChipSig("+-->", "LOVF"))
        self.sig_right(ChipSig("+-->", "LO", 0, 9))
        self.sig_right(ChipSig("+-->", "CWE"))
        self.sig_right(ChipSig("+-->", "WEN"))
        self.sig_right(ChipSig("+-->", "COM"))
        self.sig_right(ChipSig("+-->", "COH"))
        self.sig_right(ChipSig("+-->", "ZERO", 0, 7))
        self.sig_right(ChipSig("+-->", "ALMSB"))

        self.finish()

def register():
    yield XTCMUX()


