#!/usr/bin/env python3

''' 74x521 - 8-Bit Comparator, Inverting Output '''

from chip import Chip

class F521(Chip):

    ''' 74x521 - 8-Bit Comparator, Inverting Output '''

    symbol_name = "F521"

    checked = "IOC 0070"

    symbol = '''
      |  ^
      |  |
     1v19|
   +--o--o--+
   |        |
   |  E A=B |
  2|        |3
-->+A0    B0+<--
  4|        |5
-->+A1    B1+<--
  6|        |7
-->+A2    B2+<--
  8|        |9
-->+A3    B3+<--
 11|        |12
-->+A4    B4+<--
 13|        |14
-->+A5    B5+<--
 15|        |16
-->+A6    B6+<--
 17|   xnn  |18
-->+A7    B7+<--
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F521()
