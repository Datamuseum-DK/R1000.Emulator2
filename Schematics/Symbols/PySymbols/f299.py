#!/usr/bin/env python3

''' 74x299 - 8-Bit Bidirectional Universal Shift Register '''

from chip import Chip

class F299(Chip):

    ''' 74x299 - 8-Bit Bidirectional Universal Shift Register '''

    symbol_name = "F299"

    checked = "IOC 0050"

    symbol = '''
      |  |
      |  |
    12v 9v
   +--+--o--+
   |  v     |
   | CLK CLR|
 11|        |
-->+RSI     |
  7|        |2
<->+DQ0   G1o<--
 13|        |3
<->+DQ1   G2o<--
  6|        |
<->+DQ2     |
 14|        |
<->+DQ3     |
  5|        |
<->+DQ4     |
 15|        |
<->+DQ5     |
  4|        |8
<->+DQ6   Q0+-->
 16|        |17
<->+DQ7   Q7+-->
 18|        |
-->+LSI     |
   |        |
   |        |
 19|        |
-->+S0      |
  1|        |
-->+S1 xnn  |
   |        |
   |  _     |
   +--------+
'''

class F299X8(Chip):

    ''' 8 x 74x299 - 8-Bit Bidirectional Universal Shift Register '''

    symbol_name = "F299X8"

    checked = "IOC 0050"

    symbol = '''
   +---------+
   |         |
  %|         |%
<->+DQ0   CLRo<--
  %|         |%
<->+DQ1   CLK+<--
  %|         |
<->+DQ2      |
  %|         |%
<->+DQ3    S0+<--
  %|         |%
<->+DQ4    S1+<--
  %|         |
<->+DQ5      |
  %|         |%
<->+DQ6    G1o<--
  %|         |%
<->+DQ7    G2o<--
  %|         |
<->+DQ8      |
  %|         |
<->+DQ9      |
  %|         |
<->+DQ10     |
  %|         |%
<->+DQ11  RI0+<--
  %|         |%
<->+DQ12  RI1+<--
  %|         |%
<->+DQ13  RI2+<--
  %|         |%
<->+DQ14  RI3+<--
  %|         |%
<->+DQ15  RI4+<--
  %|         |%
<->+DQ16  RI5+<--
  %|         |%
<->+DQ17  RI6+<--
  %|         |%
<->+DQ18  RI7+<--
  %|         |
<->+DQ19     |
  %|         |%
<->+DQ20   Q0+-->
  %|         |%
<->+DQ21   Q1+-->
  %|         |%
<->+DQ22   Q2+-->
  %|         |%
<->+DQ23   Q3+-->
  %|         |%
<->+DQ24   Q4+-->
  %|         |%
<->+DQ25   Q5+-->
  %|         |%
<->+DQ26   Q6+-->
  %|         |%
<->+DQ27   Q7+-->
  %|         |
<->+DQ28     |
  %|         |%
<->+DQ29  LI0+<--
  %|         |%
<->+DQ30  LI1+<--
  %|         |%
<->+DQ31  LI2+<--
  %|         |%
<->+DQ32  LI3+<--
  %|         |%
<->+DQ33  LI4+<--
  %|         |%
<->+DQ34  LI5+<--
  %|         |%
<->+DQ35  LI6+<--
  %|         |%
<->+DQ36  LI7+<--
  %|         |
<->+DQ37     |
  %|         |
<->+DQ38     |
  %|         |
<->+DQ39     |
  %|         |
<->+DQ40     |
  %|         |
<->+DQ41     |
  %|         |
<->+DQ42     |
  %|         |
<->+DQ43     |
  %|         |
<->+DQ44     |
  %|         |
<->+DQ45     |
  %|         |
<->+DQ46     |
  %|         |
<->+DQ47     |
  %|         |
<->+DQ48     |
  %|         |
<->+DQ49     |
  %|         |
<->+DQ50     |
  %|         |
<->+DQ51     |
  %|         |
<->+DQ52     |
  %|         |
<->+DQ53     |
  %|         |
<->+DQ54     |
  %|         |
<->+DQ55     |
  %|         |
<->+DQ56     |
  %|         |
<->+DQ57     |
  %|         |
<->+DQ58     |
  %|         |
<->+DQ59     |
  %|         |
<->+DQ60     |
  %|         |
<->+DQ61     |
  %|         |
<->+DQ62     |
  %|         |
<->+DQ63     |
   |         |
   |         |
   |   xnn   |
   |         |
   |  _      |
   +---------+
'''


def register():
    yield F299()
    yield F299X8()
