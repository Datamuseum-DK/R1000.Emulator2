#!/usr/bin/env python3

''' 74x138 - 1-to-8 Decoder-Demultiplexer '''

# XXX: Incomplete

from chip import Chip

class F138(Chip):

    ''' 74x138 - Dual 1-to-4 Decoder-Demultiplexer '''

    symbol_name = "F138"

    checked = "IOC 0021"

    symbol = '''
   +--------+
   |        |15
   |     Y0 o===
   |        |15
   |     Y1 o===
   |_       |13
   |     Y2 o===
   |        |12
   |     Y3 o===
   |xnn     |11
   |     Y4 o===
  3|        |10
-->+S0   Y5 o===
  2|        |9
-->+S1   Y6 o===
  1|        |7
-->+S2   Y7 o===
   |        |
   +--------+
'''

def register():
    yield F138()
