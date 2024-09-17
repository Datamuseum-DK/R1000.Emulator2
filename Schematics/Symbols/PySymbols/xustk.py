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


        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_left(ChipSig("===+", "QV", 0, 15))
        self.sig_left(ChipSig("-->+", "LCLK"))

        self.sig_left(ChipSig("-->+", "PUSH"))
        self.sig_left(ChipSig("-->+", "PUSHBR"))
        self.sig_left(ChipSig("-->+", "BADHINT"))
        self.sig_left(ChipSig("-->+", "PUSHRND"))
        self.sig_left(ChipSig("-->+", "RETURN"))
        self.sig_left(ChipSig("-->+", "POPRND"))

        
        self.sig_right(ChipSig("+-->", "SVLAT"))
        self.sig_right(ChipSig("+<--", "CSR"))
        self.sig_right(ChipSig("+<--", "STOP"))
        self.sig_right(ChipSig("+-->", "SSZ"))

        self.sig_right(ChipSig("+<--", "QFOE"))
        self.sig_right(ChipSig("+===", "DQF", 0, 63))

        ####### 

        self.sig_left(ChipSig("-->+", "DV_U"))
        self.sig_left(ChipSig("-->+", "BAD_HINT"))
        self.sig_left(ChipSig("-->+", "LMAC"))
        self.sig_left(ChipSig("-->+", "G_SEL", 0, 1))
        self.sig_left(ChipSig("-->+", "U_MUX_SEL"))

        self.sig_left(ChipSig("-->+", "CUR", 0, 13))
        self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("<--+", "U_EVENT"))
        self.sig_left(ChipSig("<--o", "U_EVENT~"))
        self.sig_left(ChipSig("<--o", "MACRO_HIC"))

        self.sig_left(ChipSig("-->+", "LATE", 0, 2))

        self.sig_left(ChipSig("-->+", "UEI", 0, 14))
        self.sig_left(ChipSig("-->+", "ACLK"))

        self.sig_right(ChipSig("+<--", "FIU_CLK"))

        self.sig_right(ChipSig("+<--", "DEC", 0, 12))

        self.sig_right(ChipSig("o<--", "Q1~"))
        self.sig_right(ChipSig("+-->", "NU", 0, 13))

        self.sig_right(ChipSig("+-->", "UEVP"))

        self.finish()

def register():
    yield XUSTK()


