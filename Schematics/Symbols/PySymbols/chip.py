#!/usr/bin/env python3

''' ASCII-art to KiCad Symbols '''

import os
import sys

# Setting PICTURE_PERFECT to Tru will hide KiCads pin numbers and names and draw
# them explicitly, matching the original scanned schematics as closely as possible.

PICTURE_PERFECT = False

class Pin():
    def __init__(self, up, side, coord, direction, invert):
        self.up = up
        self.side = side
        self.coord = coord
        self.direction = direction
        self.invert = invert == 'o'
        self.name = None
        self.number = None
        self.angle = None
        self.kicoord = None

    def __str__(self):
        return " ".join(
            (
                "<Pin",
                str(self.side),
                str(self.coord),
                str(self.direction),
                str(self.invert),
                str(self.name),
                str(self.number),
                ">"
            )
        )

    def cname(self):
        retval = self.name
        for a, b in (
            ("~", "inv"),
            ("=", "eq"),
        ):
            retval = retval.replace(a, b)
        return retval
        if not self.invert:
            return self.name
        return self.name + "_"

    def kicad_symbol(self):
        length = 2.5 * 2.54
        if self.invert:
            yield '    (circle (center %.3f %.3f)' % self.up.kicad_coords(*self.kiinv)
            yield '       (radius %.3f) (stroke (width 0)) (fill (type none))' % (2.54 / 4)
            yield '    )'
            length -= 2 * 2.54 / 4

        yield '    (pin %s line (at %.2f %.2f %d) (length %.3f)' % (
            self.direction,
            *self.up.kicad_coords(*self.kicoord),
            self.angle,
            length
        )
        pname = self.name
        if PICTURE_PERFECT:
            pname = pname.replace('~', '_')
            pname = pname.replace('>', 'CLK')
            if pname[-1] != '_' and self.invert:
                pname += "_"

        yield '      (name "%s" (effects (font (size 2.54 2.54))))' % pname
        yield '      (number "%s" (effects (font (size 2.54 2.54))))' % self.number
        yield '    )'

class PinTop(Pin):
    def __init__(self, up, coord, direction, invert, lines, numbers_left):
        super().__init__(up, "T", coord, direction, invert)
        self.angle = 270
        self.kicoord = (self.coord, self.up.top - 2)
        self.kiinv = (self.coord, self.up.top + .25)
        for y in range(up.top + 1, up.bottom):
            if lines[y][coord] not in ' v':
                break
        x0 = x1 = coord
        while x0 > up.left + 1 and lines[y][x0 - 1] != ' ':
            x0 -= 1
        while x1 < up.right - 1 and lines[y][x1 + 1] != ' ':
            x1 += 1
        self.name = "".join(lines[y][x0:x1+1])

        y = up.top - 1
        if numbers_left:
            x0 = coord - 1
            assert lines[y][x0].isdigit()
            while lines[y][x0 - 1].isdigit():
                x0 -= 1
            self.number = "".join(lines[y][x0:coord])
        else:
            x1 = coord + 1
            assert lines[y][x1].isdigit()
            while x1 + 1 < len(lines[y]) and lines[y][x1 + 1].isdigit():
                x1 += 1
            self.number = "".join(lines[y][coord + 1: x1 + 1])

class PinBottom(Pin):
    def __init__(self, up, coord, direction, invert, lines, numbers_left):
        super().__init__(up, "B", coord, direction, invert)
        self.angle = 90
        self.kicoord = (self.coord, self.up.bottom + 2)
        self.kiinv = (self.coord, self.up.bottom - .25)
        for y in range(up.bottom - 1, up.top, -1):
            if lines[y][coord] not in ' v':
                break
        x0 = x1 = coord
        while x0 > up.left + 1 and lines[y][x0 - 1] != ' ':
            x0 -= 1
        while x1 < up.right - 1 and lines[y][x1 + 1] != ' ':
            x1 += 1
        self.name = "".join(lines[y][x0:x1+1])

        y = up.bottom + 1
        if numbers_left:
            x0 = coord - 1
            assert lines[y][x0].isdigit()
            while lines[y][x0 - 1].isdigit():
                x0 -= 1
            self.number = "".join(lines[y][x0:coord])
        else:
            x1 = coord + 1
            assert lines[y][x1].isdigit()
            while x1 + 1 < len(lines[y]) and lines[y][x1 + 1].isdigit():
                x1 += 1
            self.number = "".join(lines[y][coord + 1: x1 + 1])

