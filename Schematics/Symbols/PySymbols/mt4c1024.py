#!/usr/bin/env python3

''' MT4C1024 - 1048576-Bit Dynamic Random-Access Memory '''

from chip import Chip

class MT4C1024(Chip):

    ''' MT4C1024 - 1048576-Bit Dynamic Random-Access Memory '''

    symbol_name = "1MEG"

    checked = "MEM32 0034"

    symbol = '''
   +------+
  4|      |
   |NC    | 3
 15|   RASo<--
-->+A1    |16
 14|   CASo<--
-->+A2    | 2
 13|    WEo<--
-->+A3    |
 12|      |
-->+A4    | 1
 11|     D+<--
-->+A5    |
 10|      |
-->+A6    |17
  8|     Q+===
-->+A7    |
  7|      |
-->+A8    |
  6|      |
-->+A9    |
  5|   xnn|
-->+A10   |
   |      |
   | _    |
   +------+
'''

def register():
    yield MT4C1024(__file__)
