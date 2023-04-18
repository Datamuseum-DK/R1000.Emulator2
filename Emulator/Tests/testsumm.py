
import glob

class Summarize():
    def __init__(self, test):

        name = test.split("/")[-1]
        self.test = name[1:].replace(".log", "")
        self.test = self.test.replace("mem32_0_0", "mem32")
        self.test = self.test.replace("expmon_novram", "novram")

        print("=" * 72)
        print(self.test.upper())
        print("=" * 72)

        self.lines = list(
            (i.split(), i.rstrip()) for i in open(test)
        )

        try:
            self.console = open(test.replace(".log", ".console"), "rb").read()
        except FileNotFoundError:
            self.console = b''

        try:
            self.diproc = list(x for x in open(test.replace(".log", ".diproc")))
        except FileNotFoundError:
            self.diproc = None

        try:
            self.context = list(x for x in open(test.replace(".log", ".context")))
        except FileNotFoundError:
            self.context = None

        # self.missing_chips()
        self.performance()
        self.why()
        self.experiments()

    def __lt__(self, other):
        return self.test < other.test

    def missing_chips(self):
        missing = {}
        for flds, line in self.lines:
            if len(flds) != 3:
                continue
            if flds[0] == "MISSING" and flds[2] == "IMPLEMENTATION":
                i = missing.get(flds[1], 0) + 1
                missing[flds[1]] = i
        if missing:
            print()
            print("Missing Chips:")
            for chip, count in sorted(missing.items()):
                print("\t%3d" % count, chip)

    def performance(self):
        silent = True
        self.stats = []
        for lno, line in enumerate(self.lines):
            if line[1] == "Begin statistics":
                silent = False
                print("")
                print("Statistics:")
            elif line[1] == "End statistics":
                break
            elif not silent:
                self.stats.append(line[1])
                print("\t" + line[1])
        if self.diproc:
            t = int(self.diproc[-1].split()[2]) * 1e-9
            print("\t%11.3f s\t\tLast diproc byte code" % t)
        if self.context:
            for line in self.context:
                if "Total" in line:
                    n = int(line.split()[0], 10)
                    print("\t%d\t\tTotal Activations" % n)
                    
           
    def why(self):
        for flds, line in self.lines:
            i = line.split(":")
            if i[0] == "Terminating because":
                print()
                print(i[0] + ":")
                print("\t" + i[1])
                return

    def experiments(self):
        self.exp_passed = 0
        self.exp_failed = 0
        hdr = False
        for i in self.console.split(b'\r\n'):
            j = i.split(b'\r\x1b[2K')
            final = j
            if j[-1][-10:] == b'59CPASSED ':
                final = None
                k = j[-1].split(b'\r\x1b[59C')
                self.exp_passed += len(k) - 1
                continue
            if j[-1][-10:] == b'69CFAILED ':
                final = None
                if not hdr:
                    hdr = True
                    print()
                    print("Failing experiments")
                k = j[-1].split(b'\x07\r\x1b[69C')
                self.exp_failed += len(k) - 1
                print("\t", k[0].decode("utf-8"))
                for k in j[:-1]:
                    print("\t\t", k.decode("utf-8"))
                continue
        print()
        print("Experiments ", self.exp_passed + self.exp_failed, "failed", self.exp_failed)
        if final:
            print()
            print("Final Line on Console")
            for k in final:
                print("\t\t" + str([k]))

def wikitable(tests, file):
    file.write('{| class="wikitable" style="text-align: right;"\n')
    file.write("!Test\n")
    file.write("!Wall Clock\n")
    file.write("!SystemC\n")
    file.write("!Ratio\n")
    file.write("!Exp run\n")
    file.write("!Exp fail\n")
    for i in sorted(tests):
        file.write("|-\n")
        file.write('| style="text-align: left; |' + i.test + "\n")
        n = 0
        for j in i.stats:
            if "Wall Clock Time" in j:
                n += 1
                file.write('|' + "%.3f" % float(j.split()[0]) + "\n")
            elif "SystemC simulation" in j:
                n += 1
                file.write('|' + "%.6f" % float(j.split()[0]) + "\n")
            elif "SystemC Simulation ratio" in j:
                n += 1
                file.write('|' + j.split()[0] + "\n")
        while n < 3:
            file.write("|\n")
            n += 1
        file.write("|" + str(i.exp_passed + i.exp_failed) + "\n")
        file.write("|" + str(i.exp_failed) + "\n")
    file.write("|}\n")
       


def main():
    tests = []
    for test in sorted(glob.glob("_*.log")):
        tests.append(Summarize(test))
    with open("_wiki", "w") as file:
        wikitable(tests, file)

if __name__ == "__main__":
    main()

