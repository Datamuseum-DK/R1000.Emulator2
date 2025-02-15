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
   |              |%
   |          2XE~o-->
   |              |
   |              |%
   |            H1+-->
   |              |%
   |            H2+-->
   |              |
   |              |%
   |            Q2o-->
   |              |%
   |            Q3o-->
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
