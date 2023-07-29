#!/usr/bin/env python3

''' FIU Writable Control Store '''

from chip import Chip, FChip, ChipSig

class XFIUWCS(FChip):

    ''' FIU Writable Control Store '''

    symbol_name = "XFIUWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "UCLK"))
        self.sig_left(ChipSig("-->+", "CKEN"))
        self.sig_left(ChipSig("-->+", "SFST"))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "UAC", 0, 15))
        self.sig_left(ChipSig("-->+", "UAD", 0, 15))
        self.sig_left(ChipSig("-->+", "DUAS"))
        self.sig_left(ChipSig("-->+", "MODE"))
        self.sig_left(ChipSig("-->+", "SUIR"))
        self.sig_left(ChipSig("-->+", "DGI", 0, 7))

        self.sig_right(ChipSig("+-->", "UIR", 0, 47))
        self.sig_right(ChipSig("+===", "DGO", 0, 7))
        self.sig_right(ChipSig("+-->", "UPER"))
        self.sig_right(ChipSig("+-->", "APER"))

        self.finish()

def register():
    yield XFIUWCS()


