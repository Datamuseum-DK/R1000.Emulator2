#!/usr/bin/env python3

''' XCLKGEN - Global Clock Generator '''

from chip import Chip

class XCLKGEN(Chip):

    ''' XCLKGEN - Global Clock Generator '''

    symbol_name = "XCLKGEN"

    symbol = '''
   +--------------+
   |              |
   |              |%
   |         CLAMP+-->
   |              |
   |              |
   |              |%
   |            H2+-->
   |              |%
   |            Q2o-->
   |              |%
   |            Q4o-->
   |              |
   |  xnn         |
   |              |
   |  _           |
   +--------------+
'''


def register():
    yield XCLKGEN(__file__)
