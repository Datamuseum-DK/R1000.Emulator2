#!/usr/bin/env python3

''' 32 bit '374-style register '''

from chip import Chip

class XREG(Chip):

    ''' 32 bit '374-style register '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XREG%d" % npins
        self.symbol = ''
        self.symbol += '      |  |  |\n'
        self.symbol += '      |  |  |\n'
        self.symbol += '     %v %v %v\n'
        self.symbol += '   +--+--o--o--+\n'
        self.symbol += '  %|CLK INV OE |%\n'
        self.symbol += '   |           |\n'

        for i in range(1, npins + 1):
            if i == npins:
                self.symbol += '  %|    xnn    |%\n'
            else:
                self.symbol += '  %|           |%\n'
            self.symbol += '-->+%-4s   %4s+===\n' % ("D%d" % (i-1), "Q%d" % (i-1))
        self.symbol += '   |    _      |\n'
        self.symbol += '   +-----------+\n'
        super().__init__()

    def other_macros(self, file):
        file.write("#define %s_PINLIST" % self.symbol_name)
        for pin in self.pins:
            if "Q" in pin.name:
                file.write(" \\\n\tsc_out <sc_logic> pin%s;" % pin.number)
            else:
                file.write(" \\\n\tsc_in <sc_logic> pin%s;" % pin.number)
        file.write("\n")
        file.write("\n")
        file.write("#ifdef ANON_PINS\n")
        file.write("#define PIN_PAIRS(macro)")
        for i in range(1, self.xreg_npins + 1):
            file.write(" \\\n\tmacro(%d, PIN_D%d, PIN_Q%d)" % (self.xreg_npins - i, (i-1), (i-1)))
        file.write("\n")
        file.write("#endif\n")
           
def register():
    yield XREG(4)
    yield XREG(9)
    yield XREG(16)
    yield XREG(32)
    yield XREG(64)
