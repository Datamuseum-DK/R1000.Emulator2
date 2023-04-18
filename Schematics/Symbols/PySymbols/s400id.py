#!/usr/bin/env python3

''' S400ID - see comments on schematic '''

from chip import Chip

class S400ID(Chip):

    ''' S400ID - see comments on schematic '''

    symbol_name = "S400ID"

    symbol = '''
   +--------+
   |        |
  1|        |
<->+A  _    |
   |        |
   |        |
 15|        |
<->+B       |
   |   xnn  |
   | SPAR16 |
   +--------+
'''

def register():
    yield S400ID()
