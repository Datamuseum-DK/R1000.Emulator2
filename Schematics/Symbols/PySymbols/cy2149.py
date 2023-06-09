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


class CY2149X2(Chip):

    ''' Cypress CY2149 - 1,024x4 Static R/W RAM '''

    symbol_name = "2149X2"

    checked = "VAL 0026"

    symbol = '''
      |  |
      |  |
     %v %v
   +--o--o--+
   |  v     |
   |  WE CS |
  %|        |
-->+A0      |
  %|        |%
-->+A1   DQ0+<->
  %|        |%
-->+A2   DQ1+<->
  %|        |%
-->+A3   DQ2+<->
  %|        |%
-->+A4   DQ3+<->
  %|        |%
-->+A5   DQ4+<->
  %|        |%
-->+A6   DQ5+<->
  %|        |%
-->+A7   DQ6+<->
  %|        |%
-->+A8   DQ7+<->
  %|        |
-->+A9 xnn  |
   |        |
   |  _     |
   +--------+
'''


class CY2149X4(Chip):

    ''' Cypress CY2149 - 1,024x4 Static R/W RAM '''

    symbol_name = "2149X4"

    symbol = '''
      |  |
      |  |
     %v %v
   +--o--o--+
   |  v     |
   |  WE CS |
  %|        |
-->+A0      |
  %|        |%
-->+A1   DQ0+<->
  %|        |%
-->+A2   DQ1+<->
  %|        |%
-->+A3   DQ2+<->
  %|        |%
-->+A4   DQ3+<->
  %|        |%
-->+A5   DQ4+<->
  %|        |%
-->+A6   DQ5+<->
  %|        |%
-->+A7   DQ6+<->
  %|        |%
-->+A8   DQ7+<->
  %|        |%
-->+A9   DQ8+<->
   |        |%
   |     DQ9+<->
   |        |%
   |    DQ10+<->
   |        |%
   |    DQ11+<->
   |        |%
   |    DQ12+<->
   |        |%
   |    DQ13+<->
   |        |%
   |    DQ14+<->
   |        |%
   |    DQ15+<->
   |        |
   |        |
   |  xnn   |
   |        |
   |  _     |
   +--------+
'''


def register():
    yield CY2149(__file__)
    yield CY2149X2(__file__)
    yield CY2149X4(__file__)
