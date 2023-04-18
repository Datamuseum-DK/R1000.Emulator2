#!/usr/bin/env python3

''' Quad 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

from chip import Chip

class XSR16(Chip):

    ''' Quad 74x194 - 4-Bit Bidirectional Universal Shift Registers '''

    symbol_name = "XSR16"

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
  7|        |23
-->+D0    Q0+-->
  8|        |24
-->+D1    Q1+-->
  9|        |25
-->+D2    Q2+-->
 10|        |26
-->+D3    Q3+-->
 11|        |27
-->+D4    Q4+-->
 12|        |28
-->+D5    Q5+-->
 13|        |29
-->+D6    Q6+-->
 14|        |30
-->+D7    Q7+-->
 15|        |31
-->+D8    Q8+-->
 16|        |32
-->+D9    Q9+-->
 17|        |33
-->+D10  Q10+-->
 18|        |34
-->+D11  Q11+-->
 19|        |35
-->+D12  Q12+-->
 20|        |36
-->+D13  Q13+-->
 21|        |37
-->+D14  Q14+-->
 22|        |38
-->+D15  Q15+-->
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
    yield XSR16()
