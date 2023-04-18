#!/usr/bin/env python3

''' 74x258 - Quad 2-Line to 1-Line Multiplxer, Inverting Outputs'''

from chip import Chip

class F258(Chip):

    ''' 74x258 - Quad 2-Line to 1-Line Multiplxer, Inverting Outputs'''

    symbol_name = "F258"

    checked = "MEM32 0018"

    symbol = '''
      |  |
      |  |
     1v15v
   +--+--o--+
   |        |
   |  S  OE |
  2|        |
-->+A0      |4
  5|      Y0o===
-->+A1      |
 11|        |
-->+A2      |7
 14|      Y1o===
-->+A3      |
  3|        |
-->+B0      |9
  6|      Y2o===
-->+B1      |
 10|        |
-->+B2      |12
 13|      Y3o===
-->+B3 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F258()
