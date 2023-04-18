#!/usr/bin/env python3

''' PAL22V10 - Programmable Logic Device '''

# XXX: Different I/R0 markings on outputs

from chip import Chip

class TAGAPAL(Chip):

    ''' PAL22V10 - Programmable Logic Device '''

    symbol_name = "TAGAPAL"

    checked = "MEM32 28"

    symbol = '''
   +----------+
  1|          |
-->+I0/CLK    |
  2|          |23
-->+I1   I  D0+<--
  3|          |22
-->+I2   I  D1+<--
  4|          |21
-->+I3   I  D2+<--
  5|          |20
-->+I4   RO D3+-->
  6|          |19
-->+I5   RO D4+-->
  7|          |18
-->+I6   RO D5+-->
  8|          |17
-->+I7   R0 D6+-->
  9|          |16
-->+I8   RO D7+-->
 10|          |15
-->+I9   I  D8+<--
 11|          |14
-->+I10  I  D9+<--
 13|          |
-->+I11  xnn  |
   |          |
   | _        |
   +----------+
'''

def register():
    yield TAGAPAL()
