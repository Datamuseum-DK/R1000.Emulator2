
import sys
import struct

import context

SPACES = ["Resr", "Ctrl", "Type", "Que.", "Data", "Impo", "Code", "Syst"]
STATES = ["Ld", "Ro", "Rw", "Iv"]

class Tag():
    def __init__(self, slot, octets):
        self.slot = slot
        self.le = struct.unpack("<Q", octets)[0]
        # ...|...|...|...|...|...|...|...|...|...|...|...|...|...|...|...|
        # ooooooooooooooooooooooooooooooooppppppppppppppppp   LLLLSS   sss
        self.obj = self.le >> 32
        self.pg = (self.le >> 13) & 0x7ffff
        self.d = (self.le >> 12) & 0x1
        self.lru = (self.le >> 8) & 0xf
        self.state = (self.le >> 6) & 0x3
        self.ucode = (self.le >> 3) & 0x7
        self.space = self.le & 0x7
        self.ptr = (self.slot & 0x7) << 22
        self.ptr |= (self.slot >> 3) << 10

    def __repr__(self):
        return " ".join(
            (
                "T",
                "slot %05x" % self.slot,
                "obj %08x" % self.obj,
                "space %x" % self.space,
                SPACES[self.space],
                "page %x" % self.pg,
                "d %x" % self.d,
                "lru %x" % self.lru,
                "state %x" % self.state,
                STATES[self.state],
                "ucode %x" % self.ucode,
                "> %08x" % self.ptr,
            )
        )

    def __lt__(self, other):
        if self.obj != other.obj:
            return self.obj < other.obj
        if self.space != other.space:
            return self.space < other.space
        if self.pg != other.pg:
            return self.pg < other.pg
        return self.le < other.le


class Mem():

    def __init__(self, context_file):
        self.tag_ctx = list(context.contexts(filename=context_file, regex="MEM.ram"))[0]
        self.ram_ctx = list(context.contexts(filename=context_file, regex="MEM.bitt"))[0]

        print(self.ram_ctx)
        self.tags = []
        for p in range(0, len(self.tag_ctx.body), 8):
            self.tags.append(Tag(p >> 3, self.tag_ctx.body[p:p+8]))

        for tag in sorted(self.tags):
            print(tag)
            pg = self.ram_ctx.body[tag.ptr:tag.ptr + (1<<10)]
            for o in range(0, len(pg), 16):
                t, v = struct.unpack("<QQ", pg[o:o+16])
                print("   %02x %08x %016x %016x" % (o >> 4, (o + (tag.pg<<10))<<3, t, v))

def main():
    m = Mem(sys.argv[1])

if __name__ == "__main__":
    main()

