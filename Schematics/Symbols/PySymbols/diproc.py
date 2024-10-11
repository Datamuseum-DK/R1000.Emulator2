#!/usr/bin/env python3

''' Intel 8051 - 8 Bit Control Oriented Microcomputers '''

from chip import Chip, FChip, ChipSig

class DIPROC(FChip):

    ''' Diag Processor '''

    symbol_name = "DIPROC"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "RST"))
        self.sig_left(ChipSig("-->+", "XTAL2"))
        self.sig_left(ChipSig("-->+", "INT0"))
        self.sig_left(ChipSig("-->+", "INT1"))
        self.sig_left(ChipSig("-->+", "DBUS"))
        self.sig_left(ChipSig("-->+", "ID", 0, 3))

        self.sig_right(ChipSig("+-->", "WR"))
        self.sig_right(ChipSig("+-->", "A", 0, 7))
        self.sig_right(ChipSig("+<->", "B", 0, 7))
        self.sig_right(ChipSig("+<->", "C", 0, 7))

        self.finish()

def register():
    yield DIPROC()
