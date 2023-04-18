#!/usr/bin/env python3

''' PAL22V10 - Programmable Logic Device '''

# XXX: Different I/R0 markings on outputs

from chip import Chip

class CNTRPAL(Chip):

    ''' PAL22V10 - Programmable Logic Device '''

    symbol_name = "CNTRPAL"

    checked = "MEM32 34"

    symbol = '''
   +----------+
  1|          |
-->+I0/CLK    |
  2|          |23
-->+I1   CO D0+-->
  3|          |22
-->+I2   R0 D1+-->
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
-->+I8   R0 D7+-->
 10|          |15
-->+I9   R0 D8+-->
 11|          |14
-->+I10  R0 D9+-->
 13|          |
-->+I11  xnn  |
   |          |
   | _        |
   +----------+
'''

def register():
    yield CNTRPAL()
