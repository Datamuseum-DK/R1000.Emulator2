#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class MEM(FChip):

    ''' MEM32 Cache '''

    symbol_name = "MEM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.finish(19)

def register():
    yield MEM()


