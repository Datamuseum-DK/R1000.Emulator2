#!/usr/bin/env python3

''' MEM32 pg 31 '''

from chip import Chip, FChip, ChipSig

class XM31(FChip):

    ''' MEM32 pg 31 '''

    symbol_name = "XM31"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "CMDE"))
        self.sig_left(ChipSig("-->+", "SEL"))
        self.sig_left(ChipSig("-->+", "MCMD", 0, 3))
        self.sig_left(ChipSig("-->+", "CONT"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "TRACE", 0, 7))
        self.sig_left(ChipSig("-->+", "BDISYN"))
        self.sig_left(ChipSig("-->+", "BDIFRZ"))
        self.sig_left(ChipSig("-->+", "DLWDR"))
        self.sig_left(ChipSig("-->+", "DENLW"))

        self.sig_right(ChipSig("+-->", "TMP", 0, 5))
        self.sig_right(ChipSig("+-->", "TLWDR"))
        self.sig_right(ChipSig("o-->", "CSTOP"))
        self.sig_right(ChipSig("o-->", "DSYNC"))
        self.sig_right(ChipSig("o-->", "DFRZE"))

        self.finish()

def register():
    yield XM31()


