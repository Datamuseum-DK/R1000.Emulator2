#!/usr/bin/env python3

''' PAL22V10 - Programmable Logic Device '''

# XXX: Different I/R0 markings on outputs

from chip import Chip

class DRCPAL(Chip):

    ''' PAL22V10 - Programmable Logic Device '''

    symbol_name = "DRCPAL"

    checked = "MEM32 0030"

    symbol = '''
   +----------+
  1|          |
-->+I0/CLK    |
  2|          |23
-->+I1   RO D0+-->
  3|          |22
-->+I2   RO D1+-->
  4|          |21
-->+I3   RO D2+-->
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
-->+I9   RO D8+-->
 11|          |14
-->+I10  RO D9+-->
 13|          |
-->+I11  xnn  |
   |          |
   | _        |
   +----------+
'''

def register():
    yield DRCPAL()
