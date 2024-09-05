#!/usr/bin/env python3

''' TYP priv-comparator '''

from chip import Chip, FChip, ChipSig

class XPRIVCMP(FChip):

    ''' TYP priv-comparator '''

    symbol_name = "XPRIVCMP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 63))
        self.sig_left(ChipSig("-->+", "OFC"))
        self.sig_left(ChipSig("-->+", "CLIT", 0, 6))
        self.sig_left(ChipSig("-->+", "UCOD", 0, 4))

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "UPVC", 0, 2))
        self.sig_left(ChipSig("-->+", "UEN"))
        self.sig_left(ChipSig("-->+", "SPPRV"))
        self.sig_left(ChipSig("-->+", "SCKEN"))
        self.sig_left(ChipSig("-->+", "DMODE"))

        self.sig_right(ChipSig("+<--", "B", 0, 63))
        self.sig_right(ChipSig("+-->", "NAMES"))
        self.sig_right(ChipSig("+-->", "PATH"))
        self.sig_right(ChipSig("+-->", "AOP"))
        self.sig_right(ChipSig("+-->", "BOP"))
        self.sig_right(ChipSig("+-->", "IOP"))

        self.sig_right(ChipSig("+-->", "OKM"))
        self.sig_right(ChipSig("+-->", "AEQL"))
        self.sig_right(ChipSig("+-->", "AEQB"))
        self.sig_right(ChipSig("+-->", "BEQL"))
        self.sig_right(ChipSig("+-->", "ABLE"))
        self.sig_right(ChipSig("+-->", "PPRIV"))
        self.sig_right(ChipSig("+-->", "UE", 0, 5))

        self.sig_left(ChipSig("<--+", "T0STP"))
        self.sig_left(ChipSig("<--+", "T1STP"))

        self.finish()

def register():
    yield XPRIVCMP()


