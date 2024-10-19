#!/usr/bin/env python3

''' IOP '''

from chip import Chip, FChip, ChipSig

class XIOP(FChip):

    ''' IOP '''

    symbol_name = "XIOP"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->o", "RESET"))

        self.sig_left(ChipSig("-->+", "EXTID", 0, 2))
        self.sig_left(ChipSig("-->+", "KEY"))

        self.sig_left(ChipSig("-->+", "SCLK"))
        self.sig_left(ChipSig("-->+", "RND", 0, 4))
        self.sig_left(ChipSig("-->+", "RTCEN"))
        self.sig_left(ChipSig("-->+", "ITYP", 0, 63))

        self.sig_right(ChipSig("+===", "ORST"))

        self.sig_right(ChipSig("+-->", "REQEMP"))
        self.sig_right(ChipSig("+-->", "RSPEMP"))
        self.sig_right(ChipSig("+-->", "RSPEMN"))
        self.sig_right(ChipSig("+-->", "OFLO"))


        self.sig_right(ChipSig("+<--", "QTHOE"))
        self.sig_right(ChipSig("+===", "QTH", 0, 31))
        self.sig_right(ChipSig("+<--", "QTMOE"))
        self.sig_right(ChipSig("+===", "QTM", 0, 15))
        self.sig_right(ChipSig("+<--", "QTLOE"))
        self.sig_right(ChipSig("+===", "QTL", 0, 15))


        self.finish(24)

def register():
    yield XIOP()


