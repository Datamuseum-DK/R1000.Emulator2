#!/usr/bin/env python3

''' 74x163 - Synchronous 4-Bit Binary Counters '''

from chip import Chip

class F163(Chip):

    ''' 74x163 - Synchronous 4-Bit Binary Counters '''

    def __init__(self, name, width):

        self.symbol_name = name

        self.checked = "IOC 0064"

        self.symbol = '''
      |  |  |
      |  |  |
     2v 9v 1v
   +--+--o--o--+
   |  v        |
   | CLK LD CLR|
   |           |15
   |         CO+-->
  6|           |11
-->+D0       Q0+-->
  5|           |12
-->+D1       Q1+-->
  4|           |13
-->+D2       Q2+-->
  3|           |14
-->+D3       Q3+-->
  7|           |
-->+ENP        |
 10|           |
-->+ENT xnn    |
   |           |
   |    _      |
   +-----------+
'''
        super().__init__()

def register():
    yield F163("F163", 4)
