#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class XCACHE(FChip):

    ''' MEM32 Cache '''

    symbol_name = "XCACHE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DQV", 0, 63))
        self.sig_left(ChipSig("-->+", "SPC", 0, 2))
        self.sig_left(ChipSig("-->+", "ADR", 0, 56))

        self.sig_left(ChipSig("-->+", "MCMD", 0, 3))
        self.sig_left(ChipSig("-->+", "CONT"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "BDISYN"))
        self.sig_left(ChipSig("-->+", "BDIFRZ"))
        self.sig_left(ChipSig("-->+", "MRUI7"))
        self.sig_left(ChipSig("-->+", "EABT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))
        self.sig_left(ChipSig("-->+", "TVDRV"))
        self.sig_left(ChipSig("-->+", "VDRV"))

        self.sig_right(ChipSig("+<->", "DQT", 0, 63))
        self.sig_right(ChipSig("+<->", "DQC", 0, 8))

        self.sig_right(ChipSig("+-->", "QVDR"))
        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+-->", "QTDR"))
        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+<--", "QCOE"))

        self.sig_right(ChipSig("+<--", "CLK"))

        self.sig_right(ChipSig("+<--", "H1"))
        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "LDMR"))

        self.sig_right(ChipSig("+<--", "ISLOW"))
        self.sig_right(ChipSig("+<--", "Q2"))


        self.sig_right(ChipSig("+-->", "SETA"))
        self.sig_right(ChipSig("+-->", "SETB"))
        self.sig_right(ChipSig("+-->", "HITA"))
        self.sig_right(ChipSig("+-->", "HITB"))

        self.finish(21)

def register():
    yield XCACHE()


