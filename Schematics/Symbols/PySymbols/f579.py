#!/usr/bin/env python3

''' 74x579 - 8-Bit Bidirectional Counter '''

from chip import Chip

class F579(Chip):

    ''' 74x579 - 8-Bit Bidirectional Counter '''

    symbol_name = "F579"

    checked = "IOC 0064"

    symbol = '''
      |  |  |
      |  |  |
     1v12v11v
   +--+--o--o--+
   |  v        |
   | CLK CS OE |
   |           |15
 20|        CO o-->
-->oMR         |
 19|           |10
-->oSR      IO0+<->
   |           |9
   |        IO1+<->
   |           |8
   |        IO2+<->
 14|           |7
-->+U/B~    IO3+<->
 13|           |5
-->oLD      IO4+<->
   |           |4
   |        IO5+<->
 18|           |3
-->oCEP     IO6+<->
 17|           |2
-->oCET xnn IO7+<->
   |           |
   |   _       |
   |           |
   +-----------+
'''


class F579X2(Chip):

    ''' 74x579 - 8-Bit Bidirectional Counter '''

    symbol_name = "F579X2"

    checked = "IOC 0064"

    symbol = '''
      |  |  |
      |  |  |
     %v %v %v
   +--+--o--o--+
   |  v        |
   | CLK CS OE |
   |           |%
  %|        CO o-->
-->oMR         |
  %|           |%
-->oSR      IO0+<->
   |           |%
   |        IO1+<->
   |           |%
   |        IO2+<->
  %|           |%
-->+U/B~    IO3+<->
  %|           |%
-->oLD      IO4+<->
   |           |%
   |        IO5+<->
  %|           |%
-->oCEP     IO6+<->
  %|           |%
-->oCET     IO7+<->
   |           |%
   |        IO8+<->
   |           |%
   |        IO9+<->
   |           |%
   |       IO10+<->
   |           |%
   |       IO11+<->
   |           |%
   |       IO12+<->
   |           |%
   |       IO13+<->
   |           |%
   |       IO14+<->
   |           |%
   |       IO15+<->
   |           |
   |   xnn     |
   |           |
   |   _       |
   +-----------+
'''

def register():
    yield F579()
    yield F579X2()
