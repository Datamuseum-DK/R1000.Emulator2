#!/usr/bin/env python3

''' SEQ INT_READS decode '''

from chip import Chip, FChip, ChipSig

class XSREADS(FChip):

    ''' SEQ INT_READS decode '''

    symbol_name = "XSREADS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "IRD", 0, 2))

        self.sig_right(ChipSig("+-->", "PCOE"))
        self.sig_right(ChipSig("+-->", "TVOE"))
        self.sig_right(ChipSig("+-->", "CINOE"))
        self.sig_right(ChipSig("+-->", "DECOE"))
        self.sig_right(ChipSig("+-->", "TOSOE"))
        self.sig_right(ChipSig("+-->", "RNMOE"))
        self.sig_right(ChipSig("+-->", "OFFOE"))
        self.sig_right(ChipSig("+-->", "CNMOE"))

        self.finish()

def register():
    yield XSREADS()


