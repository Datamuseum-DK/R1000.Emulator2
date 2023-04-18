#!/usr/bin/env python3

''' MC1488 - Quadrupe Line Driver '''

from chip import Chip

class MC1488(Chip):

    ''' MC1488 - Quadrupe Line Driver '''

    symbol_name = "1488"

    checked = "RESHA 0010"

    symbol = '''
      ^   ^
      |   |
     1v 14v
   +--+---+-+
   |        |
   | VEE VCC|
   |        |
  2|        |3
-->+I0    Y0o-->
   |        |
  4|        |
-->+I1A     | 6
  5|      Y1o-->
-->+I1B     |
 10|        |
-->+I2A     | 8
  9|      Y2o-->
-->+I2B     |
 13|    xnn |
-->+I3A     |11
 12|      Y3o-->
-->+I3B     |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield MC1488(__file__)
