#!/usr/bin/env python3

''' 74x244 - Octal Buffer, Non-Inverting Outputs '''

from chip import Chip

class F244(Chip):

    ''' 74x244 - Octal Buffer, Non-Inverting Outputs '''

    checked = "IOC 0033"

    symbol_name = "F244"

    symbol = '''
      |  |
      |  |
     1v19v
   +--o--o--+
   |        |
   | OE0 OE1|
  2|        |18
-->+I0    Y0+===
  4|        |16
-->+I1    Y1+===
  6|   0    |14
-->+I2    Y2+===
  8|        |12
-->+I3    Y3+===
 11|  ----  |9
-->+I4    Y4+===
 13|        |7
-->+I5    Y5+===
 15|   1    |5
-->+I6    Y6+===
 17|   xnn  |3
-->+I7    Y7+===
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F244()
