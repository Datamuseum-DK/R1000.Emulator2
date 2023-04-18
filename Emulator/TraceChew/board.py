
from pyreveng import mem, assy, data, listing
from exp_disass import R1kExp

class Chain():


    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.SUPRESS = set()
        self.chain = None

    def __repr__(self):
        return "<Chain " + self.name + " %d>" % self.length

    def render_da(self, board, adr, lines):
        through_register = board.mem[adr + 1] & 1
        mode = (board.mem[adr + 1] >> 1) & 7
        data = None
        if mode == 0:
            # SND
            txt = "    " + self.name + " <= "
            if through_register:
                txt += "@R2 "
                src = board.mem[0x12]
            else:
                src = board.mem[adr + 2]
            txt += "0x%02x: " % src
            data = [board.mem[x] for x in range(src, src + self.length)]
            txt += " ".join("%02x" % x for x in data)
            print(txt)
        elif mode == 1:
            # RCV
            txt = "    " + self.name + " => "
            if through_register:
                txt += "@R3 "
                dst = board.mem[0x13]
            else:
                dst = board.mem[adr + 2]
            txt += "0x%02x: " % dst
            data = board.data_after[dst:][:self.length]
            txt += " ".join("%02x" % x for x in data)
            print(txt)
        else:
            print("RENDER chain", self, mode, through_register, self.SUPRESS)
        if data is not None:
            self.explain(data)
        for i in lines:
            chip = i[1].split('.')[-1]
            if chip not in self.SUPRESS:
                print("    ", i)
        return True

    def explain(self, data):
        if self.chain:
            for i in self.chain.explain(data):
                print("\t" + i)

    def do_chain(self, adr, lines, reg, length, tbl, regs):
        mode = self.mem[adr + 1] & 3
        tp = adr + 2
        if mode == 0:
            p = self.mem[adr + 2]
            tp += 1
            q = "<= 0x%02x: "
        elif mode == 1:
            p = self.mem[0x12]
            q = "<= @R2 0x%02x: "
        elif mode == 2:
            p = self.mem[adr + 2]
            tp += 1
            q = "=> @R3 0x%02x: "
            tbl += 1
        elif mode == 3:
            p = self.mem[0x13]
            q = "=> @R3 0x%02x: "
            tbl += 1
        if not mode & 2:
            l = ["%02x" % self.mem[x] for x in range(p, p + length)]
        else:
            l = ["__"] * length
        if self.mem[tp] != tbl:
            msg = "TABLE MISMATCH e:%02x g:%02x" % (tbl, self.mem[tp])
        else:
            msg = ""
        print("   ", reg, q % p, " ".join(l), msg)
        cache = {}
        for i in lines:
            for j in regs:
                if j in i[1]:
                    cache[i[1]] = i
        for i, j in sorted(cache.items()):
            print("    ", j)
        return True

