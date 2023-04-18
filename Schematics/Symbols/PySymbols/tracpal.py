#!/usr/bin/env python3

''' PAL22V10 - Programmable Logic Device '''

# XXX: Different I/R0 markings on outputs

from chip import Chip

class TRACPAL(Chip):

    ''' PAL22V10 - Programmable Logic Device '''

    symbol_name = "TRACPAL"

    checked = "MEM32 34"

    symbol = '''
   +----------+
  1|          |
-->+I0/CLK    |
  2|          |23
-->+I1      D0+-->
  3|          |22
-->+I2      D1+-->
  4|          |21
-->+I3      D2+-->
  5|          |20
-->+I4      D3+-->
  6|          |19
-->+I5      D4+-->
  7|          |18
-->+I6      D5+-->
  8|          |17
-->+I7      D6+-->
  9|          |16
-->+I8      D7+-->
 10|          |15
-->+I9      D8+-->
 11|          |14
-->+I10     D9+-->
 13|          |
-->+I11  xnn  |
   |          |
   | _        |
   +----------+
'''

def register():
    yield TRACPAL()
