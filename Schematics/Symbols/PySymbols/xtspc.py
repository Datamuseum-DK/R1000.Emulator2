#!/usr/bin/env python3

''' TYP Spc '''

from chip import Chip, FChip, ChipSig

class XTSPC(FChip):
    ''' TYP Spc '''

    symbol_name = "XTSPC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "MARCTL", 0, 3))
        self.sig_left(ChipSig("-->+", "FSP"))
        self.sig_left(ChipSig("-->+", "B", 0, 2))
        self.sig_left(ChipSig("-->+", "TAEN"))
        self.sig_left(ChipSig("-->+", "VAEN"))
        self.sig_left(ChipSig("-->+", "DON"))
        self.sig_left(ChipSig("-->+", "DOFF"))

        self.sig_right(ChipSig("+-->", "PARE"))
        self.sig_right(ChipSig("+<--", "PAROE"))
        self.sig_right(ChipSig("+===", "PAR"))
        self.sig_right(ChipSig("+-->", "ASPE"))
        self.sig_right(ChipSig("+<--", "ASPOE"))
        self.sig_right(ChipSig("+===", "ASP", 0, 2))

        self.finish()

def register():
    yield XTSPC()


