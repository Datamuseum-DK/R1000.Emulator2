#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class XSEQIBUF(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "XSEQIBUF"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "TYP", 0, 63))
        self.sig_left(ChipSig("-->+", "ICLK"))
        self.sig_left(ChipSig("-->+", "BCLK"))
        self.sig_left(ChipSig("-->+", "MUX"))
        self.sig_left(ChipSig("-->+", "CNDLD"))
        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "MD0"))
        self.sig_left(ChipSig("-->+", "RND1"))
        self.sig_left(ChipSig("-->+", "CLCLK"))
        self.sig_left(ChipSig("-->+", "RASEL", 0, 1))
        self.sig_left(ChipSig("-->+", "LAUIR", 0, 1))
        self.sig_left(ChipSig("-->+", "LINC"))
        self.sig_left(ChipSig("-->+", "MIBMT"))
        self.sig_left(ChipSig("-->+", "RCLK"))
        self.sig_left(ChipSig("-->+", "URAND", 0, 6))
        self.sig_left(ChipSig("-->+", "IRD", 0, 2))
        self.sig_left(ChipSig("-->+", "EMAC", 0, 6))

        self.sig_right(ChipSig("+<--", "VAL", 0, 63))
        self.sig_right(ChipSig("+-->", "DISP", 0, 15))
        self.sig_right(ChipSig("+-->", "EMPTY"))
        self.sig_right(ChipSig("+-->", "RADR", 0, 3))
        self.sig_right(ChipSig("+-->", "ICOND"))
        self.sig_right(ChipSig("+-->", "SEXT"))
        self.sig_right(ChipSig("+-->", "COFF", 0, 14))
        self.sig_right(ChipSig("+-->", "BRIDX", 0, 2))
        self.sig_right(ChipSig("+-->", "EMP"))
        self.sig_right(ChipSig("+-->", "ME", 0, 6))

        self.sig_left(ChipSig("-->+", "ACLK"))
        self.sig_left(ChipSig("-->+", "IMX"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "ILDRN"))
        self.sig_left(ChipSig("-->+", "DISPA"))
        self.sig_left(ChipSig("-->+", "FLIP"))
        self.sig_left(ChipSig("===+", "QV", 0, 15))
        self.sig_left(ChipSig("-->+", "QVOE"))
        self.sig_left(ChipSig("===+", "QB", 0, 15))
        self.sig_left(ChipSig("-->+", "QBOE"))

        self.sig_right(ChipSig("+-->", "UAD", 0, 15))
        self.sig_right(ChipSig("+-->", "DEC", 0, 7))
        self.sig_right(ChipSig("+-->", "CCL", 0, 3))
        self.sig_right(ChipSig("+-->", "DSP", 0, 15))


        self.finish()

def register():
    yield XSEQIBUF()


