#!/usr/bin/env python3

''' Double 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

from chip import Chip

class XSRN(Chip):

    ''' Double 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

    def __init__(self, width, parts):

        self.symbol_name = "XSR%dX%d" % (width, parts)

        lines = []
        lines.append('      |  |')
        lines.append('      |  |')
        lines.append('     %v %v')
        lines.append('   +--+--o--+')
        lines.append('   |  v     |')
        lines.append('   | CLK CLR|')

        lines.append('   |        |')
        for i in range(parts):
            lines.append('  %|        |')
            lines.append('-->+R%d      |' % i)

        lines.append('   |        |')
        for i in range(parts * width):
            lines.append('  %|        |%')
            lines.append('-->+D%-2d  %3s+-->' % (i, "Q%d" % i))

        lines.append('   |        |')
        for i in range(parts):
            lines.append('  %|        |%')
            lines.append('-->+L%d    O%d+-->' % (i, i))

        lines.append('   |        |')
        lines.append('  %|        |')
        lines.append('-->+S0      |')
        lines.append('  %|   xnn  |')
        lines.append('-->+S1      |')
        lines.append('   |        |')
        lines.append('   |  _     |')
        lines.append('   +--------+')
        self.symbol = '\n'.join(lines)
        super().__init__()

def register():
    yield XSRN(8,4)
    yield XSRN(8,5)
