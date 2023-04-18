#!/usr/bin/env python3

''' 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

from chip import Chip

class F194(Chip):

    ''' 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

    symbol_name = "F194"

    checked = "IOC 0060"

    symbol = '''
      |  |
      |  |
    11v 1v
   +--+--o--+
   |  v     |
   | CLK CLR|
  2|        |
-->+RSI     |
  3|        |15
-->+D0    Q0+-->
  4|        |14
-->+D1    Q1+-->
  5|        |13
-->+D2    Q2+-->
  6|        |12
-->+D3    Q3+-->
  7|        |
-->+LSI     |
   |        |
   |        |
  9|        |
-->+S0      |
 10|        |
-->+S1 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F194()
