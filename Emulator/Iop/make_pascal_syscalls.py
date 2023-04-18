import sys

sys.path.append("/home/phk/Proj/R1000.Disassembly/DFS")

import dfs_syscalls

def dbgger(ptyp):
    tok = []
    if ptyp.dbg:
        tok.append(ptyp.dbg)
    elif ptyp.width == 1:
        tok.append("@B")
        tok.append(".B")
    elif ptyp.width == 2:
        tok.append("@W")
        tok.append(".W")
    elif ptyp.width == 4:
        tok.append("@L")
        tok.append(".L")
    elif ptyp.width == 8:
        tok.append("@Q")
        tok.append(".Q")
    return tok

file = open("pascal_syscalls.c", "w")

file.write("/* Machine-generated, see %s */\n" % __file__)

for fscall in sorted(dfs_syscalls.base.SYSCALLS.values()):
    if not fscall.pascal:
        continue
    if 0 and not "Cat" in fscall.name:
        continue
    #print("//", fscall)
    nm = fscall.name.split('(')[0]
    pascal = fscall.pascal
    calltok = []
    rettok = []
    for sentry in pascal.stack:
        #print("//\t", sentry, sentry.offset)

        if sentry.name == "RETURN":
            rettok.append("'>'")
            rettok.append("sp+%d" % (sentry.offset//2))
            rettok += dbgger(sentry.ptyp)
            rettok.append(",")
            continue

        if sentry.var:
            calltok.append("'!'")
            calltok.append("sp+%d @L" % (sentry.offset//2 + 2))
        else:
            calltok.append("sp+%d" % (sentry.offset//2 + 2))
        calltok.append("'%s='" % sentry.name)
        calltok += dbgger(sentry.ptyp)
        calltok.append(",")

        if sentry.mod :
            rettok.append("sp+%d" % (sentry.offset//2))
            rettok.append("'%s='" % sentry.name)
            rettok += dbgger(sentry.ptyp)
            rettok.append(",")
        elif sentry.var:
            rettok.append("sp+%d @L" % (sentry.offset//2))
            rettok.append("'%s='" % sentry.name)
            rettok += dbgger(sentry.ptyp)
            rettok.append(",")

    if calltok:
        calltok.pop(-1)
    if rettok:
        rettok.pop(-1)

    #print("// >C\t", calltok)

    #print("// >R\t", rettok)

    file.write('\t{ 0x%05x, "`%s",\n' % (fscall.adr, nm))
    file.write('\t    "%s",\n' % (' '.join(calltok)))
    file.write('\t    "%s",\n' % (' '.join(rettok)))
    file.write('\t},\n')

    
