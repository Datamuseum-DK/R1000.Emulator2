#!/usr/bin/env python3

''' 74x381 - 4-Bit Arithmetic/Logic Unit '''

from chip import Chip, Pin

class F381(Chip):

    ''' 74x381 - 4-Bit Arithmetic/Logic Unit '''

    symbol_name = "F381"

    checked = "VAL 0036"

    symbol = '''
     | | |
     | | |
    7v6v5v
   +-+-+-+-+
   |       |
   |S0  S2 |
   |  S1   |15
   |     CI+<--
 17|       |14
-->+A0    Po-->
 19|       |13
-->+A1    Go-->
  1|       |
-->+A2     |
  3|       |12
-->+A3   F0+-->
 16|       |11
-->+D0   F1+-->
 18|       |9
-->+D1   F2+-->
  2|       |8
-->+D2   F3+-->
  4|       |
-->+D3 xnn |
   |       |
   |  _    |
   +-------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(2, "7", "SO", "T", False, "I"))
        self.pins.append(Pin(4, "6", "S1", "T", False, "I"))
        self.pins.append(Pin(6, "5", "S2", "T", False, "I"))

def register():
    yield F381()
