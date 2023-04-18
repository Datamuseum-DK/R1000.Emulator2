#!/usr/bin/env python3

''' MM58167 - Microprocessor Real Time Clock '''

from chip import Chip

class MM58167(Chip):

    ''' MM58167 - Microprocessor Real Time Clock '''

    symbol_name = "58167"

    checked = "IOC 0018"

    symbol = '''
          |
          |
        24v
   +------+-------+
   |              |
   |     VDD      |
   |              |
 22|              |
<->+D0            |
 21|              |
<->+D1            |
 20|              |
<->+D2            |
 19|              |4
<->+D3         RDYo<--
 18|              |
<->+D4            |
 17|              |23
<->+D5      PWR DNo<--
 16|              |
<->+D6            |
 15|              |14
<->+D7       STBBYo<--
  9|              |
-->+A0            |
  8|              |13
-->+A1         INT+-->
  7|              |
-->+A2            |
  6|              |
-->+A3            |
  5|              |
-->+A4            |
  1|              |10
-->oCS     OSC IN +<--
  2|              |
-->oRD   xnn      |
  3|              |11
-->oWR     OSC OUT+-->
   |              |
   |    _         |
   +--------------+
'''

def register():
    yield MM58167(__file__)
