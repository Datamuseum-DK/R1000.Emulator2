#!/usr/bin/env python3

''' IOC pg 53 '''

from chip import Chip, FChip, ChipSig

class XIOC53(FChip):

    ''' IOC pg 53 '''

    symbol_name = "XIOC53"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "UIR", 0, 7))
        self.sig_left(ChipSig("-->+", "DUMEN"))
        self.sig_left(ChipSig("-->+", "CSAHIT"))
        self.sig_left(ChipSig("-->+", "DIAGON"))
        self.sig_left(ChipSig("-->+", "DIAGOFF"))

        self.sig_right(ChipSig("+-->", "ADR", 0, 3))
        self.sig_right(ChipSig("+-->", "FIU", 0, 3))
        self.sig_right(ChipSig("+-->", "SEQTV"))
        self.sig_right(ChipSig("+-->", "FIUV"))
        self.sig_right(ChipSig("+-->", "FIUT"))
        self.sig_right(ChipSig("+-->", "RDDUM"))
        self.sig_right(ChipSig("+-->", "MEMTV"))
        self.sig_right(ChipSig("+-->", "MEMV"))
        self.sig_right(ChipSig("+-->", "IOCTV"))
        self.sig_right(ChipSig("+-->", "VALV"))
        self.sig_right(ChipSig("+-->", "TYPT"))


        self.finish(22)

def register():
    yield XIOC53()


