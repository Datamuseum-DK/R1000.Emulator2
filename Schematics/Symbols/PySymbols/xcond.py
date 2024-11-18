#!/usr/bin/env python3

''' SEQ Condition Select '''

from chip import Chip, FChip, ChipSig

class XCOND(FChip):

    ''' SEQ Condition Select '''

    symbol_name = "XCOND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "ICOND", 0, 6))
        self.sig_left(ChipSig("-->+", "CX0"))
        self.sig_left(ChipSig("-->+", "CX1"))
        self.sig_left(ChipSig("-->+", "CX2"))
        self.sig_left(ChipSig("-->+", "CX3"))
        self.sig_left(ChipSig("-->+", "CX4"))
        self.sig_left(ChipSig("-->+", "CX5"))
        self.sig_left(ChipSig("-->+", "CX6"))
        self.sig_left(ChipSig("-->+", "CX7"))
        self.sig_left(ChipSig("-->+", "CX8"))
        self.sig_left(ChipSig("-->+", "CX9"))
        self.sig_left(ChipSig("-->+", "CXA"))
        self.sig_left(ChipSig("-->+", "CXB"))
        self.sig_left(ChipSig("-->+", "CXC"))
        self.sig_left(ChipSig("-->+", "CXD"))
        self.sig_left(ChipSig("-->+", "CXE"))
        self.sig_left(ChipSig("-->+", "CXF"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SCKE"))
        # self.sig_left(ChipSig("-->+", "SC", 0, 23))

        self.sig_right(ChipSig("+-->", "E_ML"))
        self.sig_right(ChipSig("+-->", "CNDP"))
        self.sig_right(ChipSig("+-->", "CQ3P"))
        self.sig_right(ChipSig("+-->", "CQ3N"))

        self.finish()

def register():
    yield XCOND()


