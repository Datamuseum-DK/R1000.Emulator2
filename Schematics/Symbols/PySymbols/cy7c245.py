#!/usr/bin/env python3

''' Cypress CY7C245 - Reprogrammable 2K x 8 Registered PROM '''

from chip import Chip, Pin

class CY7C245(Chip):

    ''' Cypress CY7C245 - Reprogrammable 2K x 8 Registered PROM '''

    symbol_name = "P2K8R"

    checked = "MEM32 0032"

    symbol = '''
     |  |  |
     |  |  |
     v18v20v19
   +-+--o--o----+
   | v          |
   | CK MR OE   |
 21|            |
-->+A0          |
 22|            |17
-->+A1        Y0+===
 23|            |16
-->+A2        Y1+===
  1|            |15
-->+A3        Y2+===
  2|            |14
-->+A4        Y3+===
  3|            |13
-->+A5        Y4+===
  4|            |11
-->+A6        Y5+===
  5|            |10
-->+A7        Y6+===
  6|            | 9
-->+A8        Y7+===
  7|            |
-->+A9          |
  8|     xnn    |
-->+A10         |
   |    _       |
   +------------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(3, "18", "CK", "T", False, "I"))
        self.pins.append(Pin(6, "20", "MR", "T", True, "I"))
        self.pins.append(Pin(9, "19", "OE", "T", True, "I"))

def register():
    yield CY7C245(__file__)
