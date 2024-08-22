#!/usr/bin/env python3

''' Select next UADR '''

from chip import Chip, FChip, ChipSig

class XNXTUADR(FChip):

    ''' Select next UADR '''

    symbol_name = "XNXTUADR"

    def __init__(self):
        super().__init__()
        self.sig_left(ChipSig("-->+", "DV_U"))
        self.sig_left(ChipSig("-->+", "BAD_HINT"))
        self.sig_left(ChipSig("-->+", "LMAC"))
        self.sig_left(ChipSig("-->+", "G_SEL", 0, 1))
        self.sig_left(ChipSig("-->+", "U_MUX_SEL"))
        self.sig_left(ChipSig("-->+", "LCLK"))

        self.sig_left(ChipSig("-->+", "CUR", 0, 13))
        self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("<--+", "U_EVENT"))
        self.sig_left(ChipSig("<--o", "U_EVENT~"))
        self.sig_left(ChipSig("<--o", "MACRO_HIC"))

        self.sig_left(ChipSig("-->+", "LATE", 0, 2))

        self.sig_left(ChipSig("-->+", "UEI", 0, 14))
        self.sig_left(ChipSig("-->+", "ACLK"))

        self.sig_right(ChipSig("+<--", "FIU", 0, 15))
        self.sig_right(ChipSig("+<--", "FIU_CLK"))

        self.sig_right(ChipSig("+<--", "DEC", 0, 12))

        self.sig_right(ChipSig("+<--", "TOP", 0, 13))

        self.sig_right(ChipSig("o<--", "Q1~"))
        self.sig_right(ChipSig("+-->", "NU", 0, 13))

        self.sig_right(ChipSig("+-->", "UEVP"))

        self.finish()

def register():
    yield XNXTUADR()


