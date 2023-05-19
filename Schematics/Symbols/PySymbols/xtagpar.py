#!/usr/bin/env python3

''' MEM32 Tag parity '''

from chip import Chip, FChip, ChipSig

class XTAGPAR(FChip):

    ''' MEM32 Tag parity '''

    symbol_name = "XTAGPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TAG", 0, 63))

        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+<--", "OEE"))
        self.sig_right(ChipSig("+<--", "OEL"))
        self.sig_right(ChipSig("+<--", "TS6E"))
        self.sig_right(ChipSig("+<--", "TS6L"))
        self.sig_right(ChipSig("+<--", "TA6E"))
        self.sig_right(ChipSig("+<--", "TA6L"))
        self.sig_right(ChipSig("+<--", "DIAG"))
        self.sig_right(ChipSig("+<--", "TSPR", 0, 1))
        self.sig_right(ChipSig("+<--", "TSMO"))
        self.sig_right(ChipSig("+-->", "PERR"))
        self.sig_right(ChipSig("+-->", "TSPO"))

        self.finish()

def register():
    yield XTAGPAR()


