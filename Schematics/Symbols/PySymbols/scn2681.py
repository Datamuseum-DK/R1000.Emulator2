#!/usr/bin/env python3

''' SCN2681 - Dual Asynchronous Receiver/Transmitter (DUART) '''

from chip import Chip

class SCN2681(Chip):

    ''' SCN2681 - Dual Asynchronous Receiver/Transmitter (DUART) '''

    symbol_name = "2681"

    checked = "IOC 0020"

    symbol = '''
       |   |     |
       |   |     |
     32v 33v   34v
   +---+---+-----+----+
   |                  |
   |  CLK  X2  RESET  |
 19|                  |30
<->+ D0          TXDA +-->
 22|                  |31
<->+ D1          RXDA +<--
 18|                  |7
<->+ D2          CTSA o<--
 23|                  |29
<->+ D3          RTSA o-->
 17|                  |12
<->+ D4          DTRA o-->
 24|                  |2
<->+ D5          DCDA o<--
 16|                  |4
<->+ D6          DSRA o<--
 25|                  |
<->+ D7               |11
   |             TXDB +-->
  6|                  |10
-->+ A0          RXDB +<--
  5|                  |
-->+ A1               |26
  3|           TXRDYA o-->
-->+ A2               |27
  1|           RXRDYA o-->
-->+ A3               |21
   |           BSCHGA o-->
 35|                  |15
-->o CEN       TXRDYB o-->
  9|                  |14
-->o RDN       RXRDYB o-->
  8|                  |13
-->o WDN       PITINT o-->
   |                  |
 36|                  |28
-->+ PITCLK       OP2 o-->
 39|                  |
-->+ IP4              |
 38|                  |
-->+ TXCB             |
 37|        xnn       |
-->+ RXCB             |
   |        _         |
   |                  |
   +------------------+
'''


def register():
    yield SCN2681(__file__)
