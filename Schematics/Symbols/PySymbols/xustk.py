#!/usr/bin/env python3

''' Micro Stack '''

from chip import Chip, FChip, ChipSig

class XUSTK(FChip):

    ''' Micro Stack '''

    symbol_name = "XUSTK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "STKEN"))

        self.sig_left(ChipSig("-->+", "Q3COND"))
        self.sig_left(ChipSig("-->+", "LATCHED"))

        self.sig_left(ChipSig("-->+", "CURU", 0, 13))

        self.sig_left(ChipSig("-->+", "BRNCH", 0, 13))

        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_left(ChipSig("===+", "QV", 0, 15))
        self.sig_left(ChipSig("-->+", "QPOE"))
        self.sig_left(ChipSig("===+", "DQP", 0, 7))
        self.sig_left(ChipSig("-->+", "LCLK"))
        self.sig_left(ChipSig("<--+", "PERR"))

        self.sig_left(ChipSig("-->+", "PUSH"))
        self.sig_left(ChipSig("-->+", "UEVENT"))
        self.sig_left(ChipSig("-->+", "PUSHBR"))
        self.sig_left(ChipSig("-->+", "BADHINT"))
        self.sig_left(ChipSig("-->+", "PUSHRND"))
        self.sig_left(ChipSig("-->+", "RETURN"))
        self.sig_left(ChipSig("-->+", "POPRND"))

        
        self.sig_right(ChipSig("+-->", "TOPU", 0, 15))
        self.sig_right(ChipSig("+<--", "CSR"))
        self.sig_right(ChipSig("+<--", "STOP"))
        self.sig_right(ChipSig("+-->", "SSZ"))

        self.sig_right(ChipSig("+<--", "QFOE"))
        self.sig_right(ChipSig("+===", "DQF", 0, 63))

        self.finish()

def register():
    yield XUSTK()


