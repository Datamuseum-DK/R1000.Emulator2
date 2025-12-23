#!/usr/bin/env python3

'''
   Dump trace from IOC's microaddress trace RAM(s)
'''

import struct
import context

def main():
    ''' ... '''
    tram = [0] * 2049
    for ctx in context.contexts():
        if "IOC_TRAM" not in ctx.ident:
            continue
        tram = list(struct.unpack("2049H", ctx.body[:2049*2]))
        break
    tcnt = tram.pop(-1)
    if sum(tram) == 0:
        print("NO UTRACE")
        return
    print("UTRACE:", hex(tcnt))
    tcnt &= 0x3ff
    trace = list(tram[tcnt:] + tram[:tcnt])
    while trace[0] == 0:
        trace.pop(0)
    for i in trace:
        print("    %04x" % i)

if __name__ == "__main__":
    main()
