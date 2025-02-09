#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class SEQ(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "SEQ"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->+", "SCLKE"))

        self.sig_left(ChipSig("-->+", "CTL", 0, 2))

        self.sig_left(ChipSig("-->+", "CSA", 0, 3))

        self.sig_left(ChipSig("-->+", "DV_U"))
        self.sig_left(ChipSig("-->+", "LMAC"))

        # self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "DMODE"))

        self.sig_left(ChipSig("-->+", "MCOND"))
        self.sig_left(ChipSig("-->+", "MCPOL"))
        self.sig_left(ChipSig("-->+", "SFSTP"))
        self.sig_left(ChipSig("-->+", "DSTOP"))
        self.sig_left(ChipSig("-->+", "UM", 0, 1))

        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+<--", "ADROE"))

        self.sig_right(ChipSig("+<--", "EMAC", 0, 6))
        self.sig_right(ChipSig("+<--", "UEI", 0, 14))


        self.sig_right(ChipSig("+-->", "QSTP7"))
        self.sig_right(ChipSig("+-->", "HALT"))
        self.sig_right(ChipSig("+-->", "LMACO"))

        self.sig_right(ChipSig("+-->", "U_EVENT"))
        self.sig_right(ChipSig("o-->", "SFIVE"))
        self.sig_right(ChipSig("o-->", "ABORT"))

        self.sig_right(ChipSig("+<--", "CNDX0"))
        self.sig_right(ChipSig("+<--", "CNDX2"))
        self.sig_right(ChipSig("+<--", "CNDX3"))
        self.sig_right(ChipSig("+<--", "CNDX8"))
        self.sig_right(ChipSig("+<--", "CNDX9"))
        self.sig_right(ChipSig("+<--", "CNDXA"))
        self.sig_right(ChipSig("+<--", "CNDXB"))
        self.sig_right(ChipSig("+<--", "CNDXC"))
        self.sig_right(ChipSig("+<--", "CNDXD"))
        self.sig_right(ChipSig("+<--", "CNDXE"))
        self.sig_right(ChipSig("+<--", "CNDXF"))

        self.sig_right(ChipSig("+-->", "SEQSN"))
        self.sig_right(ChipSig("+-->", "LABRT"))
        self.sig_right(ChipSig("+-->", "UEVEN"))
        self.sig_right(ChipSig("+-->", "CSEL", 0, 6))


        self.finish()

def register():
    yield SEQ()

