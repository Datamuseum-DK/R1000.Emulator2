#!/usr/bin/env python3

''' N bit two input mux with common select '''

from chip import Chip

class XADD(Chip):

    ''' N bit two input mux with common select '''

    def __init__(self, npins, bname):
        self.xreg_npins = npins
        self.symbol_name = bname + "%d" % npins
        self.symbol = ''
        self.symbol += '   +--------+\n'
        self.symbol += '  %|        |%\n'
        self.symbol += '-->+CI    CO+-->\n'
        self.symbol += '   |        |\n'

        for i in range(npins):
            self.symbol += '  %|        |\n'
            self.symbol += '-->+%-4s    |\n' % ("A%d" % i)
        self.symbol += '   |        |\n'
        for i in range(npins):
            if i == npins - 1:
                self.symbol += '  %|  xnn   |%\n'
            else:
                self.symbol += '  %|        |%\n'
            self.symbol += '-->+%-3s  %3s+-->\n' % (("B%d" % i), ("Y%d" % i))
        self.symbol += '   |  _     |\n'
        self.symbol += '   +--------+\n'
        super().__init__()

def register():
    yield XADD(8, "XADD")
    yield XADD(8, "XSUB")
    yield XADD(14, "XADD")
