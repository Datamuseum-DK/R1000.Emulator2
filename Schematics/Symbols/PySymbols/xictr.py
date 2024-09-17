#!/usr/bin/env python3

''' IOC counters '''

from chip import Chip, FChip, ChipSig

class XICTR(FChip):

    ''' IOC counters'''

    symbol_name = "XICTR"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "SCE"))
        self.sig_left(ChipSig("-->+", "ESLC"))
        self.sig_left(ChipSig("-->+", "DSLC"))
        self.sig_left(ChipSig("-->+", "CSLC"))
        self.sig_left(ChipSig("-->+", "EDLY"))
        self.sig_left(ChipSig("-->+", "DDLY"))
        self.sig_left(ChipSig("-->+", "CDLY"))
        self.sig_left(ChipSig("-->+", "LDSL"))
        self.sig_left(ChipSig("-->+", "LDDL"))

        self.sig_right(ChipSig("+<->", "DQT", 0, 31))
        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+-->", "SME"))
        self.sig_right(ChipSig("+-->", "DME"))

        self.finish()

def register():
    yield XICTR()


