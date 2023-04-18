#!/usr/bin/env python3

''' Ucode tracer '''

from chip import Chip

class XUTRACE(Chip):

    ''' Ucode tracer '''

    def __init__(self):
        self.symbol_name = "XUTRACE"

        l = []
        l.append('   +-----------+')
        l.append('   |           |')
        l.append('  %|           |')
        l.append('-->+ CLK       |')

        l.append('   |           |')
        l.append('   |           |')
        for pin in range(14):
            pn = '-->+%-4s' % ("UA%d" % pin)
            l.append('  %|           |')
            l.append(pn + '       |')

        l.append('   |           |')
        l.append('   |           |')
        for pin in range(11):
            pn = '-->+%-4s' % ("ST%d" % pin)
            l.append('  %|           |')
            l.append(pn + '       |')


        l.append('   |           |')
        l.append('   |  xnn      |')
        l.append('   |           |')
        l.append('   | _         |')
        l.append('   +-----------+')

        self.symbol=("\n".join(l))
        super().__init__()

def register():
    yield XUTRACE()
