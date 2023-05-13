#!/usr/bin/env python3

''' TV A/B/C-adr generation '''

from chip import Chip, FChip, ChipSig

class XCADR(FChip):

    ''' TV A/B/C-adr generation '''

    symbol_name = "XCADR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "CCLK"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "DMODE"))
        self.sig_left(ChipSig("-->+", "DIAG", 0, 3))
        self.sig_left(ChipSig("-->+", "CSDG", 0, 2))
        self.sig_left(ChipSig("-->+", "A", 0, 5))
        self.sig_left(ChipSig("-->+", "B", 0, 5))
        self.sig_left(ChipSig("-->+", "C", 0, 5))

        self.sig_left(ChipSig("-->+", "LBOT"))
        self.sig_left(ChipSig("-->+", "LTOP"))
        self.sig_left(ChipSig("-->+", "LPOP"))
        self.sig_left(ChipSig("-->+", "CSAO", 0, 3))
        self.sig_left(ChipSig("-->+", "LOOP", 0, 9))

        self.sig_left(ChipSig("-->+", "CTL", 0, 5))

        self.sig_right(ChipSig("+-->", "AADR", 0, 9))
        self.sig_right(ChipSig("+-->", "BADR", 0, 9))

        self.sig_right(ChipSig("+<--", "FRM", 0, 4))

        self.sig_right(ChipSig("+<--", "ALOOP"))
        self.sig_right(ChipSig("+<--", "BLOOP"))


        self.finish()

def register():
    yield XCADR()


