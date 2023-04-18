#!/usr/bin/env python3

''' 74x139 - Dual 1-to-4 Decoder-Demultiplexer '''

from chip import Chip

class F139(Chip):

    ''' 74x139 - Dual 1-to-4 Decoder-Demultiplexer '''

    symbol_name = "F139"

    checked = "IOC 0061"

    symbol = '''
   +-------+
  1|       |4
-->oE    Y0o-->
   |       |
   |       |
   |       |5
   |     Y1o-->
   |       |
   | xnn   |
  3|       |6
-->+B0   Y2o-->
   |       |
   |       |
  2|       |7
-->+B1   Y3o-->
   |       |
   | _     |
   +-------+
'''

def register():
    yield F139()
