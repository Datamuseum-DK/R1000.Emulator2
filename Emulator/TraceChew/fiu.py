
from board import Board

from r1k_fiu_ucode import fiu_ucode

class FIU_Board(Board):

    CHAINS = {
        #0x60: ("F.MAR", 9, 0x18, [".MARN", ".MAR0",]),
        0x70: ("F.MDREG", 8, 0x10, [".MDREG",]),
        0x80: ("F.UIR", 6, 0x13, [".UIR"]),
    }

    UIR = {
        "0": ["OFFS_LIT0", "OFFS_LIT1", "OFFS_LIT2", "OFFS_LIT3"],
        "1": ["OFFS_LIT4", "OFFS_LIT5", "OFFS_LIT6", "LFL0"],
        "2": ["LFL1", "LFL2", "LFL3", "LFL4"],
        "3": ["LFL5", "LFL6", "LFREG_CNTL0", "LFREG_CNTL1"],
        "4": ["OP_SEL0", "OP_SEL1", "VMUX_SEL0", "VMUX_SEL1"],
        "5": ["FILL_MODE_SRC", "OREG_SRC", "b52", "CHAIN2"],
        "6": ["TIVI_SRC0", "TIVI_SRC1", "TIVI_SRC2", "TIVI_SRC3"],
        "7": ["LOAD_OREG~", "LOAD_VAR~", "LOAD_TAR~", "LOAD_MDR"],
        "8": ["MEM_START0", "MEM_START1", "MEM_START2", "MEM_START3"],
        "9": ["MEM_START4", "RDATA_SRC", "b92", "P"],
    }

    DUIRG1_BITS = (
        "DIAG_WCS.WE",
        "DIAG_HASH.CS",
        "+DIAG_HASH.WE~",
        "+DIAG_CLKSTP.EN~",
        "DIAG.CLKSTP~",
        "DIAG.CNT.EN",
        "+DIAG.CNT.DIS~",
        "DIAG.LD_CTR",
    )

    DUIRG2_BITS = (
       "+DIAG_MEMABORT~",
       "-DIAG_MEMHOLD~",
       "+DIAG_MCTL.EN~",
       "+DIAG_ADR.SEL",
       "MAR.SEL.0",
       "MAR.SEL.1",
       "+SCAN_MAR~",
       "-EVNT_CLKSTP.EN",
    )

    DUIRG3_BITS = (
        "-DIAG_FPAR",
        "-DIAG.APAR",
        "MDR.SEL.1",
        "MDR.SEL.0",
        "+SCAN_MDR~",
        "UIR.MODE~1",
        "+SCAN_UIR~",
        "-b7_unused",
    )

    DUIRG4_BITS = (
        "+DFREEZE.FSM~",
        "DSYNC.FSM",
        "+SEL_DIAG_CTL~",
        "DIAG_TV.EN",
        "+DIAG_T.EN~",
        "+DIAG_V.EN~",
        "+DIAG_F.EN~",
        "DIAG_ADR.EN",
    )

    DUIRG5_BITS = (
        "+FSM_DONE~",
        "-SYNC_FREZ.EN",
        "+SCAN_MISC~",
        "+READ_DIAG_BUS~",
        "+NOVRAM.WE~",
        "+NOVRAM.CS~",
        "+NOVRAM.STORE~",
        "+DT.EN~",
    )

    DUIRG6_BITS = (
        "PAREG.SEL.0",
        "PAREG.SEL.1",
        "+SCOPE_SYNC",
        "UIRCLK.EN~",
        "-MY_FREEZE.EN~",
        "+Q4~_DISABLE",
        "-SET_NSTATE0",
        "+b7_unused",
    )

    def __init__(self):
        super().__init__("FIU", 3)

    def Ins_d0(self, adr, lines):
        if self.mem[adr+2] == 0x18:
            print("    MAREG <= #%02x: " % self.mem[self.mem[adr + 1]])
            regs = {}
            for i in lines:
                if ".MAR" in i[1]:
                    regs[i[1]] = i
            for i, j in sorted(regs.items()):
                print("    ", j)
            return True

    def Ins_d2(self, adr, lines):
        if self.mem[adr+2] == 0x10:
            print("    MDREG <= #%02x: " % self.mem[adr + 1])
            return True
        if self.mem[adr+2] == 0x50:
            print("    PAREG <= #%02x: " % self.mem[adr + 1])
            return True

    def Ins_d4(self, adr, lines):
        if self.mem[adr+1] == 0x08 and self.mem[adr + 2] == 0x51:
            print("    PAREG => %02x " % self.mem[adr + 3])
            return True

    def name_uir_bits(self, lines):
        uir = {}
        for i in lines:
            if i[1][-1].isdigit and i[1][-5:-1] == ".UIR":
                uir[i[1]] = i
        ucode = {}
        for i, j in sorted(uir.items()):
            print(j)
            for x, y in self.decode_uir(j):
                ucode[x] = y
        def get_fld(pfx):
            n = 0
            v = 0
            while True:
                key = pfx + str(n)
                m = ucode.get(key)
                if m is None:
                    break
                del ucode[key]
                v <<= 1
                v |= m
                n += 1
            return v

        for fld in (
            "OFFS_LIT",
            "LFL",
            "LFREG_CNTL",
            "OP_SEL",
            "VMUX_SEL",
            "TIVI_SRC",
            "MEM_START",
        ):
            yield fld + "=0x%x" % get_fld(fld)
        for i, j in ucode.items():
            yield i + "=0x%x" % j

    def decode_uir(self, line):
        uir = line[1][-1]
        bits = self.UIR.get(uir, None)
        if not bits:
            return line
        a = []
        for i, j in zip(line[-1], bits):
            yield (j, int(i))

    def DUIRG0(self, line):
        self.f374(
            line,
            "DIAG.HUA0",
            "DIAG.HUA1",
            "DIAG.HUA2",
            "DIAG.HUA3",
            "DIAG.HUA4",
            "DIAG.STATE1",
            "DIAG.STATE2",
            "DIAG.STATE3",
        )
    def DUIRG1(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG1_BITS)])

    def DUIRG2(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG2_BITS)])

    def DUIRG3(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG3_BITS)])

    def DUIRG4(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG4_BITS)])

    def DUIRG5(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG5_BITS)])

    def DUIRG6(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG6_BITS)])
