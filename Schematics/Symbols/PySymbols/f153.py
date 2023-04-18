#!/usr/bin/env python3

''' 74x153 - Dual 4-Line to 1-Line Multiplexer '''

from chip import Chip

class F153(Chip):

    ''' 74x153 - Dual 4-Line to 1-Line Multiplexer '''

    symbol_name = "F153"

    checked = "IOC 0071"

    symbol = '''
      |  |
      |  |
     2v14v
   +--+--+--+
   |        |
   | S0  S1 |
  6|        |1
-->+A0    E0o<--
  5|        |15
-->+B0    E1o<--
  4|        |
-->+C0      |
  3|        |7
-->+D0    Y0+-->
 10|        |9
-->+A1    Y1+-->
 11|        |
-->+B1      |
 12|        |
-->+C1      |
 13|        |
-->+D1 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F153()
