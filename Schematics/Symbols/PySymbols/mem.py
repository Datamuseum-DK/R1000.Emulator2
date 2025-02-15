#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class MEM(FChip):

    ''' MEM32 Cache '''

    symbol_name = "MEM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "Q4"))

        self.sig_left(ChipSig("<--+", "SETA"))
        self.sig_left(ChipSig("<--+", "SETB"))
        self.sig_left(ChipSig("<--+", "HITA"))
        self.sig_left(ChipSig("<--+", "HITB"))

        self.sig_left(ChipSig("-->+", "EABT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))

        self.sig_right(ChipSig("+<--", "XXX"))

        self.finish(21)

def register():
    yield MEM()


