import sys
import context

def main():
    filename = sys.argv[1]
    i = list(sorted(context.contexts(filename=filename, regex="_RF")))
    print(i)
    print(len(i[0].body), len(i[1].body))
    for j in range(1024):
        t = int(bytes(reversed(i[0].body[j*8:j*8+8])).hex(), 16)
        v = int(bytes(reversed(i[1].body[j*8:j*8+8])).hex(), 16)
        k = j ^ 0x3ff
        print("%03x %02x:%02x %016x %016x" % (j, k>>5, k & 0x1f, t, v))
        if not k & 0x1f:
             print()


if __name__ == "__main
    main()
