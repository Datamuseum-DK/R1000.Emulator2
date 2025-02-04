#!/usr/bin/env python3

''' TV state clock '''

from chip import Chip, FChip, ChipSig

class XTVSCLK(FChip):

    ''' TV state clock '''

    symbol_name = "XTVSCLK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q4E"))
        self.sig_left(ChipSig("-->+", "SCE"))
        self.sig_left(ChipSig("-->+", "SFS"))
        self.sig_left(ChipSig("-->+", "STS"))
        self.sig_left(ChipSig("-->+", "RMS"))
        self.sig_left(ChipSig("-->+", "WEL"))
        self.sig_left(ChipSig("-->+", "DSTOP"))

        self.sig_right(ChipSig("+-->", "ACLK"))
        self.sig_right(ChipSig("+-->", "UCLK"))
        self.sig_right(ChipSig("+-->", "ARFWE"))

        self.finish(20)

def register():
    yield XTVSCLK()


