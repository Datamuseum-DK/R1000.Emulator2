#!/usr/bin/env python3

''' State clock gate '''

from chip import Chip, FChip, ChipSig

class XSCLK(FChip):

    ''' State clock gate '''

    def __init__(self, npins, *args, **kwargs):
        self.symbol_name = "XSCLK%d" % npins

        super().__init__(*args, **kwargs)

        for i in range(npins):
            self.sig_left(ChipSig("-->+", "D%d" % i))

        for i in range(npins):
            self.sig_right(ChipSig("+-->", "Q%d" % i))

        self.sig_right(ChipSig("+<--", "Q4E"))
        self.sig_right(ChipSig("+<--", "SCE"))

        self.finish(19)
           
def register():
    for i in (2, 3, 4, 8, 14,):
        yield XSCLK(i)
