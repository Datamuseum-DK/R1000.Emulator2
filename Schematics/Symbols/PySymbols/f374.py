#!/usr/bin/env python3

''' 74x374 - Octal Register '''

from chip import Chip

class F374(Chip):

    ''' 74x374 - Octal Register '''

    symbol_name = "F374"

    checked = "VAL 0069"

    symbol = '''
      |  |
      |  |
    11v 1v
   +--+--o--+
   |  v     |
   | CLK OE |
  3|        |2
-->+D0    Q0+===
  4|        |5
-->+D1    Q1+===
  7|        |6
-->+D2    Q2+===
  8|        |9
-->+D3    Q3+===
 13|        |12
-->+D4    Q4+===
 14|        |15
-->+D5    Q5+===
 17|        |16
-->+D6    Q6+===
 18|   xnn  |19
-->+D7    Q7+===
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F374()
