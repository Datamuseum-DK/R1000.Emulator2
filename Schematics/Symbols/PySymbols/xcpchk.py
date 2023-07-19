#!/usr/bin/env python3

''' Clocked parity checker '''

from chip import Chip, FChip, ChipSig

class XCPCHK(FChip):

    ''' Clocked parity checker '''

    symbol_name = "XCPCHK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "A", 0, 7))
        self.sig_left(ChipSig("-->o", "ENA"))
        
        self.sig_right(ChipSig("+-->", "ERR"))
        self.sig_right(ChipSig("+<--", "B", 0, 7))
        self.sig_right(ChipSig("o<--", "INV"))

        self.finish()

def register():
    yield XCPCHK()


