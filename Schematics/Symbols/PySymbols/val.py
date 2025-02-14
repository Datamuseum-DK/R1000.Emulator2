#!/usr/bin/env python3

''' VAL C-bus mux '''

from chip import Chip, FChip, ChipSig

class VAL(FChip):

    ''' VAL C-bus mux '''

    symbol_name = "VAL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("===+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "STS"))
        self.sig_left(ChipSig("-->+", "RMS"))
        self.sig_left(ChipSig("-->+", "FREZE"))
        self.sig_left(ChipSig("-->+", "SFS"))


        self.sig_right(ChipSig("+-->", "VCNDA"))
        self.sig_right(ChipSig("+-->", "QBIT"))

        self.finish()

def register():
    yield VAL()


