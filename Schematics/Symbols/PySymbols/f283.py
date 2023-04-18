#!/usr/bin/env python3

''' 74x283 - 4-Bit Binary Full Adder With Carry Function'''

from chip import Chip

class F283(Chip):

    ''' 74x283 - 4-Bit Binary Full Adder With Carry Function'''

    symbol_name = "F283"

    checked = "VAL 0036"

    symbol = '''
   +-------+
  7|       |9
-->+CI   CO+-->
 12|       |
-->+A0     |
 14|       |
-->+A1     |
  3|       |10
-->+A2   Y0+-->
  5|       |13
-->+A3   Y1+-->
 11|       |1
-->+B0   Y2+-->
 15|       |4
-->+B1   Y3+-->
  2|       |
-->+B2     |
  6|       |
-->+B3 xnn |
   |       |
   |  _    |
   +-------+
'''

def register():
    yield F283()