class Board():

    CHAINS = {}

    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.mem = mem.ByteMem(0, 0x100, attr=2)
        self.dlpt = 0x0f # space for length byte
        self.expins = None
        self.explines = []
        self.src = {}
        self.handlers = { }
        self.signals = { }
        self.dbus_state = -1
        self.tref = 0

    def consume(self, line):
        if line[1][-4:] == "PROC":
            self.diproc(line)
            return
        if line[2] == "FIRMWARE":
            return
        line[0] = int(line[0]) - self.tref
        chip = line[1].split(".")[-1]
        func = getattr(self, chip, None)
        if func:
            func(line)
        else:
            self.explines.append(line)

    def finish(self):
        return

    def diproc(self, line):
        if line[2] == "DIAGBUS":
            self.diagbus(line)
            return
        if line[2] == "Instr":
            line[0] = int(line[0]) - self.tref
            if "|MOVX" in line:
                self.explines.append(line)
            elif "|sfr" in line and ( "P2" in line or "P1" in line ):
                self.explines.append(line)
            return
        if line[2] != "Exec":
            return
        self.tref = int(line[0])
        self.one_ins(line)
        self.expins = line
        if line[5] == "5c": # END
            self.one_ins(None)

    def diagbus(self, line):
        if line[3] == "TX":
            return
        # print("DB", self.name, self.dbus_state, line)
        if self.dbus_state == -1:
            if line[5] == "A_DOWNLOAD" and line[6] == self.name:
                self.mem = mem.ByteMem(0, 0x100, attr=2)
                #print("DLD START", self.name)
                self.dbus_state = 0
                self.dlpt = 0x0f
            return
        if line[-1] == "payload" and self.dbus_state == 0:
            self.mem[self.dlpt] = int(line[4], 16)
            #print("DLD DATA", "0x%02x" % self.dlpt, "0x%02x" % self.mem[self.dlpt])
            if self.dlpt == 0x10 + self.mem[0xf]:
                #print("DLD END", self.name)
                self.dbus_state = -1
                self.disass()
            else:
                self.dlpt += 1

    def disass(self):
        cx = R1kExp(board=self.name)
        cx.m.map(self.mem, 0)
        cx.code_base = self.mem[0x10]
        cx.subrs = set()
        cx.disass(cx.code_base)
        print(self.name, "EXPERIMENT")
        print("=" * 80)
        fn = "/tmp/_r1ktrace"
        listing.Listing(
            cx.m,
            fn=fn,
            ncol=5,
            lo=0x10,
            charset=False,
        )
        self.src = {}
        for i in open(fn):
            i = i.rstrip()
            j = int(i[:2], 16)
            i = i[:2] + ":" + i[2:]
            self.src[j] = i
            print(i)

    def one_ins(self, next):
        if self.expins:
            adr = int(self.expins[3], 16)
            print("-" * 80)
            print(self.expins[0])
            print(self.src.get(adr))
            for i in range(10, len(self.expins), 16):
                print("   %02x: " % (i + 6), " ".join(self.expins[i:i + 16]))
            for n, i in enumerate(self.expins[10:]):
                self.mem[n + 0x10] = int(i, 16)
            if next:
                self.data_after = [-1] * 16 + [int(x, 16) for x in next[10:]]
            else:
                self.data_after = []
            try:
                ins = self.mem[adr]
                ins_hdl = "Ins_%02x" % ins
            except mem.MemError:
                ins = None
                ins_hdl = "_nonexistent"
            handler = getattr(self, ins_hdl, None)
            if not handler or not handler(adr, self.explines):
                for i in self.explines:
                    print("   ", " ".join(str(x) for x in i))
        self.expins = None
        self.explines = []

    def update_signal(self, line, signal, state):
        old = self.signals.get(signal)
        if old != state:
            self.explines.append(line[:2] + [signal + (" = 1" if state else " = 0")])
            self.signals[signal] = state

    def explain_bits(self, val, bits):
        text = {}
        for i, lbl in enumerate(bits):
            lbl = bits[i]
            mask = 0x80 >> i
            if val & mask:
                j = 1
            else:
                j = 0
            if lbl[-2] == '.':
                b = int(lbl[-1])
                k = text.setdefault(lbl[:-2], list())
                while len(k) <= b:
                    k.append(0)
                k[b] = j
                continue
            if lbl[0] == '+':
                if not val & mask:
                    text[lbl[1:]] = "0"
            elif lbl[0] == '-':
                if val & mask:
                    text[lbl[1:]] = "1"
            else:
                text[lbl] = str(j)

        return ", ".join(x + "=" + str(y) for x, y in sorted(text.items()))

    def just_bits(self, val, bits):
        if len(val) < 8:
            v = int(val, 16)
        else:
            v = int(val, 2)
        return bin((1<<8)|v)[3:] + " " + self.explain_bits(v, bits)

    def f374(self, line, *signals):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        for i in signals:
            self.update_signal(line, i, v & 0x80)
            v <<= 1
        self.explines.append(line)

    def Ins_5c(self, _adr, _lines):
        print("    END")
        return True

    def do_chain(self, adr, lines, reg, length, tbl, regs):
        mode = self.mem[adr + 1] & 3
        tp = adr + 2
        if mode == 0:
            p = self.mem[adr + 2]
            tp += 1
            q = "<= 0x%02x: "
        elif mode == 1:
            p = self.mem[0x12]
            q = "<= @R2 0x%02x: "
        elif mode == 2:
            p = self.mem[adr + 2]
            tp += 1
            q = "=> @R3 0x%02x: "
            tbl += 1
        elif mode == 3:
            p = self.mem[0x13]
            q = "=> @R3 0x%02x: "
            tbl += 1
        if not mode & 2:
            l = ["%02x" % self.mem[x] for x in range(p, p + length)]
        else:
            l = ["__"] * length
        if self.mem[tp] != tbl:
            msg = "TABLE MISMATCH e:%02x g:%02x" % (tbl, self.mem[tp])
        else:
            msg = ""
        print("   ", reg, q % p, " ".join(l), msg)
        cache = {}
        for i in lines:
            for j in regs:
                if j in i[1]:
                    cache[i[1]] = i
        for i, j in sorted(cache.items()):
            print("    ", j)
        return True

    def Ins_da(self, adr, lines):
        chain_no = self.mem[adr + 1] >> 4
        chain = self.CHAINS.get(chain_no)
        if chain:
            return chain.render_da(self, adr, lines)
        return False

    def Ins_d8(self, _adr, _lines):
        print("    DFSM_RESET")
        return True
