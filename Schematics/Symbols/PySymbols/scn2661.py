#!/usr/bin/env python3

''' SCN2661 Enhanced Programmable Communications Interface EPCI/USART '''

from chip import Chip

class SCN2661(Chip):

    ''' SCN2661 Enhanced Programmable Communications Interface EPCI/USART '''

    symbol_name = "2661B"

    checked = "IOC 0019"

    symbol = '''
          |
          |
        21v
   +------+-------+
   |              |
  8|    RESET     |
<->+D0            |
  7|              |
<->+D1            |
  6|              |19
<->+D2         TXD+-->
  5|              |
<->+D3            |
  2|              |23
<->+D4         RTSo-->
  1|              |
<->+D5            |
 28|              |24
<->+D6         DTRo-->
 27|              |
<->+D7            |
   |              |
   |              |
 10|              |
-->+A0            |
 12|              |
-->+A1            |
 11|              |
-->oCE            |
 13|              |
-->+R~/W          |
   |              |3
   |           RXD+<--
 20|              |
-->+BRCLK         |
 18|              |17
<--oTXEMT      CTSo<--
 15|              |
<--oTXRDY         |
 14|              |22
<--oRXRDY      DSRo<--
 25|              |
<--+BRKDET        |
  9|              |16
-->+XSYNC xnn  DCDo<--
   |              |
   |     _        |
   |              |
   +--------------+
'''

def register():
    yield SCN2661(__file__)
