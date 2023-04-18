#!/usr/bin/env python3

''' AMD Am2167 - 16,384x1 Static RAM '''

from chip import Chip

class AM2167(Chip):

    ''' AMD Am2167 - 16,384x1 Static RAM '''

    symbol_name = "2167"

    checked = "VAL 0063"

    symbol = '''
      |  |
      |  |
     9v11v
   +--o--o--+
   |  v     |
   | WE  CS |
 12|        |8
-->+D      Q+===
  1|        |13
-->+A0    A7+<--
  2|        |14
-->+A1    A8+<--
  3|        |15
-->+A2    A9+<--
  4|        |16
-->+A3   A10+<--
  5|        |17
-->+A4   A11+<--
  6|        |18
-->+A5   A12+<--
  7|  xnn   |19
-->+A6   A13+<--
   |        |
   |  _     |
   +--------+
'''

def register():
    yield AM2167(__file__)
