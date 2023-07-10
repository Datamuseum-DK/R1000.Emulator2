#!/usr/bin/env python3

''' TYP+VAL B parity '''

from chip import Chip, FChip, ChipSig

class XTVBPAR(FChip):

    ''' TYP+VAL B parity '''

    symbol_name = "XTVBPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q3"))
        self.sig_left(ChipSig("-->+", "BOE"))
        self.sig_left(ChipSig("-->+", "BPAR", 0, 7))
        self.sig_left(ChipSig("-->+", "BADR", 0, 7))
        self.sig_left(ChipSig("-->+", "BCHK", 0, 7))

        self.sig_right(ChipSig("+-->", "TPERR"))

        self.finish()

def register():
    yield XTVBPAR()


