#!/usr/bin/env python3

''' 82S123 - 32x8 PROM '''

from chip import Chip

class PBxxx(Chip):

    ''' 82S123 - 32x8 PROM '''

    symbol_name = "PBxxx"

    checked = "IOC 0070"

    symbol = '''
       |
       |
     15v
   +---o---+
   |       |9
   |  OE Y0+===
   |       |7
   |     Y1+===
   | xnn   |6
   |     Y2+===
 14|       |5
-->+A0   Y3+===
 13|       |4
-->+A1   Y4+===
 12|       |3
-->+A2   Y5+===
 11|       |2
-->+A3   Y6+===
 10|       |1
-->+A4   Y7+===
   |       |
   | _     |
   +-------+
'''

def register():
    yield PBxxx()
