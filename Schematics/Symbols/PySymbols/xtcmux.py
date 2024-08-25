#!/usr/bin/env python3

''' TYP C-bus mux '''

from chip import Chip, FChip, ChipSig

class XTCMUX(FChip):

    ''' TYP C-bus mux '''

    symbol_name = "XTCMUX"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "FIU", 0, 63))
        self.sig_left(ChipSig("-->+", "DTY", 0, 63))
        self.sig_left(ChipSig("-->+", "SEL"))
        #self.sig_left(ChipSig("-->+", "MOE0"))
        #self.sig_left(ChipSig("-->+", "MOE1"))
        #self.sig_left(ChipSig("-->+", "FOE0"))
        #self.sig_left(ChipSig("-->+", "FOE1"))
        self.sig_left(ChipSig("-->+", "CSRC"))
        self.sig_left(ChipSig("-->+", "CSPL"))
        self.sig_left(ChipSig("-->+", "DGCM"))
        self.sig_left(ChipSig("-->+", "A", 0, 9))

        self.sig_right(ChipSig("+-->", "C", 0, 63))
        self.sig_right(ChipSig("+<--", "ALU", 0, 63))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "WE"))
        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+<--", "LDWDR"))
        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "SCLKE"))

        self.finish()

def register():
    yield XTCMUX()


