#!/usr/bin/env python3

''' 128 bit ECC generator '''

from chip import Chip, FChip, ChipSig

class XECC(FChip):

    ''' ECC calculation '''

    symbol_name = "XECC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "T", 0, 63))
        self.sig_left(ChipSig("<->+", "DQC", 0, 8))
        self.sig_left(ChipSig("-->+", "QCOE"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "TVEN"))
        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_right(ChipSig("+<--", "V", 0, 63))
        self.sig_right(ChipSig("+-->", "ERR"))
        self.sig_right(ChipSig("+-->", "CBER"))
        self.sig_right(ChipSig("+-->", "MBER"))
        self.sig_right(ChipSig("+===", "QT", 0, 15))

        self.finish()

def register():
    yield XECC()
