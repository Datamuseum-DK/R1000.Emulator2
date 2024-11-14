#!/usr/bin/env python3

''' SEQ Instruction Buffer '''

from chip import Chip, FChip, ChipSig

class XSEQIBUF(FChip):

    ''' SEQ Instruction Buffer '''

    symbol_name = "XSEQIBUF"

    def __init__(self):
        super().__init__()

        self.sig_left(ChipSig("-->+", "DQT", 0, 63))
        self.sig_left(ChipSig("-->+", "QTOE"))

        self.sig_left(ChipSig("-->+", "Q2"))
        self.sig_left(ChipSig("-->+", "Q4"))
        self.sig_left(ChipSig("-->+", "RTCLK"))

        self.sig_left(ChipSig("-->+", "ICLK"))
        self.sig_left(ChipSig("-->+", "BCLK"))
        self.sig_left(ChipSig("-->+", "MUX"))
        self.sig_left(ChipSig("-->+", "CNDLD"))
        self.sig_left(ChipSig("-->+", "WDISP"))
        self.sig_left(ChipSig("-->+", "MD0"))
        self.sig_left(ChipSig("-->+", "RND1"))
        self.sig_left(ChipSig("-->+", "CLCLK"))
        self.sig_left(ChipSig("-->+", "RASEL", 0, 1))
        self.sig_left(ChipSig("-->+", "LAUIR", 0, 1))
        self.sig_left(ChipSig("-->+", "LINC"))
        self.sig_left(ChipSig("-->+", "MIBMT"))
        self.sig_left(ChipSig("-->+", "URAND", 0, 6))
        self.sig_left(ChipSig("-->+", "IRD", 0, 2))
        self.sig_left(ChipSig("-->+", "EMAC", 0, 6))
        self.sig_left(ChipSig("-->+", "ACLK"))
        self.sig_left(ChipSig("-->+", "IMX"))
        self.sig_left(ChipSig("-->+", "SCLKE"))
        self.sig_left(ChipSig("-->+", "ILDRN"))
        self.sig_left(ChipSig("-->+", "DISPA"))
        self.sig_left(ChipSig("-->+", "FLIP"))
        self.sig_left(ChipSig("-->+", "BMCLK"))

        self.sig_right(ChipSig("+<->", "DQV", 0, 63))
        self.sig_right(ChipSig("+<--", "QVOE"))
        self.sig_right(ChipSig("+-->", "DISP", 0, 15))
        self.sig_right(ChipSig("+-->", "EMPTY"))
        self.sig_right(ChipSig("+-->", "RADR", 0, 3))
        self.sig_right(ChipSig("+-->", "ICOND"))
        self.sig_right(ChipSig("+-->", "SEXT"))
        self.sig_right(ChipSig("+-->", "BRIDX", 0, 2))
        self.sig_right(ChipSig("+-->", "EMP"))
        self.sig_right(ChipSig("+-->", "ME", 0, 6))


        self.sig_right(ChipSig("+-->", "DEC", 0, 7))
        self.sig_right(ChipSig("+-->", "BMCLS"))

        self.sig_left(ChipSig("-->+", "RAMWE"))
        self.sig_left(ChipSig("-->+", "RSAD", 0, 3))
        self.sig_left(ChipSig("-->+", "TOSCLK"))
        self.sig_left(ChipSig("-->+", "ADRICD"))

        self.sig_left(ChipSig("-->+", "ISPC", 0, 2))

        self.sig_left(ChipSig("-->+", "MCLK"))
        self.sig_left(ChipSig("-->+", "CSEL"))
        self.sig_left(ChipSig("-->+", "CNCK"))

        self.sig_left(ChipSig("-->+", "MD"))
        self.sig_left(ChipSig("-->+", "MSD", 0, 2))
        self.sig_left(ChipSig("-->+", "H2"))
        self.sig_left(ChipSig("-->+", "TOSS"))
        self.sig_left(ChipSig("-->+", "RWE"))

        self.sig_left(ChipSig("-->+", "SGEXT"))
        self.sig_left(ChipSig("-->+", "DSPL", 0, 15))
        self.sig_left(ChipSig("-->+", "CTL", 0, 2))
        self.sig_left(ChipSig("-->+", "CMR"))
        self.sig_left(ChipSig("-->+", "SVCLK"))
        self.sig_left(ChipSig("-->+", "PDCLK"))
        self.sig_left(ChipSig("-->+", "STCLK"))
        self.sig_left(ChipSig("-->+", "TOPLD"))

        self.sig_left(ChipSig("-->+", "CSA", 0, 3))
        self.sig_left(ChipSig("-->+", "RESDR"))
        self.sig_left(ChipSig("-->+", "BRNC", 0, 2))

        self.sig_right(ChipSig("+<--", "OSPCOE"))
        self.sig_right(ChipSig("+===", "OSPC", 0, 2))
        self.sig_right(ChipSig("+<--", "ADRNOE"))
        self.sig_right(ChipSig("+===", "ADRN", 0, 31))
        self.sig_right(ChipSig("+<--", "NAMOE"))
        self.sig_right(ChipSig("+===", "NAM", 0, 31))

        self.sig_right(ChipSig("+-->", "COUT"))

        self.sig_left(ChipSig("-->+", "Q3COND"))

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

        self.sig_left(ChipSig("-->+", "FCHR"))
        self.sig_left(ChipSig("-->+", "ENFU"))

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

        self.sig_right(ChipSig("+-->", "FNER"))
        self.sig_right(ChipSig("+-->", "FERR"))
        self.sig_right(ChipSig("+-->", "USTOS"))
        self.sig_right(ChipSig("+-->", "IBFIL"))

        # self.sig_right(ChipSig("+-->", "UAD", 0, 15))

        self.finish()

def register():
    yield XSEQIBUF()

