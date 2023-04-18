#!/usr/bin/env python3

''' 74x151 - 8-Input Multiplexer '''

from chip import Chip

class F151(Chip):

    ''' 74x151 - 8-Input Multiplexer '''

    symbol_name = "F151"

    checked = "VAL 0019"

    symbol = '''
     |  |  |
     |  |  |
    9v10v11v
   +-+--+--+-+
   |         |
   | S0 S1 S2|
  4|         |7
-->+A      E~o<--
  3|         |
-->+B        |
  2|         |
-->+C        |
  1|         |5
-->+D       Y+-->
 15|         |6
-->+E      Y~o-->
 14|         |
-->+F        |
 13|         |
-->+G        |
 12|         |
-->+H  xnn   |
   |         |
   |   _     |
   +---------+
'''


class F151V(Chip):

    ''' 74x151 - 8-Input Multiplexer '''

    symbol_name = "F151V"

    checked = "VAL 0019"

    symbol = '''
   +---------+
   |         |
   | S0 S1 S2|
  %|         |%
-->+A      E~o<--
  %|         |
-->+B        |
  %|         |%
-->+C      S0+<--
  %|         |%
-->+D      S1+<--
  %|         |%
-->+E      S2+<--
  %|         |
-->+F        |
  %|         |%
-->+G       Y+-->
  %|         |%
-->+H  xnn Y~o-->
   |         |
   |   _     |
   +---------+
'''

def register():
    yield F151()
    yield F151V()
