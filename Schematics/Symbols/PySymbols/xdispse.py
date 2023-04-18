#!/usr/bin/env python3

''' SEQ DISP sign-extender '''

from chip import Chip, FChip, ChipSig

class XDISPSE(FChip):

    ''' SEQ DISP sign-extender '''

    symbol_name = "XDISPSE"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "SGEXT"))
        self.sig_left(ChipSig("-->+", "DISP", 0, 15))

        self.sig_right(ChipSig("+-->", "Q", 0, 19))

        self.finish()

def register():
    yield XDISPSE()


