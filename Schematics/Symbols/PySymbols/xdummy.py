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

        self.sig_left(ChipSig("<->+", "DQC", 0, 8))
        self.sig_left(ChipSig("-->+", "QCOE"))
        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "TVEN"))
        self.sig_left(ChipSig("-->+", "QTOE"))
        self.sig_left(ChipSig("-->+", "LDCB"))
        self.sig_left(ChipSig("-->+", "DROT"))
        self.sig_left(ChipSig("-->+", "CSTP"))

        self.sig_right(ChipSig("+-->", "ERR"))
        self.sig_right(ChipSig("+-->", "CBER"))
        self.sig_right(ChipSig("+-->", "MBER"))
        self.sig_right(ChipSig("+===", "QT", 0, 15))

	# XIOP
        self.sig_left(ChipSig("-->o", "RESET"))

        self.sig_left(ChipSig("-->+", "EXTID", 0, 2))
        self.sig_left(ChipSig("-->+", "KEY"))

        self.sig_left(ChipSig("-->+", "RND", 0, 4))
        self.sig_left(ChipSig("-->+", "RTCEN"))

        self.sig_right(ChipSig("+===", "ORST"))

        self.sig_right(ChipSig("+-->", "REQEMP"))
        self.sig_right(ChipSig("+-->", "RSPEMP"))
        self.sig_right(ChipSig("+-->", "RSPEMN"))
        self.sig_right(ChipSig("+-->", "OFLO"))


        self.sig_right(ChipSig("+<--", "QTHOE"))
        self.sig_right(ChipSig("+===", "QTH", 0, 31))
        self.sig_right(ChipSig("+<--", "QTMOE"))
        self.sig_right(ChipSig("+===", "QTM", 0, 15))
        self.sig_right(ChipSig("+<--", "QTLOE"))
        self.sig_right(ChipSig("+===", "QTL", 0, 15))

        self.sig_right(ChipSig("+-->", "BELOW"))
        self.sig_right(ChipSig("+-->", "PFR"))

        self.sig_right(ChipSig("+<--", "QIOE"))
        self.sig_right(ChipSig("+===", "QI", 0, 31))
        self.sig_right(ChipSig("+-->", "SME"))
        self.sig_right(ChipSig("+-->", "DME"))
        self.finish()

def register():
    yield XDUMMY()


