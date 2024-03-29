#!/usr/bin/env python3

''' Cypress CY7C128 - 2Kx8 Static RAM '''

from chip import Chip, Pin

class CY7C128(Chip):

    ''' Cypress CY7C128 - 2Kx8 Static RAM '''

    symbol_name = "2KX8"

    checked = "IOC 0033"

    symbol = '''
     |  |  |
     |  |  |
   18v20v21v
   +-o--o--o-+
   |         |
   | CS OE WE|
  8|         |
-->+A0       |
  7|         |
-->+A1       |9
  6|      IO0+<->
-->+A2       |10
  5|      IO1+<->
-->+A3       |11
  4|      IO2+<->
-->+A4       |13
  3|      IO3+<->
-->+A5       |14
  2|      IO4+<->
-->+A6       |15
  1|      IO5+<->
-->+A7       |16
 23|      IO6+<->
-->+A8       |17
 22|      IO7+<->
-->+A9       |
 19|         |
-->+A10  xnn |
   |         |
   |  _      |
   |         |
   +---------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(1, "10", "CS", "T", True, "I"))
        self.pins.append(Pin(4, "20", "OE", "T", True, "I"))
        self.pins.append(Pin(7, "21", "WE", "T", True, "I"))


def register():
    yield CY7C128(__file__)
