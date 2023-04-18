#!/usr/bin/env python3

lut = [0] * 512

def rule(p, v):
    p = p.replace('_', 'X')
    # print("R", p, "%02x" % v)
    i = p.split('X', 1)
    if len(i) == 1:
        p = p.replace('H', '1')
        p = p.replace('L', '0')
        lut[int(p, 2)] |= v
    else:
        rule(i[0] + "0" + i[1], v)
        rule(i[0] + "1" + i[1], v)

#     CGPGPGPGP
#     n00112233

# Cn+x
rule("XLX______", 0x10)
rule("HXL______", 0x10)

# Cn+y
rule("XXXLX____", 0x08)
rule("XLXXL____", 0x08)
rule("HXLXL____", 0x08)

# Cn+z
rule("XXXXXLX__", 0x04)
rule("XXXLXXL__", 0x04)
rule("XLXXLXL__", 0x04)
rule("HXLXLXL__", 0x04)

# G
rule("_X_XXXXLX", 0x02)
rule("_X_XXLXXL", 0x02)
rule("_X_LXXLXL", 0x02)
rule("_L_XLXLXL", 0x02)

# P
rule("__H_X_X_X", 0x01)
rule("__X_H_X_X", 0x01)
rule("__X_X_H_X", 0x01)
rule("__X_X_X_H", 0x01)

for i in range(512):
    lut[i] ^= 0x02

for i in range(0, 512, 8):
    print("\t" + ", ".join("0x%02x" % lut[i + x] for x in range(8)) + ",")

if False:
    for i in open("_s182.txt"):
        j = i.split()
        if len(j) != 3:
            continue
        k = j[1][13-1]
        k += j[1][3-1]
        k += j[1][4-1]
        k += j[1][1-1]
        k += j[1][2-1]
        k += j[1][14-1]
        k += j[1][15-1]
        k += j[1][5-1]
        k += j[1][6-1]
        l = int(k, 2)
        m = lut[l]
        n = j[1][12-1]
        n += j[1][11-1]
        n += j[1][9-1]
        n += j[1][10-1]
        n += j[1][7-1]
        o = int(n, 2)
        print(j, k, "0x%03x" % l, "%02x" % m, bin((1<<5)|m)[3:], n, bin((1<<5)|m^o)[3:])
