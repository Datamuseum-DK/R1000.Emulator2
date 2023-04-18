#!/usr/bin/env python3

''' Intel 8051 - 8 Bit Control Oriented Microcomputers '''

from chip import Chip

class I8051(Chip):

    ''' Intel 8051 - 8 Bit Control Oriented Microcomputers '''

    symbol_name = "8051"

    checked = "VAL 0069"

    symbol = '''
      |      |
      |      |
    19v     9v
   +--+------+----+
   |  v           |
   | XTAL1  RST   |32
   |            A0+-->
   |              |33
   |            A1+-->
 18|              |34
-->+XTAL2       A2+-->
   |              |35
   |            A3+-->
 31|        0     |36
-->+EA~         A4+-->
   |              |37
   |            A5+-->
 29|              |38
<--+PSEN~       A6+-->
   |              |39
   |            A7+-->
 30|              |
<--+ALE           |
   |              |8
   |            B0+<->
 10|              |7
-->+RXD         B1+<->
   |              |6
   |            B2+<->
 11|              |5
<--+TXD         B3+<->
   |        1     |4
   |            B4+<->
 12|              |3
-->+INT0~       B5+<->
   |              |2
   |            B6+<->
 13|              |1
-->+INT1~       B7+<->
   |        ---   |28
   |            C0+<->
 14|              |27
<->+T0          C1+<->
   |              |26
   |            C2+<->
 15|              |25
-->+T1          C3+<->
   |        2     |24
   |            C4+<->
 16|              |23
<--+WR~         C5+<->
   |              |22
   |            C6+<->
 17|     xnn      |21
<->+RD~         C7+<->
   |     _        |
   |              |
   +--------------+
'''

def register():
    yield I8051(__file__)
