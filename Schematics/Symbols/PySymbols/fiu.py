#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip, FChip, ChipSig

class FIU(FChip):

    ''' FIU First Stage Rotator '''

    symbol_name = "FIU"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "SCLKE"))

        self.sig_left(ChipSig("-->+", "LABR"))
        self.sig_left(ChipSig("-->+", "LEABR"))
        self.sig_left(ChipSig("-->+", "EABR"))
        self.sig_left(ChipSig("-->+", "SFSTP"))
        self.sig_left(ChipSig("-->+", "UEVSTP"))

        self.sig_left(ChipSig("-->+", "TSTS"))
        self.sig_left(ChipSig("-->+", "TRMS"))
        self.sig_left(ChipSig("-->+", "TFRZ"))

        self.sig_right(ChipSig("+-->", "MEMCND"))
        self.sig_right(ChipSig("+-->", "CNDTRU"))
        self.sig_right(ChipSig("+-->", "STOP0"))

        self.sig_right(ChipSig("+-->", "SYNC"))
        self.sig_right(ChipSig("+-->", "FREZE"))

        self.finish()

def register():
    yield FIU()


