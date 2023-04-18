#!/usr/bin/env python3

''' Generic 2764 - 8K x 8 EPROM Memory '''

# Four pieces on RESHA 0003 named 'EEPROM[0-3] (not "EPROM")
# Real-world RESHA has only a single EEPROM chip.
# IOC 0021 has same footprint named "28256"

from chip import Chip

class EPROM(Chip):

    ''' Generic 2764 - 8K x 8 EPROM Memory '''

    symbol_name = "2764"

    checked = "RESHA 0003"

    symbol = '''
     |   |
     |   |
   20v 22v
   +-o---o-+
   |       |
  2| CE  OE|
-->+A0     |
 23|       |1
-->+A1  VPP+<--
 21|       |26
-->+A2   NC+<--
 24|       |27
-->+A3  PGMo<--
 25|       |
-->+A4 xnn |
  3|       |19
-->+A5   Y0+<->
  4|       |18
-->+A6   Y1+<->
  5|       |17
-->+A7   Y2+<->
  6|       |16
-->+A8   Y3+<->
  7|       |15
-->+A9   Y4+<->
  8|       |13
-->+A10  Y5+<->
  9|       |12
-->+A11  Y6+<->
 10|       |11
-->+A12  Y7+<->
   |       |
   | _     |
   +-------+
'''

class EEPROM(EPROM):

    ''' 28256 - paged 32K x 8 EEPROM Memory '''

    symbol_name = "28256"

    checked = "IOC 0021"

def register():
    yield EPROM(__file__)
    yield EEPROM(__file__)
