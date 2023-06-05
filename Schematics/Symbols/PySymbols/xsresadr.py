#!/usr/bin/env python3

''' SEQ Resolve address '''

from chip import Chip, FChip, ChipSig

class XSRESADR(FChip):

    ''' SEQ Resolve address '''

    symbol_name = "XSRESADR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLCLK"))
        self.sig_left(ChipSig("-->+", "VAL", 0, 15))
        self.sig_left(ChipSig("-->+", "DISP", 0, 15))
        self.sig_left(ChipSig("-->+", "RASEL", 0, 1))
        self.sig_left(ChipSig("-->+", "LAUIR", 0, 1))
        self.sig_left(ChipSig("-->+", "LINC"))

        self.sig_right(ChipSig("+-->", "RADR", 0, 3))
        self.sig_right(ChipSig("+-->", "CLEX", 0, 3))
        self.sig_right(ChipSig("+-->", "ICOND"))
        self.sig_right(ChipSig("+-->", "SEXT"))

        self.finish(22)

def register():
    yield XSRESADR()


