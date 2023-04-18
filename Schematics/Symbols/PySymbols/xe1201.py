#!/usr/bin/env python3

''' Xecom XE1201 - Modem '''

from chip import Chip

class XE1201(Chip):

    ''' Xecom XE1201 - Modem '''

    symbol_name = "XE1201"

    checked = "RESHA 0010"

    symbol = '''
           |
           |
         39v
   +-------+-------+
   |               |
   |     RESET     |
 34|               |
<->+ D0            |
 33|               |7
<->+ D1      RXRDY +-->
 32|               |8
<->+ D2      TXRDY +-->
 31|               |9
<->+ D3     TXEMTY +-->
 30|               |6
<->+ D4     BRKDET +-->
 29|               |
<->+ D5            |
 28|               |14
<->+ D6        AIN +<--
 27|               |13
<->+ D7       AOUT +<--
   |               |12
 37|          AGND +<->
-->+ C/D~          |
   |               |
 38|               |24
-->o CS        TIP +<->
 35|               |21
-->o RD       RING +<->
 36|     xnn       |
-->o WR            |
   |     _         |
   |               |
   | +5V  GND  -5V |
   |               |
   +--+----+----+--+
    10^   2^  11^
      |    |    |
      v    v    v
'''

def register():
    yield XE1201()
