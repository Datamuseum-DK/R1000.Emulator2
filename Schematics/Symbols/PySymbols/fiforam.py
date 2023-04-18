#!/usr/bin/env python3

''' Dual-port 256x8 Static RAM '''

from chip import Chip, Pin

class FIFORAM(Chip):

    ''' Dual-port 256x8 Static RAM '''

    symbol_name = "FIFORAM"

    symbol = '''
      |   ^
      |   |
     %v  %|
   +--o---o--+
   | WE  EQ  |
   |         |
'''

    for i in range(16):
        symbol += '  %|         |%\n'
        symbol += '-->+I%-2d   %3s+-->\n' % (i, "Y%d" % i)
    for i in range(16):
        symbol += '   |         |\n'
    for i in range(11):
        symbol += '  %|         |%\n'
        symbol += '-->+AW%-2d %4s+<--\n' % (i, "AR%d" % i)
    symbol += '   |         |\n'
 
    symbol += '''   | xnn     |
   |         |
   |  _      |
   |         |
   +---------+
'''

def register():
    yield FIFORAM(__file__)
