#!/usr/bin/env python3

''' IOC Dummy register '''

from chip import Chip, FChip, ChipSig

class XDUMMY(FChip):

    ''' IOC Dummy register '''

    symbol_name = "XDUMMY"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("<->+", "DQTYP", 0, 63))
        self.sig_left(ChipSig("-->+", "QTYPOE"))

        self.sig_right(ChipSig("+<->", "DQVAL", 0, 63))
        self.sig_right(ChipSig("+<--", "QVALOE"))
        self.sig_right(ChipSig("+<--", "LDDUM"))
        self.sig_right(ChipSig("+<--", "ITYP"))
        self.sig_right(ChipSig("+<--", "IVAL"))
        self.sig_right(ChipSig("+<--", "Q4"))

        self.finish()

def register():
    yield XDUMMY()
