from board import Board, Chain
import scan_chains

TYP_DUIRG = {
    "DIPROC",
    "DUIRG0",
    "DUIRG1",
    "DUIRG2",
    "DUIRG3",
    "DUIRG4",
    "DUIRG5",
    "DUIRG6",
    "DUIRG7",
}

class ChainTypUir(Chain):
    def __init__(self):
        super().__init__("S.UIR", 6)
        self.SUPRESS |= TYP_DUIRG
        self.SUPRESS_ = {
           "UIR01",
           "UIR23",
           "UIR45",
           "UIR67",
           "UIR89",
           "UIRA",
           "UIRP",
        }
        self.chain = scan_chains.TypUir()


class TYP_Board(Board):

    CHAINS = {
        0x5: ChainTypUir(),
    }

    DUIRG0_BITS = (
        "DIAG.HUA.0",
        "DIAG.HUA.1",
        "DIAG.HUA.2",
        "DIAG.HUA.3",
        "DIAG.HUA.4",
        "DIAG.STATE.1",
        "DIAG.STATE.2",
        "DIAG.STATE.3",
    )

    DUIRG1_BITS = (
        "+CN.DIAG_ON~",
        "+b1",
        "+BANK_SELECT~",
        "+TYPE.DIAG_ON~",
        "+FIU.DIAG_ON~",
        "+FSM_DONE~",
        "DIAG.WDR.S~.1",
        "DIAG.WDR.S~.0",
    )

    DUIRG2_BITS = (
        "+b0",
        "+A_L.DIAG_OFF~",
        "+FORCE_SP_H1~",
        "+B_L.DIAG_OFF~",
        "+TADR.DIAG_ON~",
        "+ACS.DIAG_OFF~",
        "BCS.DIAG_OFF~",
        "-DIAG.WDR.EN",
    )

    DUIRG3_BITS = (
        "+DIAG_STOP",
        "+CSA.DIAG.EN~",
        "+b2",
        "+NOVRAM.CS~",
        "+DIAG.NO_STOP",
        "+COND.DIAG.EN~",
        "+UIR.DIAG_OFF",
        "+UIR.DIAG_ON~",
    )

    DUIRG4_BITS = (
        "+B_O.DIAG_ON",
        "+C_B.DIAG_ON~",
        "+b2",
        "+A_O.DIAG_ON~",
        "+T.T_DIAG_MODE",
        "-FREEZE.EN",
        "PAREG.SEL.0",
        "PAREG.SEL.1",
    )

    DUIRG5_BITS = (
        "DIAG_WRITE.0",
        "DIAG_WRITE.1",
        "CSA.DIAG.0",
        "CSA.DIAG.1",
        "CSA.DIAG.2",
        "DIDEC.0",
        "DIDEC.1",
        "DIDEC.2",
    )

    DUIRG6_BITS = (
        "+LOOP.DIAG.LD~",
        "-LOOP.DIAG.CT~",
        "-LOOP.DIAG.EN",
        "+DIAG_CNTR.EN~",
        "+DIAG_CNTR.LD~",
        "-UIR.SEL0~",
        "-ADR.DIAG_OFF~",
        "+DIAG_UADR.SEL~",
    )

    def __init__(self):
        super().__init__("TYP", 6)

    def Ins_d4(self, adr, lines):

        if self.mem[adr+1] == 0x08 and self.mem[adr+2] == 0x41:
            print("    PAREG => 0x%02x:" % self.mem[adr+3])
            return True


    def DUIRG0(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG0_BITS)])

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

