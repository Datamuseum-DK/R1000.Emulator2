#!/usr/bin/env python3

''' 8x8 parity generator '''

from chip import Chip

class XHASH(Chip):

    ''' mem32 hash generator '''

    def __init__(self):
        self.symbol_name = "XHASH"

        l = []
        l.append('   +-----------+')

        hash = [-3]
        def sect(let, low, pins):
            # l.append('   |           |')
            for pin in range(low, low + pins):
                pn = '-->+%-3s' % (let + "%d" % pin)
                if 0 <= hash[0] < 12:
                    l.append('  %|           |%')
                    l.append(pn + '  %6s+-->' % ("H%d" % hash[0]))
                elif 24 <= pin <= 27:
                    l.append('  %|           |%')
                    l.append(pn + '      B%d+-->' % (pin - 24))
                else:
                    l.append('  %|           |')
                    l.append(pn + '        |')
                hash[0] += 1
            l.append('   |           |')
            l.append('   |           |')
            l.append('   |           |')
            l.append('   |           |')

        sect("S", 0, 3)
        sect("A", 0, 32 + 24)
        l.append('   |  xnn      |')
        l.append('   |           |')
        l.append('   | _         |')
        l.append('   +-----------+')

        self.symbol=("\n".join(l))
        super().__init__()

def register():
    yield XHASH()
