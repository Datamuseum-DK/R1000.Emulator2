from board import Board, Chain
import scan_chains

MEM_DFSM = {
    "DIPROC",
    "DFSM0",
    "DFSM1",
    "DFSM2",
    "DFSM3",
    "DFSM4",
    "DFSM5",
    "DFSM6",
}

class ChainMemDregFull(Chain):

    def __init__(self):
        super().__init__("M.DREG_VAL_PAR", 19)
        self.SUPRESS |= MEM_DFSM
        self.SUPRESS |= { "DREGC0", "DREGC1", "DREGVP", }
        for i in "TV":
            for j in range(8):
                self.SUPRESS |= { "DREG" + i + "%d" %j, }
        self.chain = scan_chains.MemDregFull()

class ChainMemDregValPar(Chain):

    def __init__(self):
        super().__init__("M.DREG_VAL_PAR", 9)
        self.SUPRESS |= MEM_DFSM
        self.SUPRESS |= { "DREGC0", "DREGC1", "DREGVP", }
        for i in "TV":
            for j in range(8):
                self.SUPRESS |= { "DREG" + i + "%d" %j, }
        self.chain = scan_chains.MemDregValPar()

class MEM_Board(Board):

    CHAINS = {
        0x01: ChainMemDregFull(),
        0x02: ChainMemDregValPar(),
    }

    DFSM0_BITS = (
        "FSM_DONE~",
        "DI_BR_SEL.0",
        "DI_BR_SEL.1",
        "DI_BR_SEL.2",
        "DI_BR_SEL.3",
        "DI_NSTATE.1",
        "DI_NSTATE.2",
        "DI_NSTATE.3",
    )

    DFSM1_BITS = (
        "DI_SCAN_SEL.0",
        "DI_SCAN_SEL.1",
        "DI_SCAN_SEL.2",
        "+DIAG_XCVR_OE~",
        "-DIAG_FLAG",
        "P_TO_S_SEL.0",
        "P_TO_S_SEL.1",
        "-b7",
    )
    DFSM2_BITS = (
        "-BUS_PROT~",
        "+DIAG_BUZZ_OFF~",
        "+D_DRVMEM~",
        "+D_DRVTAG~",
        "D_BUS_MODE.0",
        "D_BUS_MODE.1",
        "D_BUS_MODE.2",
        "D_BUS_MODE.3",
    )
    DFSM3_BITS = (
        "-TRIGGER_SCOPE",
        "D_CNTR_OP.0",
        "D_CNTR_OP.1",
        "D_CNTR_OP.2",
        "D_CNTR_OP.3",
        "D_CNTR_OP.4",
        "-D_EARLY_ABRT~",
        "-D_LATE_ABRT~",
    )
    DFSM4_BITS = (
        "DREG_S.0",
        "DREG_S.1",
        "MAR_MODE.0",
        "MAR_MODE.1",
        "MAR_MODE.2",
        "+CNTR8_LD~",
        "-D_LOAD_WDR~",
        "-D_EN_WDR~",
    )
    DFSM5_BITS = (
        "P_TO_S_S.0",
        "P_TO_S_S.1",
        "TS_PAR_MODE.0",
        "TS_PAR_MODE.1",
        "-nothing",
        "+REFRESH~",
        "-D_CMD_EN",
        "-FREEZE_EN",
    )
    DFSM6_BITS = (
        "-D_DIS_ADR",
        "TRACE_MODE.0",
        "TRACE_MODE.1",
        "TRACE_MODE.2",
        "TRACE_MODE.3",
        "+COMMAND_OE~",
        "-CMD_TRACE_DIR",
        "-TAGCOMP_EN~",
    )

    def __init__(self, unit):
        super().__init__("MEM%d" % unit, 14 - unit)

    def Ins_c0(self, adr, lines):

        if self.mem[adr+2] == 0x04:
            p = self.mem[adr+1]
            print("    LAR <= @%02x: #%02x " % (p, self.mem[p]))
            regs = {}
            for i in lines:
                if ".LARREG" in i[1]:
                    regs["1" + i[1]] = i
                elif ".SETREG" in i[1]:
                    regs["0" + i[1]] = i
            for i, j in sorted(regs.items()):
                print("    ", j)
            return True


    def DFSM0(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM0_BITS)])

    def DFSM1(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM1_BITS)])

    def DFSM2(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM2_BITS)])

    def DFSM3(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM3_BITS)])

    def DFSM4(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM4_BITS)])

    def DFSM5(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM5_BITS)])

    def DFSM6(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DFSM6_BITS)])
