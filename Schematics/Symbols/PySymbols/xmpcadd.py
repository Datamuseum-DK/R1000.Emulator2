#!/usr/bin/env python3

''' SEQ Macro-PC adder '''

from chip import Chip, FChip, ChipSig

class XMPCADD(FChip):

    ''' SEQ Macro-PC adder '''

    symbol_name = "XMPCADD"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "MIBMT"))

        self.sig_left(ChipSig("-->+", "DISP", 0, 15))
        self.sig_left(ChipSig("-->+", "CURI", 0, 15))
        self.sig_left(ChipSig("-->+", "MPC", 0, 14))


        self.sig_right(ChipSig("+-->", "BOFF", 0, 14))
        self.sig_right(ChipSig("+<--", "RCLK"))
        self.sig_right(ChipSig("+<--", "COSEL", 0, 1))
        self.sig_right(ChipSig("+-->", "COFF", 0, 14))

        self.finish()

def register():
    yield XMPCADD()


