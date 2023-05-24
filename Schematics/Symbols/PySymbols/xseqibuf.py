#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class XSEQIBUF(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "XSEQIBUF"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TYP", 0, 63))
        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "IBOE", 0, 7))

        self.sig_right(ChipSig("+<--", "VAL", 0, 63))
        self.sig_right(ChipSig("+-->", "DISP", 0, 15))

        self.finish()

def register():
    yield XSEQIBUF()


