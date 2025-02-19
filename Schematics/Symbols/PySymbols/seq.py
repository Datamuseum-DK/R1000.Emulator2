#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class SEQ(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "SEQ"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->+", "SFSTP"))

        self.sig_left(ChipSig("-->+", "DIAG", 0, 2))

        self.sig_right(ChipSig("+-->", "QDFRZ"))

        self.sig_right(ChipSig("+-->", "SFSTPO"))

        self.finish()

def register():
    yield SEQ()

