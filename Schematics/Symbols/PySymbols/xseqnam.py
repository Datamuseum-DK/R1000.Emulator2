#!/usr/bin/env python3

''' SEQ name + offset generation '''

from chip import Chip, FChip, ChipSig

class XSEQNAM(FChip):

    ''' SEQ name generation '''

    symbol_name = "XSEQNAM"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "RAMWE"))
        self.sig_left(ChipSig("-->+", "RSAD", 0, 3))
        self.sig_left(ChipSig("-->+", "TOSCLK"))
        self.sig_left(ChipSig("-->+", "ADRICD"))

        self.sig_left(ChipSig("-->+", "ISPC", 0, 2))
        self.sig_left(ChipSig("-->+", "QVAOE"))
        self.sig_left(ChipSig("<->+", "DQVA", 0, 31))

        self.sig_left(ChipSig("-->+", "MCLK"))
        self.sig_left(ChipSig("-->+", "RTCLK"))
        self.sig_left(ChipSig("-->+", "CSEL"))
        self.sig_left(ChipSig("-->+", "CNCK"))
        self.sig_left(ChipSig("-->+", "CNOE"))

        self.sig_left(ChipSig("-->+", "MD"))
        self.sig_left(ChipSig("-->+", "MSD", 0, 2))
        self.sig_left(ChipSig("-->+", "UTOS"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "IRDS", 1, 2))
        self.sig_left(ChipSig("-->+", "TOSS"))
        self.sig_left(ChipSig("-->+", "RWE"))

        self.sig_left(ChipSig("-->+", "SGEXT"))
        self.sig_left(ChipSig("-->+", "DSPL", 0, 15))
        self.sig_left(ChipSig("-->+", "CTL", 0, 2))
        self.sig_left(ChipSig("-->+", "CMR"))
        self.sig_left(ChipSig("-->+", "FIU", 0, 31))
        self.sig_left(ChipSig("-->+", "SVCLK"))
        self.sig_left(ChipSig("-->+", "PDCLK"))
        self.sig_left(ChipSig("-->+", "STCLK"))
        self.sig_left(ChipSig("-->+", "TOPLD"))

        self.sig_left(ChipSig("-->+", "CSA", 0, 3))
        self.sig_left(ChipSig("-->+", "RESDR"))
        self.sig_left(ChipSig("-->+", "BRNC", 0, 2))
        self.sig_left(ChipSig("-->+", "CODE", 0, 11))

        self.sig_right(ChipSig("+<--", "OSPCOE"))
        self.sig_right(ChipSig("+===", "OSPC", 0, 2))
        self.sig_right(ChipSig("+<--", "ADRNOE"))
        self.sig_right(ChipSig("+===", "ADRN", 0, 31))
        self.sig_right(ChipSig("+<--", "NAMOE"))
        self.sig_right(ChipSig("+===", "NAM", 0, 31))

        self.sig_right(ChipSig("+<--", "QTHOE"))
        self.sig_right(ChipSig("+===", "DQTH", 0, 31))

        self.sig_right(ChipSig("+<--", "QTLOE"))
        self.sig_right(ChipSig("+<->", "DQTL", 0, 31))

        self.sig_right(ChipSig("+-->", "COUT"))

        self.finish()

def register():
    yield XSEQNAM()


