#!/usr/bin/env python3

''' Fujitsu MB81C71 - CMOS 64K-Bit High-Speed SRAM '''

from chip import Chip

class MB81C71(Chip):

    ''' Fujitsu MB81C71 - CMOS 64K-Bit High-Speed SRAM '''

    symbol_name = "64KX1"

    checked = "IOC 0040"

    symbol = '''

   +------+
  1|      |14
-->+A0  A8+<--
  2|      |15
-->+A1  A9+<--
  3|      |16
-->+A2 A10+<--
  4|      |17
-->+A3 A11+<--
  5|      |18
-->+A4 A12+<--
  6|      |19
-->+A5 A13+<--
  7|      |20
-->+A6 A14+<--
  8|      |21
-->+A7 A15+<--
   |      |
 13|  xnn |9
-->+D    Q+===
 12|      |10
-->oCS  WEo<--
   |      |
   | _    |
   +------+

'''

class X64KXN(Chip):

    ''' Fujitsu MB81C71 - CMOS 64K-Bit High-Speed SRAM '''

    def __init__(self, npins):

        self.symbol_name = "64KX%d" % npins

        i = []
        i.append('   +------+')
        i.append('  %|      |%')
        i.append('-->+A0  A8+<--')
        i.append('  %|      |%')
        i.append('-->+A1  A9+<--')
        i.append('  %|      |%')
        i.append('-->+A2 A10+<--')
        i.append('  %|      |%')
        i.append('-->+A3 A11+<--')
        i.append('  %|      |%')
        i.append('-->+A4 A12+<--')
        i.append('  %|      |%')
        i.append('-->+A5 A13+<--')
        i.append('  %|      |%')
        i.append('-->+A6 A14+<--')
        i.append('  %|      |%')
        i.append('-->+A7 A15+<--')
        i.append('   |      |')
        i.append('  %|      |%')
        i.append('-->oCS  WEo<--')
        i.append('   |      |')

        for j in range(npins):
            i.append('  %|      |%')
            i.append('-->+D%d  Q%d+===' % (j, j))

        i.append('   |      |')
        i.append('   |      |')
        i.append('   |  xnn |')
        i.append('   |      |')
        i.append('   | _    |')
        i.append('   +------+')

        self.symbol = "\n".join(i)
        super().__init__()


def register():
    yield MB81C71(__file__)
    yield X64KXN(9)
