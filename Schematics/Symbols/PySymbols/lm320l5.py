#!/usr/bin/env python3

''' LM320L5 Voltage Regulator '''

from chip import Chip, Pin

class LM320L5(Chip):

    ''' LM320L5 Voltage Regulator '''

    symbol_name = "LM320L5"

    checked = "RESHA 0010"

    symbol = '''
   +-------+
   |_      |
  2|       |1
-->+IN  OUT+-->
   |       |
   |  GND  |
   +---+---+
       ^3 xnn
       |
       v 
'''

    def parse_pins_bottom(self):
        ''' ... '''
        self.pins.append(Pin(4, "3", "GND", "B", False, "B"))

def register():
    yield LM320L5()
