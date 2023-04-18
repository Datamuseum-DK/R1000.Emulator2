#!/usr/bin/env python3

''' 82S147 - 512x8 PROM '''

from chip import Chip

class PAxxxNZ(Chip):

    ''' 82S147 - 512x8 PROM '''

    symbol_name = "PAxxxNZ"

    checked = "IOC 0014"

    symbol = '''
   +-------+
 19|    =0 |
-->+A0  OE |
 18|       |14
-->+A1   Y0+-->
 17|       |13
-->+A2   Y1+-->
 16|       |12
-->+A3   Y2+-->
  5|       |11
-->+A4   Y3+-->
  4|       |9
-->+A5   Y4+-->
  3|       |8
-->+A6   Y5+-->
  2|       |7
-->+A7   Y6+-->
  1|  xnn  |6
-->+A8   Y7+-->
   |       |
   | _     |
   +-------+
'''

def register():
    yield PAxxxNZ()
