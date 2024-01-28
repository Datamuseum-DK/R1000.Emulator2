#!/usr/bin/env python3

''' 74x169 - Synchronous 4-Bit Bidirectional Counters '''

from chip import Chip

class F169(Chip):

    ''' 74x169 - Synchronous 4-Bit Bidirectional Counters '''

    def __init__(self, width):

        self.checked = "TYP 0018"

        lines = []
        if width == 4:
            self.symbol_name = "F169"
            lines.append("      |  |  |")
            lines.append("      |  |  |")
            lines.append("     2v 9v 1v")
            lines.append("   +--+--o--+--+")
            lines.append("   |  v        |")
            lines.append("   | CLK LD UP |")
            lines.append("   |           |15")
            lines.append("   |         COo-->")
            lines.append("  6|           |11")
            lines.append("-->+D0       Q0+-->")
            lines.append("  5|           |12")
            lines.append("-->+D1       Q1+-->")
            lines.append("  4|           |13")
            lines.append("-->+D2       Q2+-->")
            lines.append("  3|           |14")
            lines.append("-->+D3       Q3+-->")
            lines.append("  7|           |")
            lines.append("-->oENP        |")
            lines.append(" 10|           |")
            lines.append("-->oENT xnn    |")
            lines.append("   |           |")
            lines.append("   |    _      |")
            lines.append("   +-----------+")
        else:
            self.symbol_name = "F169X%d" % (width // 4)
            lines.append("      |  |  |")
            lines.append("      |  |  |")
            lines.append("     %v %v %v")
            lines.append("   +--+--o--+--+")
            lines.append("   |  v        |")
            lines.append("   | CLK LD UP |")
            lines.append("   |           |%")
            lines.append("   |         COo-->")
            for i in range(width):
                lines.append("  %|           |%")
                lines.append("-->+D%-2d     %3s+-->" % (i, "Q%d" % i))
            lines.append("  %|           |")
            lines.append("-->oENP        |")
            lines.append("  %|           |")
            lines.append("-->oENT xnn    |")
            lines.append("   |           |")
            lines.append("   |    _      |")
            lines.append("   +-----------+")
    
        self.symbol = "\n".join(lines)

        super().__init__()

def register():
    yield F169(4)
    yield F169(8)
    yield F169(16)
