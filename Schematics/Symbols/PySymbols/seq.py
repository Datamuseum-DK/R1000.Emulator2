#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class SEQ(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "SEQ"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->+", "LMAC"))

        # self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("-->+", "SSTOP"))

        self.sig_left(ChipSig("-->+", "MCOND"))
        self.sig_left(ChipSig("-->+", "MCPOL"))
        self.sig_left(ChipSig("-->+", "SFSTP"))

        self.sig_right(ChipSig("+<--", "UEI12"))


        self.sig_right(ChipSig("+-->", "QSTP7"))
        self.sig_right(ChipSig("+-->", "LMACO"))

        self.sig_right(ChipSig("+-->", "U_EVENT"))
        self.sig_right(ChipSig("o-->", "SFIVE"))
        self.sig_right(ChipSig("o-->", "ABORT"))

        self.sig_right(ChipSig("+<--", "CNDXF"))

        self.sig_right(ChipSig("+-->", "LABRT"))

        self.sig_right(ChipSig("+-->", "QDFRZ"))
        self.sig_right(ChipSig("+-->", "SEQST"))


        self.finish()

def register():
    yield SEQ()

