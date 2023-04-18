#!/usr/bin/env python3

''' PAL16R8 - Programmable Logic Device '''

from chip import Chip

class DISTPAL(Chip):

    ''' PAL16R8 - Programmable Logic Device '''

    symbol_name = "DISTPAL"

    symbol = '''
      |  |
      |  |
     1v11v
   +--+--o--+
   |  v     |
   | CLK OE |
  2|        |19
-->+I0    Q0+-->
  3|        |18
-->+I1    Q1+-->
  4|        |17
-->+I2    Q2+-->
  5|        |16
-->+I3    Q3+-->
  6|        |15
-->+I4      +<--
  7|        |14
-->+I5      +<--
  8|        |13
-->+I6      +<--
  9|   xnn  |12
-->+I7      +<--
   |        |
   | _      |
   +--------+
'''

def register():
    yield DISTPAL()
