#!/usr/bin/env python3

''' 74x240 - Octal Buffers, Inverting Outputs '''

from chip import Chip

class F240(Chip):

    ''' 74x240 - Octal Buffers, Inverting Outputs '''

    symbol_name = "F240"

    checked = "RESHA 0002"

    symbol = '''
      |  |
      |  |
     1v19v
   +--o--o--+
   |        |
   | OE0 OE1|
  2|        |18
-->+I0    Y0o===
  4|        |16
-->+I1    Y1o===
  6|   0    |14
-->+I2    Y2o===
  8|        |12
-->+I3    Y3o===
 11|  ----  |9
-->+I4    Y4o===
 13|        |7
-->+I5    Y5o===
 15|   1    |5
-->+I6    Y6o===
 17|   xnn  |3
-->+I7    Y7o===
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F240()
