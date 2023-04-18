#!/usr/bin/env python3

''' PAL16L8 - Programmable Logic Device '''

from chip import Chip

class DIBRPAL(Chip):

    ''' PAL16L8 - Programmable Logic Device '''

    symbol_name = "DIBRPAL"

    checked = "MEM32 0028"

    symbol = '''
   +--------+
  1|        |
-->+I0      |
  2|        |19
-->+I1    O0+-->
  3|        |12
-->+I2    O1+-->
  4|        |18
-->+I3    D0+===
  5|        |17
-->+I4    D1+===
  6|        |16
-->+I5      +<--
  7|        |15
-->+I6      +<--
  8|        |14
-->+I7      +<--
  9|        |13
-->+I8      +<--
 11|        |
-->+I9 xnn  |
   |        |
   | _      |
   +--------+
'''

def register():
    yield DIBRPAL()
