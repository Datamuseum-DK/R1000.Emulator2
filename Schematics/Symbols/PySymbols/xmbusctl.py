#!/usr/bin/env python3

''' MEM32 bus control '''

from chip import Chip, FChip, ChipSig

class XMBUSCTL(FChip):

    ''' MEM32 bus control '''

    symbol_name = "XMBUSCTL"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DBUZZOF"))
        self.sig_left(ChipSig("-->+", "DDRVMEM"))
        self.sig_left(ChipSig("-->+", "DDRVTAG"))
        self.sig_left(ChipSig("-->+", "HIBOARD"))
        self.sig_left(ChipSig("-->+", "TVDRV"))
        self.sig_left(ChipSig("-->+", "VDRV"))
        self.sig_left(ChipSig("-->+", "XHITA"))
        self.sig_left(ChipSig("-->+", "XHITB"))
        self.sig_left(ChipSig("-->+", "AHIT"))
        self.sig_left(ChipSig("-->+", "BHIT"))

        self.sig_right(ChipSig("+-->", "TYPAOE"))
        self.sig_right(ChipSig("+-->", "VALAOE"))
        self.sig_right(ChipSig("+-->", "TYPBOE"))
        self.sig_right(ChipSig("+-->", "VALBOE"))
        self.sig_right(ChipSig("+-->", "EXTHIT"))

        self.finish()

def register():
    yield XMBUSCTL()


