#!/usr/bin/env python3

''' 74x174 - Hex D-Type Flip-Flops with Clear '''

from chip import Chip

class F174(Chip):

    ''' 74x174 - Hex D-Type Flip-Flops with Clear '''

    symbol_name = "F174"

    checked = "VAL 0069"

    symbol = '''
      |  |
      |  |
     9v 1v
   +--+--o--+
   |  v     |
   | CLK CLR|
  3|        |2
-->+D0    Q0+-->
  4|        |5
-->+D1    Q1+-->
  6|        |7
-->+D2    Q2+-->
 11|        |10
-->+D3    Q3+-->
 13|        |12
-->+D4    Q4+-->
 14|   xnn  |15
-->+D5    Q5+-->
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F174()
