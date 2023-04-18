#!/usr/bin/env python3

''' N bit to one muxes '''

from chip import Chip

class XMUX_1(Chip):

    ''' N bit two input mux with common select '''

    def __init__(self, npins):
        self.xreg_npins = npins
        self.symbol_name = "XMUX%d_1" % npins
        self.symbol = ''
        self.symbol += '   +--------+\n'
        self.symbol += '   |        |\n'
        did_xnn = False

        spin = 0
        space = 0
        out = 0
        for i in range(npins):
            if i == (npins - 2):
                nbrl= '  %|    xnn |'
            else:
                nbrl= '  %|        |'
            if (1 << spin) < npins:
                self.symbol += nbrl + '%\n'
                self.symbol += '-->+%-4s  %2s+<--\n' % ("I%d" % i, "S%d" % spin)
                spin += 1
            elif space < 2:
                self.symbol += nbrl + '\n'
                self.symbol += '-->+%-4s    |\n' % ("I%d" % i)
                space += 1
            elif out < 2:
                self.symbol += nbrl + '%\n'
                if out == 0:
                    self.symbol += '-->+%-4s   Y+-->\n' % ("I%d" % i)
                else:
                    self.symbol += '-->+%-4s  Y~o-->\n' % ("I%d" % i)
                out += 1
            else:
                self.symbol += nbrl + '\n'
                self.symbol += '-->+%-4s    |\n' % ("I%d" % i)
        self.symbol += '   |        |\n'
        self.symbol += '   |  _     |\n'
        self.symbol += '   +--------+\n'
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
        file.write("#define PIN_SETS(macro)")
        for i in range(0, self.xreg_npins):
            file.write(" \\\n\tmacro(PIN_A%d, PIN_B%d, PIN_Y%d)" % (i, i, i))
        file.write("\n")
        file.write("#endif\n")
           
def register():
    yield XMUX_1(16)
    yield XMUX_1(64)
