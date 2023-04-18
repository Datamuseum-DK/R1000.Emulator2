from board import Board

class VAL_Board(Board):

    CHAINS = {
        0x30: ("WDR", 8, 0x38, [".WDR0"]),
        0x33: ("WDR", 8, 0x39, [".WDR0"]),
        0x40: ("UIR", 6, 0x3b, []),
    }

    DUIRG0_BITS = (
        "DIAG.HUA0",
        "DIAG.HUA1",
        "DIAG.HUA2",
        "DIAG.HUA3",
        "DIAG.HUA4",
        "DIAG.STATE1",
        "DIAG.STATE2",
        "DIAG.STATE3",
    )

    DUIRG1_BITS = (
        "+CN.DIAG_ON~",
        "+DIAG_MUX_SEL",
        "+BANK_SELECT~",
        "+VAL.DIAG_ON~",
        "+FIU.DIAG_ON~",
        "+FSM_DONE~",
        "DIAG.WDR.S~.1",
        "DIAG.WDR.S~.0",
    )

    DUIRG2_BITS = (
        "+b0",
        "A_L.DIAG_OFF~",
        "+FORCE_PASS_A~",
        "B_L.DIAG_OFF~",
        "+b4",
        "ACS.DIAG_OFF~",
        "BCS.DIAG_OFF~",
        "-DIAG.WDR.EN",
    )

    DUIRG3_BITS = (
        "+DIAG_STOP",
        "CSA.DIAG.EN~",
        "+b2",
        "+NOVRAM.CS~",
        "+DIAG.NO_STOP",
        "COND.DIAG.EN~",
        "+UIR.DIAG_OFF",
        "UIR.DIAG_ON~",
    )

    DUIRG4_BITS = (
        "B_O.DIAG_ON",
        "C_D.DIAG_ON~",
        "+ADR.DIAG_ON~",
        "+A_O.DIAG_ON~",
        "DIAG_MODE",
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
       "LOOP.DIAG.LD~",
       "-LOOP.DIAG.CT~",
       "-LOOP.DIAG.EN",
       "+DIAG_CNTR.EN~",
       "DIAG_CNTR.LD~",
       "-UIR.SEL0~",
       "-ADR.DIAG_OFF~",
       "+DIAG_UADR.SEL",
    )

    def __init__(self):
        super().__init__("VAL", 7)

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
