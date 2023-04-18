#!/usr/bin/env python3

''' STK RAM 16x16 '''

from chip import Chip

class XSTKRAM(Chip):

    ''' STK RAM 16x16 '''

    def __init__(self, bits):

        self.symbol_name = "XSTKRAM"
        if bits != 16:
            self.symbol_name += "%d" % bits

        i = []
        i.append('      |   |')
        i.append('      |   |')
        i.append('     %v  %v')
        i.append('   +--o---o--+')
        i.append('   | WE   CS |')
        for j in range(bits):
            i.append('  %|         |%')
            i.append('-->+D%-2d   %3so===' % (j, "Q%d" % j))
        i.append('   |         |')
        i.append('  %|         |')
        i.append('-->+A0       |')
        i.append('  %|         |')
        i.append('-->+A1       |')
        i.append('  %|         |')
        i.append('-->+A2       |')
        i.append('  %|         |')
        i.append('-->+A3       |')
        i.append('   |         |')
        i.append('   |  xnn    |')
        i.append('   |         |')
        i.append('   |  _      |')
        i.append('   +---------+')

        self.symbol = '\n'.join(i)

        super().__init__()

def register():
    yield XSTKRAM(16)
    yield XSTKRAM(20)
    yield XSTKRAM(32)
