#!/usr/bin/env python3

''' 74x182 - Carry Lookahead Generator '''

from chip import Chip

class F182(Chip):

    ''' 74x182 - Carry Lookahead Generator '''

    symbol_name = "F182"

    checked = "VAL 0036"

    symbol = '''
   +-------+
 13|       |7
-->oCI   CP+-->
  4|       |10
-->+P3   CG+-->
  3|       |
-->+G3     |
 12|       |
<--oCO3    |
  2|       |
-->+P2     |
  1|       |
-->+G2     |
 11|       |
<--oCO2    |
 15|       |
-->+P1     |
 14|       |
-->+G1     |
  9|       |
<--oCO1    |
  6|       |
-->+P0     |
  5|       |
-->+G0 xnn |
   |       |
   |  _    |
   +-------+
'''

def register():
    yield F182()
