#!/usr/bin/env python3

''' AMD Am93S48 - Twelve-Input Parity Checker/Generator '''

from chip import Chip

class AM93S48(Chip):

    ''' AMD Am93S48 - Twelve-Input Parity Checker/Generator '''

    symbol_name = "93S48"

    checked = "IOC 0033"

    symbol = '''
   +-------+
   |       |
 11|       |
-->+I0     |
 12|       |
-->+I1     |
 13|       |
-->+I2     |
 14|       |
-->+I3     |
 15|       |10
-->+I4  PEV+-->
  1|       |
-->+I5     |
  2|       |9
-->+I6  POD+-->
  3|       |
-->+I7     |
  4|       |
-->+I8     |
  5|       |
-->+I9     |
  6|       |
-->+I10    |
  7|   xnn |
-->+I11    |
   |       |
   | _     |
   +-------+
'''

def register():
    yield AM93S48(__file__)
