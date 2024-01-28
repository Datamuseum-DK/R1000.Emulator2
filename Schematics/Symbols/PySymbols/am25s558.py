#!/usr/bin/env python3

''' AMD Am25S558 - Eight-Bit by Eight-Bit Combinatorial Multiplier '''

from chip import Chip

class AM25S558(Chip):

    ''' AMD Am25S558 - Eight-Bit by Eight-Bit Combinatorial Multiplier '''

    symbol_name = "25S558"

    checked = "VAL 0035"

    symbol = '''
          |
          |
        21v
   +------o-------+
   |              |
   |     OE       |
   |              |
 40|              |
-->+AM            |
 20|              |
-->+BM            |
  9|              |22
-->+RS         Y0~o===
 11|              |
-->+RU            |
   |              |23
   |            Y0+===
  8|              |24
-->+A0          Y1+===
  7|              |25
-->+A1          Y2+===
  6|              |26
-->+A2          Y3+===
  5|              |27
-->+A3          Y4+===
  4|              |28
-->+A4          Y5+===
  3|              |29
-->+A5          Y6+===
  2|              |31
-->+A6          Y7+===
  1|              |32
-->+A7          Y8+===
   |              |33
   |            Y9+===
   |              |34
   |           Y10+===
 19|              |35
-->+B0         Y11+===
 18|              |36
-->+B1         Y12+===
 17|              |37
-->+B2         Y13+===
 16|              |38
-->+B3         Y14+===
 15|              |39
-->+B4         Y15+===
 14|              |
-->+B5            |
 13|              |
-->+B6            |
 12|              |
-->+B7    xnn     |
   |              |
   |              |
   |    _         |
   +--------------+
'''


def register():
    yield AM25S558(__file__)
