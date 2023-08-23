#!/usr/bin/env python3

''' TYP conditions '''

from chip import Chip, FChip, ChipSig

class XTCOND(FChip):

    ''' TYP conditions '''

    symbol_name = "XTCOND"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SEL", 0, 6))
        self.sig_left(ChipSig("-->+", "CCLK"))
        self.sig_left(ChipSig("-->+", "SCLK"))

        self.sig_left(ChipSig("-->+", "ISBIN"))
        self.sig_left(ChipSig("-->+", "C0H"))

        self.sig_left(ChipSig("-->+", "C1A"))
        self.sig_left(ChipSig("-->+", "OVREN"))
        self.sig_left(ChipSig("-->+", "C1C"))
        self.sig_left(ChipSig("-->+", "ABIT0"))
        self.sig_left(ChipSig("-->+", "SELA"))

        self.sig_left(ChipSig("-->+", "C2A"))
        self.sig_left(ChipSig("-->+", "C2B"))
        self.sig_left(ChipSig("-->+", "C2C"))
        self.sig_left(ChipSig("-->+", "C2D"))
        self.sig_left(ChipSig("-->+", "C2E"))
        self.sig_left(ChipSig("-->+", "C2F"))
        self.sig_left(ChipSig("-->+", "C2G"))
        self.sig_left(ChipSig("-->+", "C2H"))

        self.sig_left(ChipSig("-->+", "C3A"))
        self.sig_left(ChipSig("-->+", "C3B"))
        self.sig_left(ChipSig("-->+", "C3C"))
        self.sig_left(ChipSig("-->+", "C3D"))
        self.sig_left(ChipSig("-->+", "C3E"))

        self.sig_left(ChipSig("-->+", "BBIT", 0, 6))

        self.sig_right(ChipSig("+-->", "VCOND", 0, 4))
        self.sig_right(ChipSig("+-->", "LVCND"))

        self.sig_right(ChipSig("+<--", "LOOP", 0, 9))
        self.sig_right(ChipSig("+<--", "ALUZ", 0, 7))

        self.finish()

def register():
    yield XTCOND()


