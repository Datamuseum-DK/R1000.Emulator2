#!/usr/bin/env python3

''' Double 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

from chip import Chip

class XSR8(Chip):

    ''' Double 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

    symbol_name = "XSR8"

    checked = "IOC 0060"

    symbol = '''
      |  |
      |  |
     1v 2v
   +--+--o--+
   |  v     |
   | CLK CLR|
  3|        |
-->+RSI     |
   |        |
  7|        |15
-->+D0    Q0+-->
  8|        |16
-->+D1    Q1+-->
  9|        |17
-->+D2    Q2+-->
 10|        |18
-->+D3    Q3+-->
 11|        |19
-->+D4    Q4+-->
 12|        |20
-->+D5    Q5+-->
 13|        |21
-->+D6    Q6+-->
 14|        |22
-->+D7    Q7+-->
   |        |
  4|        |
-->+LSI     |
   |        |
   |        |
  5|        |
-->+S0      |
  6|   xnn  |
-->+S1      |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield XSR8()
