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
        self.sig_left(ChipSig("-->+", "BIDX", 0, 2))
        self.sig_left(ChipSig("-->+", "CNDLD"))
        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "MD0"))
        self.sig_left(ChipSig("-->+", "RND1"))
        self.sig_left(ChipSig("-->+", "BOF", 0, 11))

        self.sig_right(ChipSig("+<--", "VAL", 0, 63))
        self.sig_right(ChipSig("+-->", "DISP", 0, 15))
        self.sig_right(ChipSig("+-->", "EMP"))
        self.sig_right(ChipSig("+-->", "MPS", 0, 14))

        self.finish()

def register():
    yield XSEQIBUF()


