#!/usr/bin/env python3

''' 74x251 - 8-Line to 1-Line Data Selector / Multiplexer '''

from chip import Chip

class F251(Chip):

    ''' 74x251 - 8-Line to 1-Line Data Selector / Multiplexer '''

    symbol_name = "F251"

    symbol = '''
     |  |  |
     |  |  |
    9v10v11v
   +-+--+--+-+
   |         |
   | S0 S1 S2|
  4|         |7
-->+A      OEo<--
  3|         |
-->+B        |
  2|         |
-->+C        |
  1|         |5
-->+D       Y+===
 15|         |6
-->+E      Y~o===
 14|         |
-->+F        |
 13|         |
-->+G        |
 12|         |
-->+H  xnn   |
   |         |
   |  _      |
   +---------+
'''

def register():
    yield F251()
