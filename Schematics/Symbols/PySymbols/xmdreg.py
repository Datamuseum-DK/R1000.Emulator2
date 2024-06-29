#!/usr/bin/env python3

''' MEM Diag Reg '''

from chip import Chip, FChip, ChipSig

class XMDREG(FChip):

    ''' MEM Diag Reg '''

    symbol_name = "XMDREG"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "S", 0, 1))
        self.sig_left(ChipSig("-->+", "QTOE"))
        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_left(ChipSig("-->+", "QCOE"))

        self.sig_right(ChipSig("+<--", "QDGOE"))
        self.sig_right(ChipSig("+<->", "DQDG", 0, 7))

        self.sig_level()
        self.sig_left(ChipSig("<->+", "DQC", 0, 8))

        self.sig_level()
        self.sig_left(ChipSig("<->+", "DQT", 0, 63))
        self.sig_right(ChipSig("+<->", "DQV", 0, 63))

        self.finish()

def register():
    yield XMDREG()


