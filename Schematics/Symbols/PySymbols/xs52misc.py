#!/usr/bin/env python3

''' SEQ 52 MISC '''

from chip import Chip, FChip, ChipSig

class XS52MISC(FChip):

    ''' SEQ 52 MISC '''

    symbol_name = "XS52MISC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))

        self.sig_left(ChipSig("-->+", "SCKEN"))
        self.sig_left(ChipSig("-->+", "LIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TCLR"))
        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "RRND", 0, 1))
        self.sig_left(ChipSig("-->+", "MEV"))
        self.sig_left(ChipSig("-->+", "COND"))
        self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "BHEN"))
        self.sig_left(ChipSig("-->+", "BHIN2"))

        self.sig_right(ChipSig("+-->", "RQ", 0, 3))
        self.sig_right(ChipSig("+-->", "LQ", 0, 3))
        self.sig_right(ChipSig("+-->", "LQN"))
        self.sig_right(ChipSig("+-->", "FO7"))
        self.sig_right(ChipSig("+-->", "LCP"))
        self.sig_right(ChipSig("+-->", "LCN"))
        self.sig_right(ChipSig("+-->", "LDC"))

        self.finish()

def register():
    yield XS52MISC()


