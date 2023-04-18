#!/usr/bin/env python3

''' 74x189 - 64-Bit Random Access Memory (With 3-State Outputs) '''

from chip import Chip

class F189(Chip):

    ''' 74x189 - 64-Bit Random Access Memory (With 3-State Outputs) '''

    symbol_name = "F189"

    checked = "SEQ 0066"

    symbol = '''
      |  |
      |  |
     3v 2v
   +--o--o--+
   |  v     |
   |  WE CS |
  1|        |
-->+A0      |
 15|        |
-->+A1      |
 14|        |
-->+A2      |
 13|        |5
-->+A3    Q0o===
   |        |7
   |      Q1o===
  4|        |9
-->+D0    Q2o===
  6|        |11
-->+D1    Q3o===
 18|        |
-->+D2      |
 12|        |
-->+D3 xnn  |
   |        |
   |  _     |
   +--------+
'''

def register():
    yield F189()
