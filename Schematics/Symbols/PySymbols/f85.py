#!/usr/bin/env python3

''' 74x85 - 4-Bit Magnitude Comparator '''

from chip import Chip

class F85(Chip):

    ''' 74x85 - 4-Bit Magnitude Comparator '''

    symbol_name = "F85"

    checked = "IOC 0070"

    symbol = '''
   +-------+
 15|       |4
-->+A0   E>+<--
 13|       |3
-->+A1   E=+<--
 12|       |2
-->+A2   E<+<--
 10|       |
-->+A3     |
  1|       |5
-->+B0  A>B+-->
 14|       |6
-->+B1  A=B+-->
 11|       |7
-->+B2  A<B+-->
  9|       |
-->+B3 xnn |
   |       |
   |  _    |
   +-------+
'''

def register():
    yield F85()
