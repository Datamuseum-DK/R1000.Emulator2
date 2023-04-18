#!/usr/bin/env python3

''' PAL16L8 - Programmable Logic Device '''

# Different CO/I markings

from chip import Chip

class CMDPAL(Chip):

    ''' PAL16L8 - Programmable Logic Device '''

    symbol_name = "CMDPAL"

    checked = "MEM32 28"

    symbol = '''
   +--------+
  1|        |
-->+I0      |
  2|        |19
-->+I1    O0+-->
  3|        |12
-->+I2    O1+-->
  4|        |18
-->+I3 CO D0+-->
  5|        |17
-->+I4 CO D1+-->
  6|        |16
-->+I5 CO D2+-->
  7|        |15
-->+I6 CO D3+-->
  8|        |14
-->+I7 CO D4+-->
  9|        |13
-->+I8  I D5+<--
 11|        |
-->+I9 xnn  |
   |        |
   | _      |
   +--------+
'''

def register():
    yield CMDPAL()
