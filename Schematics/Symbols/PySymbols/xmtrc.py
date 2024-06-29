#!/usr/bin/env python3

''' MEM32 Tracing '''

from chip import Chip, FChip, ChipSig

class XMTRC(FChip):

    ''' MEM32 Tracing '''

    symbol_name = "XMTRC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLKQ2"))
        self.sig_left(ChipSig("-->+", "CLKQ4"))

        self.sig_left(ChipSig("-->+", "IA", 0, 7))

        self.sig_left(ChipSig("-->o", "IBE0"))

        self.sig_left(ChipSig("-->+", "IC", 0, 7))
        self.sig_left(ChipSig("-->o", "ICE0"))
        self.sig_left(ChipSig("-->o", "ICE1"))

        self.sig_left(ChipSig("-->+", "ID", 0, 7))
        self.sig_left(ChipSig("-->+", "IDE"))

        self.sig_left(ChipSig("-->+", "MODE", 0, 3))
        self.sig_left(ChipSig("-->+", "DIR"))
        self.sig_left(ChipSig("-->+", "ADIR"))
        self.sig_left(ChipSig("-->+", "RFSH"))
        self.sig_left(ChipSig("-->+", "C8LD"))

        self.sig_left(ChipSig("-->+", "TSCEN"))
        self.sig_left(ChipSig("-->+", "ROWE"))
        self.sig_left(ChipSig("-->+", "ROW", 0, 7))
        self.sig_left(ChipSig("-->+", "COLE"))
        self.sig_left(ChipSig("-->+", "COL", 0, 7))
        self.sig_left(ChipSig("-->+", "DCNT", 0, 4))

        self.sig_right(ChipSig("+-->", "Q", 0, 7))
        self.sig_right(ChipSig("+===", "QDIAG", 0, 7))
        self.sig_right(ChipSig("+-->", "TQB", 0, 7))
        self.sig_right(ChipSig("+-->", "DR", 3, 10))
        self.sig_right(ChipSig("+-->", "TSTR", 0, 15))
        self.sig_right(ChipSig("+-->", "TA3"))
        self.sig_right(ChipSig("+-->", "OVFO"))
        self.sig_right(ChipSig("+-->", "TRADR", 0, 3))

        self.finish()

def register():
    yield XMTRC()


