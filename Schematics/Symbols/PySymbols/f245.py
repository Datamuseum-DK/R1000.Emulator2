#!/usr/bin/env python3

''' 74x245 - Octal Bus Transceiver, Non-Inverting Outputs '''

from chip import Chip, Pin

class F245(Chip):

    ''' 74x245 - Octal Bus Transceiver, Non-Inverting Outputs '''

    def __init__(self, npins=8):
        if npins == 8:
            self.symbol_name = "F245"
            self.symbol = '''
      |  |
      |  |
     1v19v
   +--+--o--+
   |        |
   | DIR OE |
  2|        |18
<->+A0    B0+<->
  3|        |17
<->+A1    B1+<->
  4|        |16
<->+A2    B2+<->
  5|        |15
<->+A3    B3+<->
  6|        |14
<->+A4    B4+<->
  7|        |13
<->+A5    B5+<->
  8|        |12
<->+A6    B6+<->
  9|  xnn   |11
<->+A7    B7+<->
   |        |
   | _      |
   +--------+
'''

        else:
            self.symbol_name = "XBIDIR%d" % npins

            self.symbol =  '''      |  |\n'''
            self.symbol += '''      |  |\n'''
            self.symbol += '''     %v %v\n'''
            self.symbol += '''   +--+--o--+\n'''
            self.symbol += '''   |        |\n'''
            self.symbol += '''   | DIR OE |\n'''
            for i in range(npins):
                if i == npins - 1:
                    self.symbol += '''  %|  xnn   |%\n'''
                else:
                    self.symbol += '''  %|        |%\n'''
                self.symbol += '''<->+A%-2d  %3s+<->\n''' % (i, "B%d" % i)
            self.symbol += '''   |        |\n'''
            self.symbol += '''   | _      |\n'''
            self.symbol += '''   +--------+\n'''

        super().__init__()

def register():
    yield F245()
    yield F245(11)
    yield F245(16)
    yield F245(32)
    yield F245(64)
