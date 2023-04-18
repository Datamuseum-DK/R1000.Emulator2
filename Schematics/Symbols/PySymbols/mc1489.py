#!/usr/bin/env python3

''' MC1489 - Quadruple Line Receiver '''

from chip import Chip

class MC1489(Chip):

    ''' MC1489 - Quadruple Line Receiver '''

    symbol_name = "1489"

    checked = "IOC 0019"

    symbol = '''
   +--------+
   |        |
   |        |
  1|        |
-->+IN0     | 3
  2|      Y0o-->
-->+RC0     |
  4|        |
-->+IN1     | 6
  5|      Y1o-->
-->+RC1     |
 10|        |
-->+IN2     | 8
  9|      Y2o-->
-->+RC2     |
 13|    xnn |
-->+IN3     |11
 12|      Y3o-->
-->+RC3     |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield MC1489(__file__)
