#!/usr/bin/env python3

''' SEQ Macro Event resolver '''

from chip import Chip, FChip, ChipSig

class XSMEV(FChip):

    ''' SEQ Condition Select '''

    symbol_name = "XSMEV"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "MDISP"))
        self.sig_left(ChipSig("-->+", "EMP"))
        self.sig_left(ChipSig("-->+", "LMP", 0, 7))

        #self.sig_left(ChipSig("-->+", "MUFLO"))
        #self.sig_left(ChipSig("-->+", "MOFLO"))
        #self.sig_left(ChipSig("-->+", "SSTOP"))
        #self.sig_left(ChipSig("-->+", "DISP0"))
        #self.sig_left(ChipSig("-->+", "LVKDC"))
        #self.sig_left(ChipSig("-->+", "UTOSD"))
        #self.sig_left(ChipSig("-->+", "TVLDC"))

        self.sig_right(ChipSig("+-->", "MEVL"))
        self.sig_right(ChipSig("+-->", "MEVH"))
        self.sig_right(ChipSig("+-->", "LMAC"))
        self.sig_right(ChipSig("+-->", "DISP"))
        self.sig_right(ChipSig("+-->", "LMU", 0, 2))
        self.sig_right(ChipSig("+-->", "MIBF"))

        self.finish()

def register():
    yield XSMEV()


