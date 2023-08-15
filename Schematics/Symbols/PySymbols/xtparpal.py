#!/usr/bin/env python3

''' MEM32 TPARPAL '''

from chip import Chip, FChip, ChipSig

class XTPARPAL(FChip):

    ''' MEM32 TPARPAL '''

    symbol_name = "XTPARPAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "CTSP"))
        self.sig_left(ChipSig("-->+", "TPM", 0, 1))
        self.sig_left(ChipSig("-->+", "TSAPER"))
        self.sig_left(ChipSig("-->+", "TSBPER"))
        self.sig_left(ChipSig("-->+", "MARPE"))

        self.sig_left(ChipSig("-->+", "TAGPE"))
        self.sig_left(ChipSig("-->+", "TSAPED"))
        self.sig_left(ChipSig("-->+", "TSBPED"))

        self.sig_right(ChipSig("+-->", "TSP", 0, 1))

        self.sig_right(ChipSig("+-->", "TPD"))
        self.sig_right(ChipSig("+-->", "TGPEY"))
        self.sig_right(ChipSig("+-->", "TSAPE"))
        self.sig_right(ChipSig("+-->", "TSBPE"))
        self.sig_right(ChipSig("+-->", "PERR"))

        self.finish()

def register():
    yield XTPARPAL()


