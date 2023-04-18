#!/usr/bin/env python3

''' 74x157 - Quad 2-Line to 1-Line Multiplxer, Non-Inverting Outputs'''

from chip import Chip

class F157(Chip):

    ''' 74x157 - Quad 2-Line to 1-Line Multiplxer, Non-Inverting Outputs'''

    symbol_name = "F157"

    checked = "FIU 0039"

    symbol = '''
      |  |
      |  |
     1v15v
   +--+--o--+
   |        |
   |  S  E  |
  2|        |
-->+A0      |4
  5|      Y0+-->
-->+A1      |
 11|        |
-->+A2      |7
 14|      Y1+-->
-->+A3      |
  3|        |
-->+B0      |9
  6|      Y2+-->
-->+B1      |
 10|        |
-->+B2      |12
 13|      Y3+-->
-->+B3 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F157()