class PinLeft(Pin):
    def __init__(self, up, coord, direction, invert, lines):
        super().__init__(up, "L", coord, direction, invert)
        self.angle = 0
        self.kicoord = (self.up.left - 2, self.coord)
        self.kiinv = (self.up.left + .25, self.coord)
        for x0 in range(up.left + 1, up.right):
            if lines[coord][x0] != ' ':
                break
        for x1 in range(x0 + 1, up.right):
            if lines[coord][x1] == ' ':
                break
        self.name = "".join(lines[coord][x0:x1]).replace("xnn","")

        s = list(lines[coord - 1][:up.left])
        while s[0] == ' ':
            s.pop(0)
        while s[-1] == ' ':
            s.pop(-1)
        self.number = "".join(s)

class PinRight(Pin):
    def __init__(self, up, coord, direction, invert, lines):
        super().__init__(up, "R", coord, direction, invert)
        self.angle = 180
        self.kicoord = (self.up.right + 2, self.coord)
        self.kiinv = (self.up.right - .25, self.coord)
        for x1 in range(up.right - 1, up.left, -1):
            if lines[coord][x1] != ' ':
                break
        for x0 in range(x1 - 1, up.left, -1):
            if lines[coord][x0] == ' ':
                break
        self.name = "".join(lines[coord][x0+1:x1+1]).replace("xnn","")

        s = list(lines[coord - 1][up.right + 1:])
        while s[0] == ' ':
            s.pop(0)
        while s[-1] == ' ':
            s.pop(-1)
        self.number = "".join(s)

