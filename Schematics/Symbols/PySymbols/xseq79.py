#!/usr/bin/env python3

''' SEQ 79 Clock Generation '''

from chip import Chip, FChip, ChipSig

class XSEQ79(FChip):

    ''' SEQ 79 Clock Generation '''

    symbol_name = "XSEQ79"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "C2EN"))
        self.sig_left(ChipSig("-->+", "H1E"))
        self.sig_left(ChipSig("-->+", "DSTOP"))
        self.sig_left(ChipSig("-->+", "SFSTP"))
        self.sig_left(ChipSig("-->+", "LCLKE"))

        self.sig_right(ChipSig("+-->", "ACLK"))
        self.sig_right(ChipSig("+-->", "LCLK"))

        self.finish(22)

def register():
    yield XSEQ79()


