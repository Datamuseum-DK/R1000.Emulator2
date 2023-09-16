#!/usr/bin/env python3

''' FIU Memory Monitor '''

from chip import Chip, FChip, ChipSig

class XMEMMON(FChip):

    ''' FIU Memory Monitor '''

    symbol_name = "XMEMMON"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "MSTRT", 0, 4))
        self.sig_left(ChipSig("-->+", "DMHLD"))
        self.sig_left(ChipSig("-->+", "LABR"))
        self.sig_left(ChipSig("-->+", "LEABR"))
        self.sig_left(ChipSig("-->+", "EABR"))
        self.sig_left(ChipSig("-->+", "MCTL", 0, 3))

        self.sig_right(ChipSig("+-->", "LABRT"))
        self.sig_right(ChipSig("+-->", "RMARP"))

        self.sig_right(ChipSig("+-->", "PRMZ", 0, 5))

        self.sig_right(ChipSig("+-->", "PRMT", 0, 7))

        self.sig_left(ChipSig("-->+", "DMCTL"))
        self.sig_left(ChipSig("-->+", "SCKE"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "H2"))

        self.sig_left(ChipSig("-->+", "CNDSL", 0, 6))

        self.sig_left(ChipSig("-->+", "BDHIT", 0, 3))
        self.sig_left(ChipSig("-->+", "DGHWE"))
        self.sig_left(ChipSig("-->+", "PGMOD"))


        self.sig_right(ChipSig("+-->", "PGSTQ", 0, 1))
        self.sig_right(ChipSig("+-->", "ST1"))
        self.sig_right(ChipSig("+-->", "EABD"))
        self.sig_left(ChipSig("-->+", "IQF", 0, 3))
        self.sig_right(ChipSig("+-->", "OQF", 0, 3))

        self.sig_left(ChipSig("-->+", "SFSTP"))
        self.sig_right(ChipSig("+-->", "MEMEXP"))

        self.sig_left(ChipSig("-->+", "Q4DIS"))
        self.sig_right(ChipSig("+-->", "OMQ", 0, 3))

        self.sig_left(ChipSig("-->+", "MISS"))
        self.sig_left(ChipSig("-->+", "CSAOOR"))
        self.sig_left(ChipSig("-->+", "PXNXT"))
        self.sig_left(ChipSig("-->+", "EVENT"))
        self.sig_left(ChipSig("-->+", "TI", 0, 31))
        self.sig_left(ChipSig("-->+", "SCADAT"))
        self.sig_left(ChipSig("-->+", "SCAPEV"))
        self.sig_left(ChipSig("-->+", "FRDRDR"))
        self.sig_left(ChipSig("-->+", "FRDTYP"))
        self.sig_left(ChipSig("-->+", "UEVSTP"))

        self.sig_right(ChipSig("+-->", "MEMCT", 0, 3))
        self.sig_right(ChipSig("+-->", "MCNTL3"))
        self.sig_right(ChipSig("+-->", "SPARER"))
        self.sig_right(ChipSig("+-->", "LOGRW"))
        self.sig_right(ChipSig("+-->", "LOGRWN"))

        self.sig_right(ChipSig("+-->", "COND", 0, 7))
        self.sig_right(ChipSig("+-->", "RTVNXT"))
        self.sig_right(ChipSig("+-->", "MEMCND"))
        self.sig_right(ChipSig("+-->", "CNDTRU"))
        self.sig_right(ChipSig("+-->", "CONTIN"))
        self.sig_right(ChipSig("+-->", "ACKRFS"))
        self.sig_right(ChipSig("+-->", "WRSCAV"))
        self.sig_right(ChipSig("+-->", "SETQ", 0, 1))
        self.sig_right(ChipSig("+-->", "COND6A"))
        self.sig_right(ChipSig("+-->", "COND6E"))
	
        self.sig_right(ChipSig("+-->", "NOHIT"))
        self.sig_right(ChipSig("+-->", "SCVHIT"))
        self.sig_right(ChipSig("+-->", "MCISRD"))
        self.sig_right(ChipSig("+-->", "LOGRWD"))

        self.finish()

def register():
    yield XMEMMON()


