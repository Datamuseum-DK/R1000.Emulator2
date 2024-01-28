#!/usr/bin/env python3

''' National DS8641 - Quad Unified Bus Tranceiver '''

from chip import Chip

class DS8641(Chip):

    ''' National DS8641 - Quad Unified Bus Tranceiver '''

    symbol_name = "8641"

    checked = "RESHA 0002"

    symbol = '''
      ^  ^  ^  ^
      |  |  |  |
    15v12v 1v 4v
   +--o--o--o--o--+
   |              |
   | B0 B1 B2 B3  |
 14|              |13
-->+IN0       OUT0+-->
 11|              |10
-->+IN1       OUT1+-->
  2|              |3
-->+IN2       OUT2+-->
  5|              |6
-->+IN3       OUT3+-->
   |              |
   |              |
  7|              |
-->oEN0           |
  9|     xnn      |
-->oEN1           |
   |     _        |
   |              |
   +--------------+
'''


class DS8641XN(Chip):

    ''' National DS8641 - Quad Unified Bus Tranceiver '''

    def __init__(self, npins):
        self.npins = npins

        self.symbol_name = "8641X%d" % npins

        self.symbol = ""

        self.symbol += "   +--------------+\n"
        self.symbol += "   |              |\n"
        for i in range(npins):
            self.symbol += "  %|              |%\n"
            self.symbol += "-->+IN%-2d     %-5s+-->\n" % (i, "OUT%d" % i)
        self.symbol += "   |              |\n"
        self.symbol += "   |              |\n"

        for i in range(npins):
            if i == npins - 2:
                self.symbol += "  %|              |%\n"
                self.symbol += "-->oEN0       %4so<->\n" % ("B%d" % i)
            elif i == npins - 1:
                self.symbol += "  %|     xnn      |%\n"
                self.symbol += "-->oEN1       %4so<->\n" % ("B%d" % i)
            else:
                self.symbol += "   |              |%\n"
                self.symbol += "   |          %4so<->\n" % ("B%d" % i)

        self.symbol += "   |     _        |\n"
        self.symbol += "   |              |\n"
        self.symbol += "   +--------------+\n"

        super().__init__()

def register():
    yield DS8641(__file__)
