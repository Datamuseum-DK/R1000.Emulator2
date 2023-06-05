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
   |       CLK_DIS+-->
   |              |
   |              |%
   |         BP_2X+-->
   |              |%
   |        BP_2X~o-->
   |              |%
   |      BP_PHASE+-->
   |              |
   |              |%
   |           2XE+-->
   |              |%
   |          2XE~o-->
   |              |
   |              |%
   |            2X+-->
   |              |%
   |           2X~o-->
   |              |
   |              |%
   |         H1PHD+-->
   |              |%
   |         H2PHD+-->
   |              |
   |              |%
   |           H1E+-->
   |              |%
   |           H2E+-->
   |              |
   |              |%
   |            H1+-->
   |              |%
   |            H2+-->
   |              |
   |              |%
   |            Q1o-->
   |              |%
   |            Q2o-->
   |              |%
   |            Q3o-->
   |              |%
   |            Q4o-->
   |              |
   |              |%
   |           Q4Eo-->
   |  xnn         |
   |              |
   |  _           |
   +--------------+
'''


def register():
    yield XCLKGEN(__file__)
