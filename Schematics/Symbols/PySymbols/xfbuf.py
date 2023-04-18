#!/usr/bin/env python3

''' N bit '244-style buffer '''

from chip import Chip

class XFBUF(Chip):

    ''' N bit '244-style register '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XFBUF%d" % npins
        self.symbol = ''
        self.symbol += '   +---------+\n'
        self.symbol += '  %|         |%\n'
        self.symbol += '-->+INV    OEo<--\n'

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
    yield XFBUF(32)
