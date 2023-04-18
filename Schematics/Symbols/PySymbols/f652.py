#!/usr/bin/env python3

''' 74x652 - Octal Bus Tranceiver/Register, Non-Inverting Outputs '''

from chip import Chip, Pin

class F652(Chip):

    ''' 74x652 - Octal Bus Tranceiver/Register, Non-Inverting Outputs '''

    symbol_name = "F652"

    checked = "RESHA 0003"

    symbol = '''
     |    |
     |    |
   21v   3v
   +-o----o-+
   |OEA  OEB|
 23|        |1
-->+CBA  CAB+<--
 22|        |2
-->+SBA  SAB+<--
   |        |
   |^HI=REG^|
  4|        |20
<->+A0    B0+<->
  5|        |19
<->+A1    B1+<->
  6|        |18
<->+A2    B2+<->
  7|        |17
<->+A3    B3+<->
  8|        |16
<->+A4    B4+<->
  9|        |15
<->+A5    B5+<->
 10|        |14
<->+A6    B6+<->
 11|   xnn  |13
<->+A7    B7+<->
   |        |
   |  _     |
   +--------+
'''

    def parse_pins_top(self):
        ''' ... '''
        self.pins.append(Pin(2, "21", "OEA", "T", True, "I"))
        self.pins.append(Pin(6, "3", "OEB", "T", True, "I"))


class F652X(Chip):

    def __init__(self, bits):
        self.symbol_name = "F652_%d" % bits

        i = []
        
        i.append("   +----------+")
        i.append("  %|          |%")
        i.append("-->oOEA    OEBo<--")
        i.append("  %|          |%")
        i.append("-->+CBA    CAB+<--")
        i.append("  %|          |%")
        i.append("-->+SBA    SAB+<--")
        i.append("   |          |")
        i.append("   |          |")
        for j in range(bits):
            if j == bits - 1:
                 i.append("  %|   xnn    |%")
            else:
                 i.append("  %|          |%")
            i.append("<->+A%-2d    %3s+<->" % (j, "B%d" % j))
        i.append("   |          |")
        i.append("   |  _       |")
        i.append("   +----------+")

        self.symbol = "\n".join(i)

        super().__init__()


def register():
    yield F652()
    yield F652X(9)
    yield F652X(64)
