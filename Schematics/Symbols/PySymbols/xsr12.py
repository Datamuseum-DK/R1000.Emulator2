#!/usr/bin/env python3

''' Tripple 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

from chip import Chip

class XSR12(Chip):

    ''' Tripple 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

    symbol_name = "XSR12"

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
  7|        |19
-->+D0    Q0+-->
  8|        |20
-->+D1    Q1+-->
  9|        |21
-->+D2    Q2+-->
 10|        |22
-->+D3    Q3+-->
 11|        |23
-->+D4    Q4+-->
 12|        |24
-->+D5    Q5+-->
 13|        |25
-->+D6    Q6+-->
 14|        |26
-->+D7    Q7+-->
 15|        |27
-->+D8    Q8+-->
 16|        |28
-->+D9    Q9+-->
 17|        |29
-->+D10  Q10+-->
 18|        |30
-->+D11  Q11+-->
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
    yield XSR12()
