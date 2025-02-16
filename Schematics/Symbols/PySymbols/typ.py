#!/usr/bin/env python3

''' TYP C-bus mux '''

from chip import Chip, FChip, ChipSig

class TYP(FChip):

    ''' TYP C-bus mux '''

    symbol_name = "TYP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))

        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "TQBIT"))
        self.sig_left(ChipSig("-->+", "BHSTP"))
        self.sig_left(ChipSig("-->+", "STS"))
        self.sig_left(ChipSig("-->+", "RMS"))
        self.sig_left(ChipSig("-->+", "FREZE"))
        self.sig_left(ChipSig("-->+", "SFS"))

        self.sig_right(ChipSig("+-->", "CWE"))
        self.sig_right(ChipSig("+-->", "T0STP"))
        self.sig_right(ChipSig("+-->", "T1STP"))

        self.finish()

def register():
    yield TYP()


