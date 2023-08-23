#!/usr/bin/env python3

''' SEQ offset generation '''

from chip import Chip, FChip, ChipSig

class XSEQOFS(FChip):

    ''' SEQ offset generation '''

    symbol_name = "XSEQOFS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RESDR"))
        self.sig_left(ChipSig("-->+", "ADRIC"))
        self.sig_left(ChipSig("-->+", "RES", 0, 19))
        self.sig_left(ChipSig("-->+", "CODE", 0, 11))
        self.sig_left(ChipSig("-->+", "OFFS", 0, 19))
        self.sig_left(ChipSig("-->+", "BRNC", 0, 2))

        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+-->", "ADR", 0, 31))
        self.sig_right(ChipSig("+-->", "PAR", 0, 3))

        self.finish()

def register():
    yield XSEQOFS()


