#!/usr/bin/env python3

''' 74x181 - Arithmetic Logic Unit '''

from chip import Chip, Pin

class F181(Chip):

    ''' 74x181 - Arithmetic Logic Unit '''

    symbol_name = "F181"

    checked = "VAL 0040"

    symbol = '''
      | | | | |
      | | | | |
     8v3v4v5v6v
   +--+-+-+-+-+---+
   |              |
   |  M   S1  S3  |
   |    S0  S2    |16
   |            COo-->
 19|              |7
-->+A0          CIo<--
 21|              |15
-->+A1           P+-->
 23|              |17
-->+A2           G+-->
  2|              |14
-->+A3         A=B+ooo
 18|              |13
-->+B0          Y0+-->
 20|              |11
-->+B1          Y1+-->
 22|              |10
-->+B2          Y2+-->
  1|     xnn      |9
-->+B3          Y3+-->
   |              |
   |    _         |
   +--------------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(3, "8", "M", "T", False, "I"))
        self.pins.append(Pin(5, "3", "S0", "T", False, "I"))
        self.pins.append(Pin(7, "4", "S1", "T", False, "I"))
        self.pins.append(Pin(9, "5", "S2", "T", False, "I"))
        self.pins.append(Pin(11, "6", "S3", "T", False, "I"))

def register():
    yield F181()
