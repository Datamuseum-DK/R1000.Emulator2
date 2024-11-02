#!/usr/bin/env python3

''' IOC WCS '''

from chip import Chip, FChip, ChipSig

class XIOCWCS(FChip):

    ''' IOC WCS '''

    symbol_name = "XIOCWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SFSTOP"))
        self.sig_left(ChipSig("-->+", "UADR", 0, 13))
        self.sig_left(ChipSig("-->+", "TRAEN"))
        self.sig_left(ChipSig("-->+", "CLKSTP"))
        self.sig_left(ChipSig("-->+", "DUMNXT"))
        self.sig_left(ChipSig("-->+", "ICSAH"))

        self.sig_right(ChipSig("+-->", "UIR", 0, 13))
        self.sig_right(ChipSig("+-->", "DUMEN"))
        self.sig_right(ChipSig("+-->", "CSAHIT"))
        self.sig_right(ChipSig("+-->", "AEN", 0, 3))
        self.sig_right(ChipSig("+-->", "FEN", 0, 3))

        self.finish()

def register():
    yield XIOCWCS()


