#!/usr/bin/env python3

''' SEQ uins decode '''

from chip import Chip, FChip, ChipSig

class XSUDEC(FChip):

    ''' SEQ uins decode '''

    symbol_name = "XSUDEC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "COND"))
        self.sig_left(ChipSig("-->+", "BRTIM", 0, 1))
        self.sig_left(ChipSig("-->+", "BRTYP", 0, 3))
        self.sig_left(ChipSig("-->+", "MEVENT"))
        self.sig_left(ChipSig("-->+", "UEVENT"))

        self.sig_left(ChipSig("-->+", "SCLKE"))

        self.sig_left(ChipSig("-->+", "BHCKE"))
        self.sig_left(ChipSig("-->+", "MPRND"))

        self.sig_left(ChipSig("-->+", "LIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TCLR"))
        self.sig_left(ChipSig("-->+", "RRND", 0, 1))
        self.sig_left(ChipSig("-->+", "MEV"))
        self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "BHEN"))

        self.sig_right(ChipSig("+-->", "UASEL"))

        self.sig_right(ChipSig("+-->", "WDISP"))
        self.sig_right(ChipSig("+-->", "RTN"))
        self.sig_right(ChipSig("+-->", "PUSHBR"))
        self.sig_right(ChipSig("+-->", "PUSH"))

        self.sig_right(ChipSig("+-->", "DTIME"))
        self.sig_right(ChipSig("+-->", "DBHINT"))
        self.sig_right(ChipSig("+-->", "DMDISP"))
        self.sig_right(ChipSig("+-->", "MPCMB"))

        self.sig_right(ChipSig("+-->", "RQ", 0, 3))
        self.sig_right(ChipSig("+-->", "FO7"))
        self.sig_right(ChipSig("+-->", "LDC"))

        self.sig_right(ChipSig("+-->", "BHP"))
        self.sig_right(ChipSig("+-->", "BHN"))

        self.finish()

def register():
    yield XSUDEC()


