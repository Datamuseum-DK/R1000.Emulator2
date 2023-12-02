
import struct
import sys
import context

def parbyte(x):
    x = (x >> 4) ^ x
    x = (x >> 2) ^ x
    x = (x >> 1) ^ x
    return x & 1

class Line():
    def __init__(self, side, line, ram1, ram2):
        self.side = side
        self.line = line
        self.ram1 = ram1
        self.ram2 = ram2
        # ....|.......|.......
        # .....######--.......
        # .....012345.........
        # .....------7........
        self.tag = ram1 & ~(0xfe << 7)
        self.tag |= (ram2 & 0xfe) << 7
        self.parbit = (ram1 >> 7) & 0xfc
        self.parbit |= (ram2 & 1) << 1
        self.parbit |= (ram1 >> 8) & 1

        ba = bin((1<<64)|ram1)[3:] + " " + bin((1<<8)|ram2)[3:]
        bb = bin((1<<64)|self.tag)[3:] + " " + bin((1<<8)|self.parbit)[3:]
        ca = len(ba.replace('0', ''))
        cb = len(bb.replace('0', ''))
        if ca != cb:
            print("M", "%016x" % ram1, "%02x" % ram2, "%016x" % self.tag, "%02x" % self.parbit, ca, cb)
            print("  ", ba)
            print("  ", bb)
        for i, j in (
            (56, 0),
            (48, 1),
            (40, 2),
            (32, 3),
            (24, 4),
            (16, 5),
            (8, 6),
            (0, 7),
        ):
            if j == 16 or parbyte(self.tag >> i) != ((self.parbit >> (7-j)) & 1):
                print(
                   self.up.ctx.ident,
                   "PAR",
                   j,
                   "%04x" % self.line,
                   "%016x" % ram1,
                   "%02x" % ram2,
                   "%016x" % self.tag,
                   "%02x" % self.parbit,
                   parbyte(self.tag >> i),
                   (self.parbit >> (7-j)) & 1,
                )
                #print("  ", ba)
                #print("  ", bb)

        self.seg = self.tag >> 40
        self.vpid = (self.tag >> 32) & 0xff
        self.pg = (self.tag >> 13) & ((1<<19)-1)
        self.d = (self.tag >> 12) & 0x1
        self.lru = (self.tag >> 8) & 0xf
        self.stat = (self.tag >> 6) & 0x3
        self.res = (self.tag >> 3) & 0x7
        self.spc = (self.tag >> 0) & 0x7

    def __repr__(self):
        b = bin((1<<64)|self.tag)[3:]
        return ':'.join(
            [
                self.side, 
                "%04x" % self.line,
                "%06x" % self.seg,
                "%02x" % self.vpid,
                "%05x" % self.pg,
                "%x" % self.d,
                "%x" % self.lru,
                "%x" % self.stat,
                "%x" % self.res,
                "%x" % self.spc,
            ]
        )
        return "L:%016x:%06x:%02x:%05x %016x:%02x:(%02x)" % (self.tag, self.seg, self.vpid, self.pg, self.ram1, self.ram2, self.parbit)


class XCache():

    def __init__(self, side, ctx):
        self.side = side
        self.ctx = ctx
        self.ram = ctx.body[:0x20000]
        self.rame = ctx.body[0x20000:0x22000]
        self.raml = ctx.body[0x24000:0x26000]
        self.lines = []
        for n, ptr in enumerate(range(0, len(self.ram), 8)):
            i = struct.unpack("<Q", self.ram[ptr:ptr+8])
            if n & 3 in (1, 2):
                self.lines.append(Line(self.side, n, i[0], self.raml[n >> 1]))
            else:
                self.lines.append(Line(self.side, n, i[0], self.rame[n >> 1]))

    def __iter__(self):
        yield from self.lines

class MemBoard():
    def __init__(self, acache, bcache):
        self.acache = acache
        self.bcache = bcache
        self.check_lru()

    def __iter__(self):
        yield from self.acache
        yield from self.bcache

    def check_lru(self):
        l = []
        for i in range(4096):
            l.append(set())
        for i in self:
            l[i.line >> 2].add(i.lru)
        for n, i in enumerate(l):
            if len(i) == 8:
                continue
            print("LRU trouble", n, i)
        print("End of LRU check")

    def stats(self):
        unused = [0] * 4096
        st = [0] * 4
        lru = [0] * 8
        spc = [0] * 8
        for line in self:
            if line.stat == 2 and line.d:
                print("MOD but RO", line)
            st[line.stat] += 1
            lru[line.lru] += 1
            spc[line.spc] += 1
            if line.stat in (0, 3):
                unused[line.line>>2] += 1
        print("STAT\t", st)
        print("LRU\t", lru)
        print("SPC\t", spc)
        full = 0
        hist = [0] * 9
        for n, i in enumerate(unused):
            hist[i] += 1
        print("HIST\t", hist)

    def dump(self):
        for line in self:
            print(line)

def main():
    acache = None
    bcache = None
    filename = sys.argv[1]
    for ctx in context.contexts(filename=filename, regex="[.][AB]CACHE"):
        if '.ACACHE' in ctx.ident:
            acache = XCache("A", ctx)
        elif '.BCACHE' in ctx.ident:
            bcache = XCache("B", ctx)
    mem = MemBoard(acache, bcache)
    mem.stats()
    mem.dump()

if __name__ == "__main__":
    main()

