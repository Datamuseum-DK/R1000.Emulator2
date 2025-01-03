#!/usr/bin/env python3

''' IOC Dummy register '''

from chip import Chip, FChip, ChipSig

class IOC(FChip):

    ''' IOC Dummy register '''

    symbol_name = "IOC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQTYP", 0, 63))
        self.sig_left(ChipSig("-->+", "QTYPOE"))


        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "TVEN"))
        self.sig_left(ChipSig("-->+", "CSTP"))

        self.sig_left(ChipSig("-->o", "RESET"))

        self.sig_left(ChipSig("-->+", "EXTID", 0, 2))
        self.sig_left(ChipSig("-->+", "KEY"))

        self.sig_left(ChipSig("-->+", "RTCEN"))

        self.sig_left(ChipSig("-->+", "TVBS", 0, 3))
        self.sig_left(ChipSig("-->+", "DUMEN"))
        self.sig_left(ChipSig("-->+", "ULWDR"))
        self.sig_left(ChipSig("-->+", "RAND", 0, 4))
        self.sig_left(ChipSig("-->+", "SCLKST"))
        self.sig_left(ChipSig("-->+", "RSTRDR"))

        self.sig_left(ChipSig("-->+", "CONDS", 0, 6))

        self.sig_right(ChipSig("+<->", "DQVAL", 0, 63))
        self.sig_right(ChipSig("+<--", "QVALOE"))

        self.sig_right(ChipSig("+-->", "ERR"))

        self.sig_right(ChipSig("+===", "ORST"))

        self.sig_right(ChipSig("+-->", "RSPEMN"))


        self.sig_right(ChipSig("+-->", "SME"))
        self.sig_right(ChipSig("+-->", "DME"))


        self.sig_right(ChipSig("+-->", "LDWDR"))
        self.sig_right(ChipSig("+-->", "DECC"))

        self.sig_right(ChipSig("+-->", "COND"))
        self.sig_right(ChipSig("+-->", "BLTCP"))


        self.finish()

def register():
    yield IOC()
