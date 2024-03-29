#!/usr/bin/env python3

''' FIU Writable Control Store '''

from chip import Chip, FChip, ChipSig

class XFIUWCS(FChip):

    ''' FIU Writable Control Store '''

    symbol_name = "XFIUWCS"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "CLK"))
        self.sig_left(ChipSig("-->+", "CKEN"))
        self.sig_left(ChipSig("-->+", "SFST"))
        self.sig_left(ChipSig("-->+", "WE"))
        self.sig_left(ChipSig("-->+", "UAC", 0, 15))
        self.sig_left(ChipSig("-->+", "UAD", 0, 15))
        self.sig_left(ChipSig("-->+", "DUAS"))
        self.sig_left(ChipSig("-->+", "MODE"))
        self.sig_left(ChipSig("-->+", "SUIR"))
        self.sig_left(ChipSig("-->+", "DGI", 0, 7))
        self.sig_left(ChipSig("-->+", "DTVE"))

        self.sig_right(ChipSig("+===", "DGO", 0, 7))
        self.sig_right(ChipSig("+-->", "UPER"))
        self.sig_right(ChipSig("+-->", "APER"))
        self.sig_right(ChipSig("+-->", "OFSL", 0, 6))
        self.sig_right(ChipSig("+-->", "LFL", 0, 6))
        self.sig_right(ChipSig("+-->", "LFCN", 0, 1))
        self.sig_right(ChipSig("+-->", "OPSL", 0, 1))
        self.sig_right(ChipSig("+-->", "VMSL", 0, 1))
        self.sig_right(ChipSig("+-->", "FILL"))
        self.sig_right(ChipSig("+-->", "OSRC"))
        self.sig_right(ChipSig("+-->", "TIVI", 0, 3))
        self.sig_right(ChipSig("+-->", "LDO"))
        self.sig_right(ChipSig("+-->", "LDV"))
        self.sig_right(ChipSig("+-->", "LDT"))
        self.sig_right(ChipSig("+-->", "LDM"))
        self.sig_right(ChipSig("+-->", "MSTR", 0, 4))
        self.sig_right(ChipSig("+-->", "RSRC"))
        self.sig_right(ChipSig("+-->", "LSRC"))
        self.sig_right(ChipSig("+-->", "OFSRC"))

        self.finish()

def register():
    yield XFIUWCS()


