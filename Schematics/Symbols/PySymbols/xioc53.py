#!/usr/bin/env python3

''' IOC pg 53 '''

from chip import Chip, FChip, ChipSig

class XIOC53(FChip):

    ''' IOC pg 53 '''

    symbol_name = "XIOC53"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TVBS", 0, 3))
        self.sig_left(ChipSig("-->+", "DUMEN"))
        self.sig_left(ChipSig("-->+", "CSAHIT"))
        self.sig_left(ChipSig("-->+", "RAND", 0, 5))
        self.sig_left(ChipSig("-->+", "DIAGLW"))
        self.sig_left(ChipSig("-->+", "SCLKST"))
        self.sig_left(ChipSig("-->+", "RSTRDR"))

        self.sig_left(ChipSig("<--+", "DUMTOE"))
        self.sig_left(ChipSig("<--+", "DUMVOE"))

        self.sig_right(ChipSig("+-->", "SEQTV"))
        self.sig_right(ChipSig("+-->", "FIUV"))
        self.sig_right(ChipSig("+-->", "FIUT"))
        self.sig_right(ChipSig("+-->", "MEMTV"))
        self.sig_right(ChipSig("+-->", "MEMV"))
        self.sig_right(ChipSig("+-->", "IOCTV"))
        self.sig_right(ChipSig("+-->", "VALV"))
        self.sig_right(ChipSig("+-->", "TYPT"))
        self.sig_right(ChipSig("+-->", "R", 0, 16))
        self.sig_right(ChipSig("+-->", "LDWDR"))
        self.sig_right(ChipSig("+-->", "LDDUM"))
        self.sig_right(ChipSig("+-->", "DECC"))
        self.sig_right(ChipSig("+-->", "NCBEN"))
        self.sig_right(ChipSig("+-->", "TRCV"))


        self.finish(22)

def register():
    yield XIOC53()


