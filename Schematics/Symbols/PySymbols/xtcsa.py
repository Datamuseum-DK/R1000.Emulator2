#!/usr/bin/env python3

''' TYP CSA logic '''

from chip import Chip, FChip, ChipSig

class XTCSA(FChip):

    ''' TYP CSA logic '''

    symbol_name = "XTCSA"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "HITOF", 0, 3))
        self.sig_left(ChipSig("-->+", "CSACT", 0, 2))
        self.sig_left(ChipSig("-->+", "CSACLK"))
        self.sig_left(ChipSig("-->+", "UIRSL0"))
        self.sig_left(ChipSig("-->+", "DIAG14"))
        self.sig_left(ChipSig("-->+", "TFPRED"))
        self.sig_left(ChipSig("-->+", "CSAHIT"))

        self.sig_right(ChipSig("+-->", "CSAOF", 0, 3))
        self.sig_right(ChipSig("+-->", "NVE", 0, 3))
        self.sig_right(ChipSig("+-->", "LDTOP"))
        self.sig_right(ChipSig("+-->", "LDBOT"))
        self.sig_right(ChipSig("+-->", "POPDN"))

        self.finish()

def register():
    yield XTCSA()


