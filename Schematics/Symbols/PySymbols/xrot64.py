#!/usr/bin/env python3

''' N x 25S10 rotator '''

from chip import Chip

class XROT16(Chip):

    ''' N x 25S10 rotator '''

    def __init__(self, npins):
        self.xrot_npins = npins
        self.symbol_name = "XROT%d" % npins
        self.symbol = ''
        self.symbol += '   +-----------+\n'
        self.symbol += '   |           |\n'
        self.symbol += '  %|           |%\n'
        self.symbol += '-->+S0      AB0+<--\n'
        self.symbol += '  %|           |%\n'
        self.symbol += '-->+S1      AB1+<--\n'
        self.symbol += '   |           |%\n'
        self.symbol += '   |        AB2+<--\n'
        self.symbol += '   |           |%\n'
        self.symbol += '   |        AB3+<--\n'
        self.symbol += '   |           |\n'
        self.symbol += '   |           |\n'
        for i in range(npins + 3):
            self.symbol += '  %|           |\n'
            self.symbol += '-->+%3s        |\n' % ("A%d" % i)
        self.symbol += '   |           |\n'
        self.symbol += '   |           |\n'
        for i in range(npins + 3):
            if i < npins:
                self.symbol += '  %|           |%\n'
            elif i == npins:
                self.symbol += '  %|    xnn    |\n'
            else:
                self.symbol += '  %|           |\n'
            if i < npins:
                self.symbol += '-->+%3s     %-3s+-->\n' % ("B%d" % i, "Y%d" % i)
            else:
                self.symbol += '-->+%3s        |\n' % ("B%d" % i)
        self.symbol += '   |           |\n'
        self.symbol += '   |    _      |\n'
        self.symbol += '   +-----------+\n'
        super().__init__()

    def other_macros(self, file):
        file.write("#define %s_PINLIST" % self.symbol_name)
        for pin in self.pins:
            if "=" in pin.name:
                file.write(" \\\n\tsc_out <sc_logic> pin%s;" % pin.number)
            else:
                file.write(" \\\n\tsc_in <sc_logic> pin%s;" % pin.number)
        file.write("\n")
        file.write("\n")
        file.write("#ifdef ANON_PINS\n")
        file.write("#define XROT_IPINS(macro)")
        for i in range(-3, self.xrot_npins):
            if i < 0:
                j = "PIN_I_%d" % (-i)
            else:
                j = "PIN_I%d" % i
            file.write(" \\\n\tmacro(%d, %s)" % (self.xrot_npins - (1 + i), j))
        file.write("\n")
        file.write("\n")
        file.write("#define XROT_OGROUPS(macro)")
        for i in range(0, self.xrot_npins, 4):
            file.write(" \\\n\tmacro(%d, PIN_OE%d, PIN_Y%d, PIN_Y%d, PIN_Y%d, PIN_Y%d)" % (
                self.xrot_npins - (i + 1), 
                i // 4, 
                i, 
                i + 1, 
                i + 2, 
                i + 3, 
            ))
        file.write("\n")
        file.write("\n")
        file.write("#endif\n")
           

class XROT64(Chip):

    ''' N x 25S10 rotator '''

    def __init__(self, npins):
        self.xrot_npins = npins
        self.symbol_name = "XROT%d" % npins
        self.symbol = ''
        self.symbol += '   +-----------+\n'
        self.symbol += '   |           |%\n'
        self.symbol += '   |         OEo<--\n'
        self.symbol += '  %|           |%\n'
        self.symbol += '-->+S0       S2+<--\n'
        self.symbol += '  %|           |%\n'
        self.symbol += '-->+S1       S3+<--\n'
        self.symbol += '   |           |\n'
        self.symbol += '   |           |\n'
        for i in range(npins):
            if i == npins - 3:
                self.symbol += '  %|    xnn    |%\n'
            else:
                self.symbol += '  %|           |%\n'
            self.symbol += '-->+%3s     %-3s+===\n' % ("I%d" % i, "Y%d" % i)
        self.symbol += '   |           |\n'
        self.symbol += '   |    _      |\n'
        self.symbol += '   +-----------+\n'
        super().__init__()

    def other_macros(self, file):
        file.write("#define %s_PINLIST" % self.symbol_name)
        for pin in self.pins:
            if "=" in pin.name:
                file.write(" \\\n\tsc_out <sc_logic> pin%s;" % pin.number)
            else:
                file.write(" \\\n\tsc_in <sc_logic> pin%s;" % pin.number)
        file.write("\n")
        file.write("\n")
        file.write("#ifdef ANON_PINS\n")
        file.write("#define XROT_IPINS(macro)")
        for i in range(-3, self.xrot_npins):
            if i < 0:
                j = "PIN_I_%d" % (-i)
            else:
                j = "PIN_I%d" % i
            file.write(" \\\n\tmacro(%d, %s)" % (self.xrot_npins - (1 + i), j))
        file.write("\n")
        file.write("\n")
        file.write("#define XROT_OGROUPS(macro)")
        for i in range(0, self.xrot_npins, 4):
            file.write(" \\\n\tmacro(%d, PIN_OE%d, PIN_Y%d, PIN_Y%d, PIN_Y%d, PIN_Y%d)" % (
                self.xrot_npins - (i + 1), 
                i // 4, 
                i, 
                i + 1, 
                i + 2, 
                i + 3, 
            ))
        file.write("\n")
        file.write("\n")
        file.write("#endif\n")
           
def register():
    yield XROT16(16)
    yield XROT64(64)
