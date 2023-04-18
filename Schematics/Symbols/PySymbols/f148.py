#!/usr/bin/env python3

''' 74x148 - 8-Line to 3-Line Priority Encoder '''

from chip import Chip

class F148(Chip):

    ''' 74x148 - 8-Line to 3-Line Priority Encoder '''

    symbol_name = "F148"

    checked = "VAL 0019"

    symbol = '''
       |
       |
      5v
   +---o---+
   |       |
   |   E   |
  4|       |14
-->oI0   GSo-->
  3|       |15
-->oI1   EZo-->
  2|       |
-->oI2     |
  1|       |6
-->oI3   Y0+-->
 13|       |7
-->oI4   Y1+-->
 12|       |9
-->oI5   Y2+-->
 11|       |
-->oI6     |
 10|       |
-->oI7 xnn |
   |       |
   | _     |
   +-------+

'''

class F148X2(Chip):

    ''' Double 74x148 - 8-Line to 3-Line Priority Encoder '''

    symbol_name = "F148X2"

    symbol = '''
       |
       |
      %v
   +---o---+
   |       |
   |   E   |
  %|       |%
-->oI0   GSo-->
  %|       |%
-->oI1   EZo-->
  %|       |
-->oI2     |
  %|       |%
-->oI3   Y0+-->
  %|       |%
-->oI4   Y1+-->
  %|       |%
-->oI5   Y2+-->
  %|       |%
-->oI6   Y3+-->
  %|       |
-->oI7     |
  %|       |
-->oI8     |
  %|       |
-->oI9     |
  %|       |
-->oI10    |
  %|       |
-->oI11    |
  %|       |
-->oI12    |
  %|       |
-->oI13    |
  %|       |
-->oI14    |
  %|   xnn |
-->oI15    |
   |       |
   | _     |
   +-------+
'''

def register():
    yield F148()
    yield F148X2()
