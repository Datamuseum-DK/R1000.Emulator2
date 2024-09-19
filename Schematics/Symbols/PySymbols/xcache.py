#!/usr/bin/env python3

''' MEM32 Cache '''

from chip import Chip, FChip, ChipSig

class XCACHE(FChip):

    ''' MEM32 Cache '''

    symbol_name = "XCACHE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DQV", 0, 63))
        self.sig_left(ChipSig("-->+", "SPC", 0, 2))
        self.sig_left(ChipSig("-->+", "ADR", 0, 56))

        self.sig_left(ChipSig("-->+", "MCMD", 0, 3))
        self.sig_left(ChipSig("-->+", "CONT"))
        self.sig_left(ChipSig("-->+", "LDWDR"))
        self.sig_left(ChipSig("-->+", "BDISYN"))
        self.sig_left(ChipSig("-->+", "BDIFRZ"))
        self.sig_left(ChipSig("-->+", "MRUI7"))
        self.sig_left(ChipSig("-->+", "EABT"))
        self.sig_left(ChipSig("-->+", "ELABT"))
        self.sig_left(ChipSig("-->+", "LABT"))

        self.sig_right(ChipSig("+<->", "DQT", 0, 63))
        self.sig_right(ChipSig("+<->", "DQC", 0, 8))

        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+<--", "QTOE"))
        self.sig_right(ChipSig("+<--", "QCOE"))

        self.sig_right(ChipSig("+<--", "CLK"))

        self.sig_right(ChipSig("+-->", "NME"))
        self.sig_right(ChipSig("+-->", "NML"))

        self.sig_right(ChipSig("+-->", "CRE", 0, 6))
        self.sig_right(ChipSig("+-->", "CRL", 0, 6))

        #self.sig_right(ChipSig("+-->", "PQ", 0, 7))

        self.sig_right(ChipSig("+<--", "K12"))
        self.sig_right(ChipSig("+<--", "K13"))
        self.sig_right(ChipSig("+-->", "CMD", 0, 3))
        self.sig_right(ChipSig("+<--", "H1"))
        self.sig_right(ChipSig("+<--", "Q4"))
        self.sig_right(ChipSig("+<--", "LDMR"))
        self.sig_right(ChipSig("+-->", "PS", 0, 3))

        self.sig_right(ChipSig("+<--", "ISLOW"))
        self.sig_right(ChipSig("+<--", "ISA"))
        self.sig_right(ChipSig("+<--", "ICK"))
        self.sig_right(ChipSig("+<--", "RWE"))
        self.sig_right(ChipSig("+<--", "CAS"))
        self.sig_right(ChipSig("+<--", "Q2"))
        self.sig_right(ChipSig("+<--", "SET", 0, 1))


        self.sig_right(ChipSig("+-->", "DLRU"))
        self.sig_right(ChipSig("+<--", "DLOE"))
        self.sig_right(ChipSig("+<->", "DQL", 0, 3))
        self.sig_right(ChipSig("+-->", "LABRT"))

        self.sig_right(ChipSig("+-->", "CYO"))
        self.sig_right(ChipSig("+-->", "CYT"))
        self.sig_right(ChipSig("+-->", "MC2N"))
        self.sig_right(ChipSig("+-->", "LRUP"))

        self.finish(21)

def register():
    yield XCACHE()


