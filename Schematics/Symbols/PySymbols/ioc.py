#!/usr/bin/env python3

''' IOC Dummy register '''

from chip import Chip, FChip, ChipSig

class IOC(FChip):

    ''' IOC Dummy register '''

    symbol_name = "IOC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "QTYPOE"))


        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "CSTP"))

        self.sig_left(ChipSig("-->o", "RESET"))

        self.sig_left(ChipSig("-->+", "RTCEN"))

        self.sig_left(ChipSig("-->+", "SCLKST"))
        self.sig_left(ChipSig("-->+", "RSTRDR"))

        self.sig_left(ChipSig("-->+", "TRAEN"))
        
        self.sig_left(ChipSig("-->+", "DUMNXT"))

        self.sig_right(ChipSig("+<--", "QVALOE"))

        self.sig_right(ChipSig("+-->", "RSPEMN"))


        self.sig_right(ChipSig("+-->", "SME"))
        self.sig_right(ChipSig("+-->", "DME"))

        self.sig_right(ChipSig("+-->", "BLTCP"))

        self.sig_right(ChipSig("+-->", "FEN", 0, 3))
        self.sig_right(ChipSig("+-->", "SEQTV"))
        self.sig_right(ChipSig("+-->", "FIUV"))
        self.sig_right(ChipSig("+-->", "FIUT"))
        self.sig_right(ChipSig("+-->", "MEMTV"))
        self.sig_right(ChipSig("+-->", "MEMV"))
        self.sig_right(ChipSig("+-->", "VALV"))
        self.sig_right(ChipSig("+-->", "TYPT"))
        self.sig_right(ChipSig("+-->", "IOCTV"))

        self.finish()

def register():
    yield IOC()