class Chip():

    checked = None

    def __init__(self, pyfn=None):
        self.pyfn = pyfn
        self.pins = []
        self.alpha = []
        self.xnn = None
        self.value = None

        self.lex_symbol()
        i = [x.name for x in self.pins]
        if len(set(i)) != len(self.pins):
            print("DUPLICATE PIN NAMES", self.symbol_name, list(sorted(i)))

    def __str__(self):
        return "<Chip " + self.symbol_name + ">"

    def main(self):
        assert len(sys.argv) == 2
        assert sys.argv[1] == "rebuild"

        cname = self.__class__.__name__
        if not self.pyfn:
            self.pyfn = self.symbol_name.lower()
        sfn = os.path.basename(self.pyfn).replace(".py", "")
        with open("Chipdesc/chipdict.py", "a") as file:
            file.write("from Chipdesc.%s import %s\n" % (sfn, cname))
        with open("Chipdesc/chipdict.py.suf", "a") as file:
            #file.write("    '%s': %s,\n" % (self.signature(), cname))
            file.write("CHIPSIGS.setdefault('%s', list()).append(%s)\n" % (self.signature(), cname))
            file.write("CHIPS['%s'] = %s\n" % (self.symbol_name, cname))

        fo = open("KiCadFiles/%s_.txt" % self.symbol_name, "w")
        for i in self.kicad_symbol():
            fo.write(i + "\n")

        if False and not self.checked:
            print(self.pyfn, self.symbol_name, "NOT CHECKED")

    def other_macros(self, file):
        return

    def lex_symbol(self):
        verbose = False

        if verbose:
            print()
            print(self.symbol_name, pyfn)
            print()

        if "xnn" not in self.symbol:
            raise Exception("No 'xnn' in symbol", self)

        lines = self.symbol.splitlines(False)

        # Eliminate leading and trailing blank lines
        while len(lines[0]) == 0:
            lines.pop(0)
        while len(lines[-1]) == 0:
            lines.pop(-1)

        apin = 1
        for lineno, line in enumerate(lines):
             for a, b, c, d in (
                 ("%|", " %|", "  %|", "%d|"),
                 ("%v", " %v", "  %v", "%dv"),
                 ("|%", "|%", "|%", "|%d"),
             ):
                 if apin < 10:
                     while a in line:
                         line = line.replace(a, d % apin, 1)
                         apin += 1
                 if apin < 100:
                     while a in line:
                         line = line.replace(b, d % apin, 1)
                         apin += 1
                 else:
                     while b in line:
                         line = line.replace(c, d % apin, 1)
                         apin += 1
             lines[lineno] = line

        # Split to list of chars
        i = []
        for j in lines:
            i.append(list(x for x in j))
        lines = i

        if verbose:
            for n, i in enumerate(lines):
                print("%2d" % n, "".join(i))

        # Find the main rectangle
        for n, i in enumerate(lines):
            if '+' not in i:
                continue
            self.left = i.index('+')
            self.top = n
            self.right = max(n for n,x in enumerate(i) if x == '+')
            break

        for n, i in reversed(list(enumerate(lines))):
            if '+' not in i:
                continue
            j = i.index('+')
            if j != self.left:
                raise Exception("Top and bottom left '+' not aligned")
            j = max(n for n,x in enumerate(i) if x == '+')
            if j != self.right:
                raise Exception("Top and bottom right '+' not aligned")
            self.bottom = n
            break

        if verbose:
            print("TOP", self.top)
            print("LEFT", self.left)
            print("RIGHT", self.right)
            print("BOT", self.bottom)

        lines[self.top][self.left] = ' '
        lines[self.top][self.right] = ' '
        lines[self.bottom][self.left] = ' '
        lines[self.bottom][self.right] = ' '

        # Find out if pins on the top are numbered to the left or right
        if self.top > 0:
            for i in lines[self.top - 1]:
                if i == ' ':
                    continue
                top_numbers_left = i.isdigit()
                break

        # Find out if pins on the bottom are numbered to the left or right
        if self.bottom < len(lines) - 1:
            for i in lines[self.bottom + 1]:
                if i == ' ':
                    continue
                bottom_numbers_left = i.isdigit()
                break

        # Find top & bottom pins:
        for x in range(self.left + 1, self.right):
            i = lines[self.top][x]
            lines[self.top][x] = ' '
            if i != '-':
                s = lines[self.top-3][x] + lines[self.top-2][x] + lines[self.top-1][x]
                dir = {
                    "||v": "input",
                    "^|v": "bidirectional",
                    "^||": "output",
                    "===": "tri_state",
                    "ooo": "open_collector",
                }[s]
                lines[self.top-3][x] = lines[self.top-2][x] = lines[self.top-1][x] = ' '
                self.pins.append(PinTop(self, x, dir, i, lines, top_numbers_left))
                if verbose:
                    print(self.pins[-1])

            i = lines[self.bottom][x]
            lines[self.bottom][x] = ' '
            if i != '-':
                s = lines[self.bottom+1][x] + lines[self.bottom+2][x] + lines[self.bottom+3][x]
                dir = {
                    "^||": "input",
                    "^|v": "bidirectional",
                    "||v": "output",
                    "===": "tri_state",
                    "ooo": "open_collector",
                }[s]
                lines[self.bottom+1][x] = lines[self.bottom+2][x] = lines[self.bottom+3][x] = ' '
                self.pins.append(PinBottom(self, x, dir, i, lines, bottom_numbers_left))
                if verbose:
                    print(self.pins[-1])

        # Find left & right pins:
        for y in range(self.top + 1, self.bottom):
            i = lines[y][self.left]
            lines[y][self.left] = ' '
            if i != '|':
                s = "".join(lines[y][self.left-3:self.left])
                dir = {
                    "-->": "input",
                    "<->": "bidirectional",
                    "<--": "output",
                    "===": "tri_state",
                    "ooo": "open_collector",
                }[s]
                lines[y][self.left-3] = lines[y][self.left-2] = lines[y][self.left-1] = ' '
                self.pins.append(PinLeft(self, y, dir, i, lines))
                if verbose:
                    print(self.pins[-1])

            i = lines[y][self.right]
            lines[y][self.right] = ' '
            if i != '|':
                s = "".join(lines[y][self.right + 1:self.right+4])
                dir = {
                    "<--": "input",
                    "<->": "bidirectional",
                    "-->": "output",
                    "===": "tri_state",
                    "ooo": "open_collector",
                }[s]
                lines[y][self.right+1] = lines[y][self.right+2] = lines[y][self.right+3] = ' '
                self.pins.append(PinRight(self, y, dir, i, lines))
                if verbose:
                    print(self.pins[-1])

        # Locate 'xnn' field
        for y, i in enumerate(lines):
            for x, j in enumerate(i):
                if j == 'x' and i[x + 1] == 'n' and i[x + 2] == 'n':
                    self.origo_x = x
                    self.origo_y = y
                    self.xnn = (x, y)
                    i[x] = ' '
                    i[x + 1] = ' '
                    i[x + 2] = ' '
                    break

        # Locate '_' field
        for y, i in enumerate(lines):
            for x, j in enumerate(i):
                if j == '_':
                    self.value = (x, y)
                    i[x] = ' '
                    break

        # Collect the glyphs
        for y, i in enumerate(lines):
            for x, j in enumerate(i):
                if j != ' ':
                    self.alpha.append([j, x, y])

        if verbose:
            for n, i in enumerate(lines):
                print("%2d" % n, "".join(i))

    def kicad_coords(self, x, y):
        return (
            (x - self.origo_x) * 2.54,
            (y - self.origo_y) * -2.54,
        )

    def kicad_symbol(self):
        yield '  (symbol "%s"' % self.symbol_name
        if PICTURE_PERFECT:
            yield '    (pin_numbers hide) (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)'
        else:
            yield '     (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
        yield '    (property "Reference" "U" (id 0) (at %.2f %.2f 0)' % (
            *self.kicad_coords(self.xnn[0] + 1, self.xnn[1] - 2),
        )
        yield '      (effects (font (size 1.27 1.27)))'
        yield '    )'
        yield '    (property "Value" "%s" (id 1) (at %.2f %.2f 0)' % (
            self.symbol_name,
            *self.kicad_coords(self.value[0] - .5, self.value[1]),
        )
        yield '      (effects (font (size 2.54 2.54)) (justify left))'
        yield '    )'
        yield '    (property "Footprint" "" (id 2) (at 1.27 -1.27 0)'
        yield '      (effects (font (size 1.27 1.27)) hide)'
        yield '    )'
        yield '    (property "Datasheet" "" (id 3) (at 1.27 -1.27 0)'
        yield '      (effects (font (size 1.27 1.27)) hide)'
        yield '    )'
        yield '    (property "Location" "___" (id 4) (at %.2f %.2f 0)' % (
            *self.kicad_coords(self.xnn[0] - .5, self.xnn[1]),
        )
        yield '      (effects (font (size 2.54 2.54)) (justify left))'
        yield '    )'
        yield '    (property "Name" "______" (id 5) (at %.2f %.2f 0)' % (
            *self.kicad_coords((self.left + self.right)//2 + .5, self.bottom + 2),
        )
        yield '      (effects (font (size 2.54 2.54)) (justify bottom))'
        yield '    )'

        yield '    (symbol \"%s_1_1\"' % self.symbol_name

        if PICTURE_PERFECT:
            for a, x, y in sorted(self.alpha):
                yield '      (text "%s" (at %.2f %.2f 0)' % (a, *self.kicad_coords(x, y))
                yield '        (effects (font (size 2.54 2.54)))'
                yield '      )'

        yield '      (rectangle (start %.2f %.2f) (end %.2f %.2f)' % (
            *self.kicad_coords(self.left + .5, self.top + .5),
            *self.kicad_coords(self.right - .5, self.bottom - .5),
        )
        yield '        (stroke (width 0)) (fill (type none))'
        yield '      )'
        for i in self.pins:
            yield from i.kicad_symbol()
        yield '    )'
        yield '  )'

    def signature(self):
        pins = {
            "L": {},
            "R": {},
            "T": {},
            "B": {},
        }
        hhi = 0
        hlo = 99
        vhi = 0
        vlo = 99
        for i in self.pins:
            if i.side in "TB":
                hhi = max(hhi, i.coord)
                hlo = min(hlo, i.coord)
            else:
                vhi = max(vhi, i.coord)
                vlo = min(vlo, i.coord)
            pins[i.side][i.coord] = i

        def pin_side(side, fm, to):
            sig = side
            for i in range(fm, to):
                j = pins[side].get(i)
                if not j:
                    sig += "_"
                elif j.invert:
                    sig += "o"
                else:
                    sig += "I"
            return sig

        sig = pin_side("L", vlo, vhi + 1)
        sig += pin_side("R", vlo, vhi + 1)
        sig += pin_side("T", hlo, hhi + 1)
        sig += pin_side("B", hlo, hhi + 1)
        return sig

class ChipSig():

    def __init__(self, arrow, name, low = None, high = None, bus=False):
        self.arrow = arrow
        self.name = name
        self.low = low
        self.high = high
        self.bus = bus

    def __iter__(self):
        if self.low is None and self.high is None:
            yield self.name, self.arrow
        elif self.bus:
            yield self.name + "%d" % self.low, self.arrow
            yield self.name + "%d" % self.high, self.arrow
        else:
            for pin in range(self.low, self.high + 1):
                yield self.name + "%d" % pin, self.arrow

    def spacing(self, really):
        if really:
            yield ""
            yield ""
            if 0 and self.high:
                yield ""
                yield ""

class FChip(Chip):

    def __init__(self):
        self.sig_l = []
        self.sig_r = []

    def sig_left(self, signal):
        self.sig_l.append(signal)

    def sig_right(self, signal):
        self.sig_r.append(signal)

    def finish(self, width = 0):
        self.symbol = ''

        left = []
        space = False
        for sig in self.sig_l:
            for _i in sig.spacing(space):
                left.append('   |')
            for nm, arrow in sig:
                left.append('  %|')
                if sig.bus:
                    left.append(arrow + '=' + nm)
                else:
                    left.append(arrow + nm)
 
            space = True

        right = []
        space = False
        for sig in self.sig_r:
            for _i in sig.spacing(space):
                right.append('   |   ')
            for nm, arrow in sig:
                right.append('|%  ')
                if sig.bus:
                    right.append(nm + '=' + arrow)
                else:
                    right.append(nm + arrow)
            space = True

        minwidth = max(len(x) for x in left) + max(len(x) for x in right) + 2
        if width == 0:
            print(self.symbol_name, "W", width, "MW", minwidth)
            width = minwidth
        else:
            print(self.symbol_name, "W", width, "MW", minwidth)
            assert width >= minwidth

        top_bot = '   +' + '-' * (width - 8) + '+\n'
        spacer = '   |' + ' ' * (width - 8) + '|\n'

        self.symbol += top_bot
        self.symbol += spacer
        self.symbol += spacer.replace('|    ', '| xnn')
        self.symbol += spacer

        while len(left) < len(right):
            left.append('   |')
        while len(right) < len(left):
            right.append('|   ')
        for l, r in zip(left, right):
            pad = " " * (width - (len(l) + len(r)))
            self.symbol += l + pad + r.rstrip() + "\n"

        self.symbol += spacer
        self.symbol += spacer
        self.symbol += spacer.replace('|  ', '| _')
        self.symbol += top_bot

        super().__init__()

