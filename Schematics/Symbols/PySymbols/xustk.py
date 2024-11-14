#!/usr/bin/env python3

''' Micro Stack '''

from chip import Chip, FChip, ChipSig

class XUSTK(FChip):

    ''' Micro Stack '''

    symbol_name = "XUSTK"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))

        self.sig_left(ChipSig("-->+", "Q3COND"))

        self.sig_left(ChipSig("-->+", "QWOE"))
        self.sig_left(ChipSig("===+", "QW", 0, 15))
        self.sig_left(ChipSig("-->+", "LCLK"))

        self.sig_left(ChipSig("-->+", "PUSHRND"))
        self.sig_left(ChipSig("-->+", "POPRND"))

        self.sig_left(ChipSig("-->+", "DV_U"))
        self.sig_left(ChipSig("-->+", "LMAC"))

        self.sig_left(ChipSig("-->+", "BRN", 0, 13))

        self.sig_left(ChipSig("<--+", "U_EVENT"))
        self.sig_left(ChipSig("<--o", "U_EVENT~"))
        self.sig_left(ChipSig("<--o", "MACRO_HIC"))

        self.sig_left(ChipSig("-->+", "LATE", 0, 2))

        self.sig_left(ChipSig("-->+", "UEI", 0, 14))
        self.sig_left(ChipSig("-->+", "ACK"))
        self.sig_left(ChipSig("-->+", "BRTYP", 0, 3))
        self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "DMODE"))

        
        self.sig_right(ChipSig("+-->", "SVLAT"))
        self.sig_right(ChipSig("+<--", "CSR"))
        self.sig_right(ChipSig("+<--", "STOP"))
        self.sig_right(ChipSig("+-->", "SSZ"))

        self.sig_right(ChipSig("+<--", "QFOE"))
        self.sig_right(ChipSig("+===", "DQF", 0, 63))

        self.sig_right(ChipSig("+<--", "FIU_CLK"))

        self.sig_right(ChipSig("+<--", "DECC", 0, 12))

        self.sig_right(ChipSig("+-->", "NU", 0, 13))

        self.sig_right(ChipSig("+-->", "UEVP"))

        self.sig_left(ChipSig("-->+", "COND"))
        self.sig_left(ChipSig("-->+", "BRTIM", 0, 1))
        self.sig_left(ChipSig("-->+", "MEVENT"))

        self.sig_left(ChipSig("-->+", "SCKE"))

        self.sig_left(ChipSig("-->+", "BHCKE"))
        self.sig_left(ChipSig("-->+", "MPRND"))

        self.sig_left(ChipSig("-->+", "LIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TIN", 0, 3))
        self.sig_left(ChipSig("-->+", "TCLR"))
        self.sig_left(ChipSig("-->+", "RRND", 0, 1))
        self.sig_left(ChipSig("-->+", "MEV"))
        #self.sig_left(ChipSig("-->+", "SSTOP"))
        self.sig_left(ChipSig("-->+", "BHEN"))

        self.sig_right(ChipSig("+-->", "VDISP"))

        self.sig_right(ChipSig("+-->", "DTIME"))
        self.sig_right(ChipSig("+-->", "DBHINT"))
        self.sig_right(ChipSig("+-->", "DMDISP"))
        self.sig_right(ChipSig("+-->", "MPCMB"))

        self.sig_right(ChipSig("+-->", "RQ", 0, 3))
        self.sig_right(ChipSig("+-->", "FO7"))
        self.sig_right(ChipSig("+-->", "LDC"))

        self.sig_right(ChipSig("+-->", "BHP"))
        self.sig_right(ChipSig("+-->", "BHN"))

        self.finish()

def register():
    yield XUSTK()


