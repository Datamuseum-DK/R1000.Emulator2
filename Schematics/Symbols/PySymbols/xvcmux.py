#!/usr/bin/env python3

''' VAL C-bus mux '''

from chip import Chip, FChip, ChipSig

class XVCMUX(FChip):

    ''' VAL C-bus mux '''

    symbol_name = "XVCMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "FIU", 0, 63))
        self.sig_left(ChipSig("-->+", "ALU", 0, 63))
        self.sig_left(ChipSig("-->+", "SEL10"))
        self.sig_left(ChipSig("-->+", "OE00"))
        self.sig_left(ChipSig("-->+", "OE01"))
        self.sig_left(ChipSig("-->+", "OE10"))
        self.sig_left(ChipSig("-->+", "OE11"))
        self.sig_left(ChipSig("-->+", "FOE0"))
        self.sig_left(ChipSig("-->+", "FOE1"))

        self.sig_right(ChipSig("+===", "C", 0, 63))
        self.sig_right(ChipSig("+<--", "WDR", 0, 63))
        self.sig_right(ChipSig("+<--", "COND"))
        self.sig_right(ChipSig("+<--", "CSEL", 0, 2))
        self.sig_right(ChipSig("+<--", "OE"))

        self.finish()

def register():
    yield XVCMUX()


