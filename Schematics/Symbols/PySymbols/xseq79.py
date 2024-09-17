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
        self.sig_left(ChipSig("-->+", "DUADR"))
        self.sig_left(ChipSig("-->+", "LLMC"))
        self.sig_left(ChipSig("-->+", "BHNT"))
        self.sig_left(ChipSig("-->+", "UEVNT"))

        self.sig_right(ChipSig("+-->", "DGET"))
        self.sig_right(ChipSig("+-->", "ACLK"))
        self.sig_right(ChipSig("+-->", "PCLK"))
        self.sig_right(ChipSig("+-->", "LCLK"))
        self.sig_right(ChipSig("+-->", "BHEN"))

        self.finish(22)

def register():
    yield XSEQ79()


