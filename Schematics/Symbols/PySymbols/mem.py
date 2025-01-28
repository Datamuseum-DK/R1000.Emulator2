#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class MEM(FChip):

    ''' MEM32 Cache '''

    symbol_name = "MEM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "MCMD", 0, 3))
        self.sig_left(ChipSig("-->+", "CONT"))

        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_left(ChipSig("-->+", "QTOE"))
        self.sig_left(ChipSig("-->+", "QCOE"))

        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "Q4"))

        self.sig_left(ChipSig("-->+", "LDMR"))

        self.sig_left(ChipSig("-->+", "ISLOW"))

        self.sig_left(ChipSig("<--+", "SETA"))
        self.sig_left(ChipSig("<--+", "SETB"))
        self.sig_left(ChipSig("<--+", "HITA"))
        self.sig_left(ChipSig("<--+", "HITB"))

        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "BDISYN"))
        self.sig_left(ChipSig("-->+", "BDIFRZ"))
        self.sig_left(ChipSig("-->+", "MRUI7"))
        self.sig_left(ChipSig("-->+", "EABT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))

        self.sig_right(ChipSig("+<--", "XXX"))

        self.finish(21)

def register():
    yield MEM()


