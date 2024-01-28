#!/usr/bin/env python3

''' Cypress CY2149 - 1,024x4 Static R/W RAM '''

from chip import Chip

class CY2149(Chip):

    ''' Cypress CY2149 - 1,024x4 Static R/W RAM '''

    symbol_name = "2149"

    checked = "VAL 0026"

    symbol = '''
      |  |
      |  |
    10v 8v
   +--o--o--+
   |  v     |
   |  WE CS |
  5|        |
-->+A0      |
  6|        |
-->+A1      |
  7|        |
-->+A2      |
  4|        |14
-->+A3   DQ0+<->
  3|        |13
-->+A4   DQ1+<->
  2|        |12
-->+A5   DQ2+<->
  1|        |11
-->+A6   DQ3+<->
 17|        |
-->+A7      |
 16|        |
-->+A8      |
 15|        |
-->+A9 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield CY2149(__file__)
