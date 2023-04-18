#!/usr/bin/env python3

''' Xicor 2212 - 256 x 4 NOVRAM '''

from chip import Chip

class X2212(Chip):

    ''' Xicor 2212 - 256 x 4 NOVRAM '''

    symbol_name = "NOVRAM"

    checked = "VAL 0069"

    symbol = '''
      |  |
      |  |
    11v 7v
   +--o--o--+
   |  v     |
   |  WE CS |
 10|        |
-->oRECALL  |
  9|        |
-->oSTORE   |
  6|        |
-->+A0      |
  5|        |15
-->+A1   DQ0+<->
  4|        |14
-->+A2   DQ1+<->
  3|        |13
-->+A3   DQ2+<->
  8|        |12
-->+A4   DQ3+<->
 16|        |
-->+A5      |
 17|        |
-->+A6      |
  1|        |
-->+A7 xnn  |
   |        |
   | _      |
   +--------+
'''

def register():
    yield X2212(__file__)
