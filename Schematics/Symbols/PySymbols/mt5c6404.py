#!/usr/bin/env python3

''' MT5C6404 - 16K x 4 SRAM '''

from chip import Chip, Pin

class MT5C6404(Chip):

    ''' MT5C6404 - 16K x 4 SRAM '''

    symbol_name = "16KX4"

    checked = "IOC 0060"

    symbol = '''
     |   |
     |   |
     v10 v12
   +-o---o-+
   | CS WE |
  1|       |
-->+A0     |
  2|       |
-->+A1     |
  3|       |
-->+A2     |
  4|       |
-->+A3     |
  5|       |
-->+A4     |
  6|       |13
-->+A5  IO0+<->
  7|       |14
-->+A6  IO1+<->
  8|       |15
-->+A7  IO2+<->
  9|       |16
-->+A8  IO3+<->
 17|       |
-->+A9     |
 18|       |
-->+A10    |
 19|       |
-->+A11    |
 20|       |
-->+A12    |
 21|    xnn|
-->+A13    |
   |       |
   | _     |
   +-------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(2, "10", "CS", "T", True, "I"))
        self.pins.append(Pin(6, "12", "WE", "T", True, "I"))

def register():
    yield MT5C6404(__file__)
