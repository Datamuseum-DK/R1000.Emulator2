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

class MT5C6404X2(Chip):

    ''' 2x MT5C6404 - 16K x 4 SRAM '''

    symbol_name = "16KX8"

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
  4|       |22
-->+A3  IO0+<->
  5|       |23
-->+A4  IO1+<->
  6|       |13
-->+A5  IO2+<->
  7|       |14
-->+A6  IO3+<->
  8|       |15
-->+A7  IO4+<->
  9|       |16
-->+A8  IO5+<->
 17|       |24
-->+A9  IO6+<->
 18|       |25
-->+A10 IO7+<->
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

class MT5C6404X4(Chip):

    ''' 5x MT5C6404 - 16K x 4 SRAM '''

    symbol_name = "16KX16"

    symbol = '''
      |    |
      |    |
     %v   %v
   +--o----o--+
   |  CS   WE |
  %|          |%
-->+A0     IO0+<->
  %|          |%
-->+A1     IO1+<->
  %|          |%
-->+A2     IO2+<->
  %|          |%
-->+A3     IO3+<->
  %|          |%
-->+A4     IO4+<->
  %|          |%
-->+A5     IO5+<->
  %|          |%
-->+A6     IO6+<->
  %|          |%
-->+A7     IO7+<->
  %|          |%
-->+A8     IO8+<->
  %|          |%
-->+A9     IO9+<->
  %|          |%
-->+A10   IO10+<->
  %|          |%
-->+A11   IO11+<->
  %|          |%
-->+A12   IO12+<->
  %|          |%
-->+A13   IO13+<->
   |          |%
   |      IO14+<->
   |          |%
   |      IO15+<->
   |          |
   | xnn      |
   |          |
   | _        |
   +----------+
'''

def register():
    yield MT5C6404(__file__)
    yield MT5C6404X2(__file__)
    yield MT5C6404X4(__file__)
