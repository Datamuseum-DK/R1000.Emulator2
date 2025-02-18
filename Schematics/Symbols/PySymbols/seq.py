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
        self.sig_left(ChipSig("-->+", "STOP", 0, 2))
        self.sig_left(ChipSig("-->+", "CSAWR"))
        self.sig_left(ChipSig("-->+", "BLTCP"))

        self.sig_right(ChipSig("+-->", "QSTP7"))

        self.sig_right(ChipSig("+-->", "QDFRZ"))
        self.sig_right(ChipSig("+-->", "SEQST"))

        self.sig_right(ChipSig("+-->", "SFSTPO"))
        self.sig_right(ChipSig("+-->", "FREEZ"))
        self.sig_right(ChipSig("+-->", "RAMRUN"))
        self.sig_right(ChipSig("+-->", "CLKRUN"))
        self.sig_right(ChipSig("+-->", "ICLK"))
        self.sig_right(ChipSig("+-->", "SCLKE"))

        self.finish()

def register():
    yield SEQ()

