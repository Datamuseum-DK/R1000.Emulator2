
import sys

class xtrace():
    def __init__(self, filename, component):
        self.dig = {}
        self.ingest(filename, component)

    def ingest(self, filename, component):
        prev = None
        for i in open(filename):
            if component not in i:
                continue
            j = i.split(component)
            t = j[0].split()[2] + " ^ " + j[1]
            if prev is not None:
                y = prev.get(t, 0)
                prev[t] = y + 1
            prev = self.dig.setdefault(t, {})
        print(len(self.dig), "nodes")

    def dotfile(self, filename):
        with open(filename, "w") as file:
            file.write("digraph {\n")
            file.write("rankdir=LR\n")
            states = {}
            for i, j in self.dig.items():
                if i not in states:
                    states[i] = self.dot_node(file, i)
                for k, n in j.items():
                    if k not in states:
                        states[k] = self.dot_node(file, k)
                    file.write(states[i] + " -> " + states[k] + ' [label="%s"]' % n + "\n")
            file.write("}\n")

    def dot_node(self, file, rec):
        lbl = rec.strip()
        while lbl[-1] in " ^":
            lbl = lbl[:-1]

        t0 = int(lbl.split(maxsplit=1)[0])
        attr = '"'
        if t0 == 15:
            attr += ', color=red, penwidth=2'
        elif t0 == 65:
            attr += ', color=green, penwidth=2'
        elif t0 == 115:
            attr += ', color=blue, penwidth=2'
        elif t0 == 165:
            attr += ', color=orange, penwidth=2'
        elif 15 < t0 < 65:
            attr += ', color=red'
        elif 65 < t0 < 115:
            attr += ', color=green'
        elif 115 < t0 < 165:
            attr += ', color=blue'
        elif t0 < 15 or t0 > 165:
            attr += ', color=orange'
        lbl = [x.strip() for x in lbl.split('^')]
        lbl = '\\n'.join(lbl)
        nname = rec.replace("^", "").split()
        nname = "n_" + "_".join(nname)
        file.write(nname + ' [shape=box, label="' + lbl + attr + ']\n')

        return nname

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv += [ "../_work/Optimized/_r1000.trace", "TRACE" ]
    x = xtrace(*sys.argv[1:])
    x.dotfile("/tmp/_.dot")
