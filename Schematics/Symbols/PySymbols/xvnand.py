#!/usr/bin/env python3

''' 32 bit '374-style register '''

from chip import Chip

class XVNAND(Chip):

    ''' Vector of NAND '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XVNAND%d" % npins
        self.symbol = ''
        self.symbol += '   +-----------+\n'
        self.symbol += '   |           |\n'

        for i in range(1, npins + 1):
            self.symbol += '  %|           |%\n'
            self.symbol += '-->+%-4s       |\n' % ("A%d" % (i-1))

        self.symbol += '   |           |\n'
        self.symbol += '   |           |\n'

        for i in range(1, npins + 1):
            if i == npins:
                self.symbol += '  %|    xnn    |%\n'
            else:
                self.symbol += '  %|           |%\n'
            self.symbol += '-->+%-4s   %4so-->\n' % ("B%d" % (i-1), "Q%d" % (i-1))
        self.symbol += '   |           |\n'
        self.symbol += '   |  _        |\n'
        self.symbol += '   +-----------+\n'
        super().__init__()

def register():
    yield XVNAND(7)
    yield XVNAND(12)
    yield XVNAND(14)
    yield XVNAND(16)
