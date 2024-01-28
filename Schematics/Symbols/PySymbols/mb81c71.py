#!/usr/bin/env python3

''' Fujitsu MB81C71 - CMOS 64K-Bit High-Speed SRAM '''

from chip import Chip

class MB81C71(Chip):

    ''' Fujitsu MB81C71 - CMOS 64K-Bit High-Speed SRAM '''

    symbol_name = "64KX1"

    checked = "IOC 0040"

    symbol = '''

   +------+
  1|      |14
-->+A0  A8+<--
  2|      |15
-->+A1  A9+<--
  3|      |16
-->+A2 A10+<--
  4|      |17
-->+A3 A11+<--
  5|      |18
-->+A4 A12+<--
  6|      |19
-->+A5 A13+<--
  7|      |20
-->+A6 A14+<--
  8|      |21
-->+A7 A15+<--
   |      |
 13|  xnn |9
-->+D    Q+===
 12|      |10
-->oCS  WEo<--
   |      |
   | _    |
   +------+

'''

def register():
    yield MB81C71(__file__)
