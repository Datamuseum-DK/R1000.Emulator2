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
        self.sig_left(ChipSig("-->+", "OTYPOE"))


        self.sig_right(ChipSig("+===", "ORST"))

        self.sig_right(ChipSig("+-->", "REQEMP"))
        self.sig_right(ChipSig("+-->", "RSPEMP"))

        self.sig_right(ChipSig("+<--", "RND", 0, 4))

        self.sig_level()
        self.sig_left(ChipSig("-->+", "ITYP", 0, 15))
        self.sig_right(ChipSig("+===", "OTYP", 0, 15))


        self.finish(24)

def register():
    yield XIOP()


