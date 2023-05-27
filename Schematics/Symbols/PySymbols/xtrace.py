#!/usr/bin/env python3

''' Tracer '''

from chip import Chip, FChip, ChipSig

class XTRACE(FChip):

    ''' Tracer '''

    symbol_name = "XTRACE"

    def __init__(self):
        super().__init__()

        for a in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.sig_left(ChipSig("-->+", a))


        self.sig_right(ChipSig("+-->", "NULL"))

        self.finish()

def register():
    yield XTRACE()


