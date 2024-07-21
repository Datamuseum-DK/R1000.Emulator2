
import sys
import context

def main():
    filename = "../_work/Optimized/_r1000.ctx"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    regex = "DUI"
    for ctx in context.contexts(filename=filename, regex=regex):
        msk = 0x80
        l = []
        while msk:
            zero = ctx.body[0x200] & msk
            one = ctx.body[0x201] & msk
            if one and not zero:
                l.append("+")
            elif zero:
                l.append("1")
            elif not one:
                l.append("0")
            else:
                print("Bogus")
                exit(2)
            msk >>= 1
        print(
            ctx,
            "%02x" % ctx.body[0x200],
            "%02x" % ctx.body[0x201],
            "".join(l)
        )


if __name__ == "__main__":
    main()

