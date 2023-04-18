
import sys
import context

def main():
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        regex = sys.argv[2]
    else:
        regex = None
    for ctx in context.contexts(filename=filename, regex=regex):
        print(ctx, len(ctx.body))
        for i in range(0, len(ctx.body), 16):
            print("%08x" % i, ctx.body[i:i+16].hex())


if __name__ == "__main__":
    main()

