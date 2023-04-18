#!/usr/bin/env python3

''' AMD Am25S10 - Four-Bit Shifter with Three-State Outputs '''

from chip import Chip

class AM25S10(Chip):

    ''' AMD Am25S10 - Four-Bit Shifter with Three-State Outputs '''

    symbol_name = "25S10"

    checked = "FIU 0025"

    symbol = '''
     |  |  |
     |  |  |
    9v10v13v
   +-+--+--o-+
   |         |
   | S0 S1 OE|
  1|         |
-->+I-3      |
  2|         |
-->+I-2      |
  3|         |
-->+I-1      |
  4|         |15
-->+I0     Y0+===
  5|         |14
-->+I1     Y1+===
  6|         |12
-->+I2     Y2+===
  7|         |11
-->+I3 xnn Y3+===
   |         |
   |  _      |
   +---------+
'''

def register():
    yield AM25S10(__file__)
