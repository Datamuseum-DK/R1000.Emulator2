#!/usr/bin/env python3

''' FIU A-bus parity '''

from chip import Chip, FChip, ChipSig

class XFAPAR(FChip):

    ''' FIU A-bus parity '''

    symbol_name = "XFAPAR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "B", 0, 7))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "CKP"))
        self.sig_left(ChipSig("-->+", "FAE"))
        self.sig_left(ChipSig("-->+", "IO2"))
        self.sig_left(ChipSig("-->+", "MSP", 0, 2))
        self.sig_left(ChipSig("-->+", "CKPN"))

        self.sig_left(ChipSig("-->+", "CKCTP"))
        self.sig_left(ChipSig("-->+", "CTP", 0, 7))

        self.sig_right(ChipSig("+-->", "AERR"))
        self.sig_right(ChipSig("+===", "DQP", 0, 8))
        self.sig_right(ChipSig("+-->", "MOE"))
        self.sig_right(ChipSig("+<--", "QPOE"))

        self.finish()

def register():
    yield XFAPAR()


