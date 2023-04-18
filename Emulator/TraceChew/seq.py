from board import Board, Chain
import scan_chains 

SEQ_DUIRG = {
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

class ChainSeqTypVal(Chain):
    def __init__(self):
        super().__init__("S.TYPVAL", 16)
        self.SUPRESS |= SEQ_DUIRG
        for i in range(16):
            self.SUPRESS.add("SEQDG%X" % i)
        self.chain = scan_chains.SeqTypVal()

class ChainSeqUir(Chain):
    def __init__(self):
        super().__init__("S.UIR", 6)
        self.SUPRESS |= SEQ_DUIRG
        self.SUPRESS |= {
           "UIR01",
           "UIR23",
           "UIR45",
           "UIR67",
           "UIR89",
           "UIRA",
           "UIRP",
        }
        self.chain = scan_chains.SeqUir()

class ChainSeqDecoder(Chain):

    def __init__(self):
        super().__init__("S.DECODER", 5)
        self.SUPRESS |= SEQ_DUIRG
        self.SUPRESS |= {
            "DECDG0",
            "DECDG1",
            "DECDG2",
            "DECDG3",
        }
        self.chain = scan_chains.SeqDecoder()

class ChainSeqMisc(Chain):

    def __init__(self):
        super().__init__("S.MISC", 9)
        self.SUPRESS |= SEQ_DUIRG
        # self.SUPRESS |= { "UADR", }
        self.chain = scan_chains.SeqMisc()

class SEQ_Board(Board):


    CHAINS = {
	0x9: ChainSeqTypVal(),
	0xa: ChainSeqUir(),
	0xb: ChainSeqDecoder(),
	0xc: ChainSeqMisc(),
    }

    DUIRG1_BITS = (
        "LOCL_STOP.DIAG~",
        "BUS_OFF.DIAG",
        "+TYP_ON.DIAG~",
        "+VAL_ON.DIAG~",
        "+FIU_ON.DIAG~",
        "+DIAG_MODE~",
        "DIAG.FORCE_CLK",
        "DV_UADR~.DIAG",
    )

    DUIRG2_BITS = (
        "DOUBLE_CLK.FSM",
        "-UADR_PAR.DIAG",
        "+LD_CNT.LOW~",
        "+BUZ_OFF.DIAG",
        "+RND_SEL.DIAG",
        "+WCS_PAR.DIAG",
        "+COUNT.EN~",
        "-WCS.WE",
    )

    DUIRG3_BITS = (
        "ALWAYS.MODE.0",
        "ALWAYS.MODE.1",
        "UIR.MODE.0",
        "UIR.MODE.1",
        "DECODER.MODE.0",
        "DECODER.MODE.1",
        "DG_SEQ.MODE.0",
        "DG_SEQ.MODE.1",
    )

    DUIRG4_BITS = (
        "-DSYNC.FSM",
        "DIAG_STOP",
        "SCAN.MODE.0",
        "SCAN.MODE.1",
        "-CUR_DV~.DIAG",
        "+DEC_WRITE.OE~",
        "-DEC_CS.DIAG",
        "+DEC_WE~.DIAG",
    )

    DUIRG5_BITS = (
        "FSM_DONE~",
        "-SYNC_FREZ.EN",
        "+NOVRAM.WE~",
        "+NOVRAM.CS~",
        "+NOVRAM.STORE~",
        "DEC.0",
        "DEC.1",
        "DEC.2",
    )

    DUIRG6_BITS = (
        "DGRG_TYP.OE~",
        "DGRG_VAL.OE~",
        "ADR_OFF.DIAG~",
        "DFREEZE.FSM~",
        "COUNT.UP",
        "LD_CNT.HIGH~",
        "ADR_ON.DIAG~",
        "PREDECODE.FSM",
    )

    DUIRG7_BITS = (
        "FSM_BANK_SELECT",
        "PARITY_CHK.EN",
        "FLIP_VAL.DRV",
        "DG_SEQ_V.MODE.0",
        "DG_SEQ_V.MODE.1",
        "LOC_STOP.DIAG2~",
        "b6",
        "STOP_MACH.ME~",
    )

    def __init__(self):
        super().__init__("SEQ", 2)

    def Ins_cb(self, adr, lines):

        if self.mem[adr+1] == 0x31:
            print("    SEQDG.L => @R3 (@0x%02x) = 0x%02x" % (self.mem[0x13], self.data_after[self.mem[0x13]]))
            return True

    def Ins_c4(self, adr, lines):
        if self.mem[adr + 2] == 0x43:
            return True

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

    def DUIRG7(self, line):
        self.explines.append(line[:2] + [self.just_bits(line[-1], self.DUIRG7_BITS)])
