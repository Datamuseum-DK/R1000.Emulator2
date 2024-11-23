#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class SEQ(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "SEQ"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQT", 0, 63))
        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->+", "BCLK"))
        self.sig_left(ChipSig("-->+", "RASEL", 0, 1))
        self.sig_left(ChipSig("-->+", "LAUIR", 0, 1))
        self.sig_left(ChipSig("-->+", "LINC"))
        self.sig_left(ChipSig("-->+", "MIBMT"))
        self.sig_left(ChipSig("-->+", "URAND", 0, 6))
        self.sig_left(ChipSig("-->+", "IRD", 0, 2))
        self.sig_left(ChipSig("-->+", "ACLK"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "FLIP"))
        self.sig_left(ChipSig("-->+", "TOSCLK"))

        self.sig_left(ChipSig("-->+", "MD"))

        self.sig_left(ChipSig("-->+", "SGEXT"))
        self.sig_left(ChipSig("-->+", "CTL", 0, 2))

        self.sig_left(ChipSig("-->+", "CSA", 0, 3))

        self.sig_left(ChipSig("-->+", "Q3COND"))

        self.sig_left(ChipSig("-->+", "LCLK"))

        self.sig_left(ChipSig("-->+", "DV_U"))
        self.sig_left(ChipSig("-->+", "LMAC"))

        self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("-->+", "BRTYP", 0, 3))
        self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "DMODE"))
        self.sig_left(ChipSig("-->+", "COND"))
        self.sig_left(ChipSig("-->+", "BRTIM", 0, 1))

        self.sig_left(ChipSig("-->+", "BHCKE"))

        self.sig_left(ChipSig("-->+", "LIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TCLR"))

        self.sig_left(ChipSig("-->+", "BHEN"))

        self.sig_left(ChipSig("-->+", "ENFU"))
        self.sig_left(ChipSig("-->+", "STOP"))
        self.sig_left(ChipSig("-->+", "FIU_CLK"))
        self.sig_left(ChipSig("-->+", "CSEL", 0, 6))
        self.sig_left(ChipSig("-->+", "LXVAL"))

        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+===", "ADR", 0, 63))
        self.sig_right(ChipSig("+<--", "ADROE"))
        self.sig_right(ChipSig("+===", "OSPC", 0, 2))
        self.sig_right(ChipSig("+<--", "OSPCOE"))

        self.sig_right(ChipSig("+-->", "NU", 0, 13))

        self.sig_right(ChipSig("+<--", "EMAC", 0, 6))
        self.sig_right(ChipSig("+<--", "UEI", 0, 14))

        self.sig_right(ChipSig("+-->", "DISP0"))
        self.sig_right(ChipSig("+-->", "RADR", 0, 3))
        self.sig_right(ChipSig("+-->", "SEXT"))


        self.sig_right(ChipSig("+-->", "UEVP"))

        self.sig_right(ChipSig("+-->", "DBHINT"))
        self.sig_right(ChipSig("+-->", "DMDISP"))

        self.sig_right(ChipSig("+-->", "BHN"))

        self.sig_right(ChipSig("+-->", "FERR"))
        self.sig_right(ChipSig("+-->", "MIBUF"))
        self.sig_right(ChipSig("+-->", "QSTP7"))
        self.sig_right(ChipSig("+-->", "HALT"))
        self.sig_right(ChipSig("+-->", "BAR8"))
        self.sig_right(ChipSig("+-->", "MEH"))
        self.sig_right(ChipSig("+-->", "LMACO"))
        self.sig_right(ChipSig("+-->", "DISP"))
        self.sig_right(ChipSig("+-->", "CONDA"))
        self.sig_right(ChipSig("+-->", "CONDB"))
        self.sig_right(ChipSig("+-->", "CONDC"))

        self.sig_right(ChipSig("+-->", "U_EVENT"))
        self.sig_right(ChipSig("o-->", "U_EVENT~"))
        self.sig_right(ChipSig("o-->", "SFIVE"))
        self.finish()

def register():
    yield SEQ()

