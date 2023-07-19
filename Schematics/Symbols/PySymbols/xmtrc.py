#!/usr/bin/env python3

''' MEM32 Tracing '''

from chip import Chip, FChip, ChipSig

class XMTRC(FChip):

    ''' MEM32 Tracing '''

    symbol_name = "XMTRC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))

        self.sig_left(ChipSig("-->+", "IA", 0, 7))
        self.sig_left(ChipSig("-->o", "IAE0"))
        self.sig_left(ChipSig("-->+", "IAE1"))

        self.sig_left(ChipSig("-->+", "IB", 0, 7))
        self.sig_left(ChipSig("-->o", "IBE0"))
        self.sig_left(ChipSig("-->o", "IBE1"))

        self.sig_left(ChipSig("-->+", "IC", 0, 7))
        self.sig_left(ChipSig("-->o", "ICE0"))
        self.sig_left(ChipSig("-->o", "ICE1"))

        self.sig_left(ChipSig("-->+", "ID", 0, 7))
        self.sig_left(ChipSig("-->+", "IDE"))

        self.sig_left(ChipSig("-->+", "A", 0, 13))
        self.sig_left(ChipSig("-->+", "WE"))

        self.sig_right(ChipSig("+-->", "Q", 0, 7))

        self.finish()

def register():
    yield XMTRC()


