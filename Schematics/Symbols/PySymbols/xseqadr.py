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
        self.sig_left(ChipSig("-->+", "RAMCS"))
        self.sig_left(ChipSig("-->+", "RADR", 0, 3))
        self.sig_left(ChipSig("-->+", "TOSCLK"))
        self.sig_left(ChipSig("-->+", "ADRICD"))


        self.sig_right(ChipSig("+<--", "SEQAE"))
        self.sig_right(ChipSig("+<--", "DADOF"))
        self.sig_right(ChipSig("+<--", "DADON"))
        self.sig_right(ChipSig("+-->", "NSPOE"))
        self.sig_right(ChipSig("+-->", "APAROE"))
        self.sig_right(ChipSig("+<--", "TYPOE"))
        self.sig_right(ChipSig("+<--", "VALOE"))

        self.sig_level()
        self.sig_right(ChipSig("+<--", "OSPCOE"))
        self.sig_level()
        self.sig_left(ChipSig("-->+", "ISPC", 0, 2))
        self.sig_right(ChipSig("+===", "OSPC", 0, 2))

        self.sig_level()
        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_right(ChipSig("+<--", "ADRNOE"))
        self.sig_level()
        self.sig_left(ChipSig("<->+", "DQV", 0, 31))
        self.sig_right(ChipSig("+===", "ADRN", 0, 31))

        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+===", "DQT", 0, 31))

        self.sig_left(ChipSig("-->+", "MCLK"))
        self.sig_left(ChipSig("-->+", "RCLK"))
        self.sig_left(ChipSig("-->+", "CSEL"))
        self.sig_left(ChipSig("-->+", "CNCK"))
        self.sig_left(ChipSig("-->+", "CNOE"))
        self.finish()

def register():
    yield XSEQNAM()


