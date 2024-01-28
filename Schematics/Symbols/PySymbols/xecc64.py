#!/usr/bin/env python3

''' 128 bit ECC generator '''

from chip import Chip, FChip, ChipSig

class XECC(FChip):

    ''' ECC calculation '''

    symbol_name = "XECC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<--+", "PT", 0, 7))
        self.sig_left(ChipSig("-->+", "T", 0, 63))
        self.sig_left(ChipSig("-->+", "CBI", 0, 8))
        self.sig_left(ChipSig("-->+", "GEN"))
        self.sig_left(ChipSig("-->+", "CLK"))

        self.sig_right(ChipSig("+-->", "PV", 0, 7))
        self.sig_right(ChipSig("+<--", "V", 0, 63))
        self.sig_right(ChipSig("+-->", "CBO", 0, 8))
        self.sig_right(ChipSig("+-->", "ERR"))

        self.finish()

def register():
    yield XECC()
