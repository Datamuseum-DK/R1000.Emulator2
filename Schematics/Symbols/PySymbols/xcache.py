#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class XCACHE(FChip):

    ''' MEM32 Cache '''

    symbol_name = "XCACHE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "A", 0, 13))
        self.sig_left(ChipSig("<->+", "VDQ", 0, 63))
        self.sig_left(ChipSig("-->+", "CWE", 0, 5))
        self.sig_left(ChipSig("-->+", "CWL", 0, 5))
        self.sig_left(ChipSig("-->+", "PDQ", 0, 7))
        self.sig_left(ChipSig("-->+", "DIR"))
        self.sig_left(ChipSig("-->+", "EVEN"))
        self.sig_left(ChipSig("-->+", "LVEN"))
        self.sig_left(ChipSig("-->+", "EWE"))
        self.sig_left(ChipSig("-->+", "LWE"))
        self.sig_left(ChipSig("-->+", "ELCE"))

        self.sig_right(ChipSig("+<--", "WE"))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "TGOE"))

        self.sig_right(ChipSig("+<--", "CLK"))
        self.sig_right(ChipSig("+<--", "OEE"))
        self.sig_right(ChipSig("+<--", "OEL"))
        self.sig_right(ChipSig("+<--", "DIAG"))
        self.sig_right(ChipSig("+<--", "TSPR", 0, 1))
        self.sig_right(ChipSig("+<--", "TSMO"))
        self.sig_right(ChipSig("+-->", "PERR"))
        self.sig_right(ChipSig("+-->", "TSPO"))

        self.sig_right(ChipSig("+<--", "EQ"))
        self.sig_right(ChipSig("+<--", "E"))
        self.sig_right(ChipSig("+<--", "NM", 0, 31))
        self.sig_right(ChipSig("+<--", "PG", 0, 12))
        self.sig_right(ChipSig("+<--", "SP", 0, 2))
        self.sig_right(ChipSig("+-->", "NME"))
        self.sig_right(ChipSig("+-->", "NML"))

        self.sig_right(ChipSig("+-->", "TQ", 0, 1))

        self.sig_right(ChipSig("+-->", "CRE", 0, 5))
        self.sig_right(ChipSig("+-->", "CRL", 0, 5))

        #self.sig_right(ChipSig("+-->", "PQ", 0, 7))

        self.sig_right(ChipSig("+-->", "DROE"))
        self.sig_right(ChipSig("+<--", "VQOE"))
        self.sig_right(ChipSig("+<--", "PQOE"))
        self.sig_right(ChipSig("+<--", "K12"))
        self.sig_right(ChipSig("+<--", "K13"))

        self.finish()

def register():
    yield XCACHE()


