#!/usr/bin/env python3

''' 74x175 - Quadrupe D-Type Flip-Flops With Clear '''

from chip import Chip

class F175(Chip):

    ''' 74x175 - Quadrupe D-Type Flip-Flops With Clear '''

    symbol_name = "F175"

    checked = "VAL 0069"

    symbol = '''
      |  |
      |  |
     9v 1v
   +--+--o--+
   |  v     |
   | CLK CLR|
  4|        | 2
-->+D0    Q0+-->
   |        | 3
   |     Q0~o-->
  5|        | 7
-->+D1    Q1+-->
   |        | 6
   |     Q1~o-->
 12|        |10
-->+D2    Q2+-->
   |        |11
   |     Q2~o-->
 13|        |15
-->+D3    Q3+-->
   |        |14
   |  xnnQ3~o-->
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F175()
