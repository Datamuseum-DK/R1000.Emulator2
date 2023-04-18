#!/usr/bin/env python3

''' PAL16L8 - Programmable Logic Device '''

# Different CO/I markings

from chip import Chip

class PAL16L8(Chip):

    ''' PAL16L8 - Programmable Logic Device '''

    symbol_name = "PAL16L8"

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
-->+I3    D0+-->
  5|        |17
-->+I4    D1+-->
  6|        |16
-->+I5    D2+-->
  7|        |15
-->+I6    D3+-->
  8|        |14
-->+I7    D4+<--
  9|        |13
-->+I8    D5+<--
 11|        |
-->+I9 xnn  |
   |        |
   | _      |
   +--------+
'''

def register():
    yield PAL16L8()
