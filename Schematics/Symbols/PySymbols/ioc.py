#!/usr/bin/env python3

''' IOC Dummy register '''

from chip import Chip, FChip, ChipSig

class IOC(FChip):

    ''' IOC Dummy register '''

    symbol_name = "IOC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->o", "RESET"))

        self.finish(19)

def register():
    yield IOC()
