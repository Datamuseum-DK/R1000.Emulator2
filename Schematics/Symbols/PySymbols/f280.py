#!/usr/bin/env python3

''' 74x280 - 9-Bit Odd/Even Parity Generator/Checker '''

from chip import Chip

class F280(Chip):

    ''' 74x280 - 9-Bit Odd/Even Parity Generator/Checker '''

    symbol_name = "F280"

    checked = "IOC 0059"

    symbol = '''
   +-------+
   |       |
  8|       |
-->+I0     |
  9|       |
-->+I1     |
 10|       |5
-->+I2  PEV+-->
 11|       |
-->+I3     |
 12|       |6
-->+I4  POD+-->
 13|       |
-->+I5     |
  1|       |
-->+I6     |
  2|       |
-->+I7     |
  4|       |
-->+I8 xnn |
   |       |
   | _     |
   +-------+
'''

def register():
    yield F280()
