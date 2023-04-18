#!/usr/bin/env python3

'''
   Dump trace from IOC's microaddress trace RAM(s)
'''

import struct
import context

def main():
    ''' ... '''
    tram = [0] * 2048
    tcnt = 0
    branch = set()
    for ctx in context.contexts():
        if "ioc_55" not in ctx.ident:
            continue
        if ctx.ident == "IOC.ioc_55.TACNT":
            i = struct.unpack("I", ctx.body[:4])
            tcnt = i[0]
            branch.add("megacomp2")
        elif ctx.ident == "IOC.ioc_55.TRAM":
            tram = struct.unpack("2048H", ctx.body)
            branch.add("megacomp2")
        elif ctx.ident == "IOC.ioc_55.TACNT0":
            i = struct.unpack("I", ctx.body[:4])
            tcnt |= i[0] << 8
            branch.add("main")
        elif ctx.ident == "IOC.ioc_55.TACNT1":
            i = struct.unpack("I", ctx.body[:4])
            tcnt |= i[0] << 4
            branch.add("main")
        elif ctx.ident == "IOC.ioc_55.TACNT2":
            i = struct.unpack("I", ctx.body[:4])
            tcnt |= i[0]
            branch.add("main")
        elif ctx.ident == "IOC.ioc_55.TRAM0":
            ram = struct.unpack("2048H", ctx.body)
            branch.add("main")
            for i in range(2048):
                tram[i] |= ram[i] << 8
        elif ctx.ident == "IOC.ioc_55.TRAM1":
            ram = struct.unpack("2048H", ctx.body)
            branch.add("main")
            for i in range(2048):
                tram[i] |= ram[i]
    if sum(tram) == 0:
        print("NO UTRACE", branch)
        return
    print("UTRACE:", hex(tcnt), branch)
    tcnt &= 0x3ff
    trace = list(tram[tcnt:] + tram[:tcnt])
    while trace[0] == 0:
        trace.pop(0)
    for i in trace:
        print("    %04x" % i)

if __name__ == "__main__":
    main()
