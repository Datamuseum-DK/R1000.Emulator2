#!/usr/bin/env python3

''' IOP's 128KX36 RAM '''

from chip import Chip

class XIOPRAM(Chip):

    ''' IOP's 128KX36 RAM '''

    def __init__(self, npin):
        self.symbol_name = "XIOPRAM%d" % npin
        self.symbol = ''
        self.symbol += '   +---------+\n'
        self.symbol += '   |         |\n'

        for i in range(8):
            self.symbol += '  %|         |%\n'
            self.symbol += '-->+%-4s %4s+<--\n' % ("A%d" % i, "A%d" % (i + 8))
        self.symbol += '   |         |%\n'
        self.symbol += '   |      A16+<--\n'

        self.symbol += '   |         |\n'
        self.symbol += '  %|         |%\n'
        self.symbol += '-->oCS    WE0o<--\n'
        self.symbol += '   |         |%\n'
        self.symbol += '   |      WE1o<--\n'
        self.symbol += '   |         |%\n'
        self.symbol += '   |      WE2o<--\n'
        self.symbol += '   |         |%\n'
        self.symbol += '   |      WE3o<--\n'
        self.symbol += '   |         |\n'

        for i in range(npin):
            self.symbol += '  %|         |%\n'
            self.symbol += '-->+%-4s %4s+-->\n' % ("D%d" % i, "Q%d" % i)

        self.symbol += '   |         |\n'
        self.symbol += '   |         |\n'
        self.symbol += '   | xnn     |\n'
        self.symbol += '   |         |\n'
        self.symbol += '   |  _      |\n'
        self.symbol += '   +---------+\n'
        super().__init__()

#!/usr/bin/env python3

''' IOP's 128KX32 RAM '''

from chip import Chip, FChip, ChipSig

class XCPURAM(FChip):

    ''' R1000 access to IOP RAM '''

    def __init__(self):
        self.symbol_name = "XCPURAM"
        super().__init__()

        self.sig_left(ChipSig("-->+", "ITYP", 0, 63))
        self.sig_right(ChipSig("+===", "OTYP", 0, 31))
        self.sig_right(ChipSig("+<--", "OE"))
        self.sig_right(ChipSig("+<--", "SCLK"))
        self.sig_right(ChipSig("+<--", "INCA"))
        self.sig_right(ChipSig("+<--", "LDA"))
        self.sig_right(ChipSig("+-->", "OFLO"))
        self.sig_right(ChipSig("+<--", "WR"))
        self.sig_right(ChipSig("+<--", "RD"))
        self.sig_right(ChipSig("+<--", "DGENA"))

        self.finish()

def register():
    yield XIOPRAM(4)
    yield XIOPRAM(32)
    yield XCPURAM()


