#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip, FChip, ChipSig

class FIU(FChip):

    ''' FIU First Stage Rotator '''

    symbol_name = "FIU"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_left(ChipSig("<->+", "DQF", 0, 63))
        self.sig_left(ChipSig("-->+", "QFOE"))

        #self.sig_left(ChipSig("-->+", "OL", 0, 6))
        #self.sig_left(ChipSig("-->+", "LFL", 0, 6))
        #self.sig_left(ChipSig("-->+", "LFRC", 0, 1))
        #self.sig_left(ChipSig("-->+", "OP", 0, 1))
        #self.sig_left(ChipSig("-->+", "SEL", 0, 1))
        #self.sig_left(ChipSig("-->+", "FSRC"))
        #self.sig_left(ChipSig("-->+", "ORSR"))
        #self.sig_left(ChipSig("-->+", "OCLK"))
        #self.sig_left(ChipSig("-->+", "VCLK"))
        #self.sig_left(ChipSig("-->+", "TCLK"))
        #self.sig_left(ChipSig("-->+", "LDMDR"))
        #self.sig_left(ChipSig("-->+", "MSTRT", 0, 4))
        #self.sig_left(ChipSig("-->+", "RDSRC"))
        #self.sig_left(ChipSig("-->+", "LSRC"))
        #self.sig_left(ChipSig("-->+", "OSRC"))
        #self.sig_left(ChipSig("-->+", "TIVI", 0, 3))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H1"))
        self.sig_left(ChipSig("-->+", "SCLKE"))


        self.sig_left(ChipSig("-->+", "PRED"))

        self.sig_left(ChipSig("-->+", "LABR"))
        self.sig_left(ChipSig("-->+", "LEABR"))
        self.sig_left(ChipSig("-->+", "EABR"))
        self.sig_left(ChipSig("-->+", "SFSTP"))
        self.sig_left(ChipSig("-->+", "UEVSTP"))

        self.sig_left(ChipSig("-->+", "MICEN"))

        self.sig_right(ChipSig("+<--", "QVOE"))

        self.sig_right(ChipSig("+<--", "QADROE"))

        self.sig_right(ChipSig("+<--", "CNDSL", 0, 6))
        self.sig_right(ChipSig("+<--", "CNV", 0, 3))
        self.sig_right(ChipSig("+<--", "CSA", 0, 2))
        self.sig_right(ChipSig("+<--", "MCTL", 0, 3))
        self.sig_right(ChipSig("+<--", "BDHIT", 0, 3))
        self.sig_right(ChipSig("+<--", "ST", 0, 1))

        self.sig_right(ChipSig("+-->", "HOFS", 0, 3))
        self.sig_right(ChipSig("+-->", "MEMCT", 0, 3))


        self.sig_right(ChipSig("+-->", "CHIT"))
        self.sig_right(ChipSig("+-->", "RFSH"))
        self.sig_right(ChipSig("+-->", "FRDR"))


        self.sig_right(ChipSig("+-->", "MEMCND"))
        self.sig_right(ChipSig("+-->", "CNDTRU"))
        self.sig_right(ChipSig("+-->", "CONTIN"))
        self.sig_right(ChipSig("+-->", "DNEXT"))
        self.sig_right(ChipSig("+-->", "CSAWR"))
        self.sig_right(ChipSig("+-->", "CONDA"))
        self.sig_right(ChipSig("+-->", "CONDB"))
        self.sig_right(ChipSig("+-->", "PGXIN"))
        self.sig_right(ChipSig("+-->", "MEMEX"))

        self.finish()

def register():
    yield FIU()


