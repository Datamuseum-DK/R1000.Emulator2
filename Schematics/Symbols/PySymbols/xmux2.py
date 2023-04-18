#!/usr/bin/env python3

''' N bit two input mux with individual selects '''

from chip import Chip

class XMUX2(Chip):

    ''' N bit two input mux with individual selects '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XMUX2%d" % npins
        self.symbol = ''
        self.symbol += '   +-----------+\n'
        self.symbol += '   |           |\n'

        for i in range(1, npins + 1):
            self.symbol += '  %|           |%\n'
            self.symbol += '-->+%-4s   %4s+<--\n' % ("A%d" % (i-1), "S%d" % (i-1))
        self.symbol += '   |           |\n'
        for i in range(1, npins + 1):
            if i == npins:
                self.symbol += '  %|    xnn    |%\n'
            else:
                self.symbol += '  %|           |%\n'
            self.symbol += '-->+%-4s   %4s+-->\n' % ("B%d" % (i-1), "Q%d" % (i-1))
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
        for i in range(0, self.xreg_npins):
            file.write(" \\\n\tmacro(%d, PIN_A%d, PIN_B%d, PIN_S%d, PIN_Q%d)" % (i, i, i, i, i))
        file.write("\n")
        file.write("#endif\n")
           
def register():
    yield XMUX2(32)
