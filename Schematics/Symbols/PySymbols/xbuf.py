#!/usr/bin/env python3

''' N bit '244-style buffer '''

from chip import Chip

class XBUF(Chip):

    ''' N bit '244-style register '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XBUF%d" % npins
        self.symbol = ''
        self.symbol += '      |   |\n'
        self.symbol += '      |   |\n'
        self.symbol += '     %v  %v\n'
        self.symbol += '   +--o---o--+\n'
        self.symbol += '   | INV  OE |\n'
        self.symbol += '   |         |\n'

        for i in range(1, npins + 1):
            if i == npins:
                self.symbol += '  %|   xnn   |%\n'
            else:
                self.symbol += '  %|         |%\n'
            self.symbol += '-->+%-4s %4s+===\n' % ("I%d" % (i-1), "Y%d" % (i-1))
        self.symbol += '   |  _      |\n'
        self.symbol += '   +---------+\n'
        super().__init__()

    def other_macros(self, file):
        file.write("#define %s_PINLIST" % self.symbol_name)
        for pin in self.pins:
            if "Y" in pin.name:
                file.write(" \\\n\tsc_out <sc_logic> pin%s;" % pin.number)
            else:
                file.write(" \\\n\tsc_in <sc_logic> pin%s;" % pin.number)
        file.write("\n")
        file.write("\n")
        file.write("#ifdef ANON_PINS\n")
        file.write("#define PIN_PAIRS(macro)")
        for i in range(1, self.xreg_npins + 1):
            file.write(" \\\n\tmacro(%d, PIN_I%d, PIN_Y%d)" % (self.xreg_npins - i, (i-1), (i-1)))
        file.write("\n")
        file.write("#endif\n")
           
def register():
    yield XBUF(3)
    yield XBUF(4)
    yield XBUF(6)
    yield XBUF(8)
    yield XBUF(9)
    yield XBUF(16)
    yield XBUF(20)
    yield XBUF(24)
    yield XBUF(32)
    yield XBUF(48)
    yield XBUF(56)
    yield XBUF(64)
