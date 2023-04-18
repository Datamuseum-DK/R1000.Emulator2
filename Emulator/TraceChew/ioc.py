
from board import Board

class IOC_Board(Board):

    RAND0_BITS = (
        "LOAD_SLICE~",
        "LOAD_DELAY~",
        "CLEAR_RTC~",
        "ENABLE_SLICE",
        "DISABLE_SLICE",
        "ENABLE_DELAY",
        "DISABLE_DELAY",
        "READ_TIMERS~",
    )
    RAND1_BITS = (
        "READ_RTC~",
        "DRIVE_TYP_INFO~",
        "DRIVE_OTHER_CB~",
        "LOAD_DIAG_CB~",
        "LOAD_ADDR~",
        "INC_ADDR",
        "RAM_WRITE",
        "DISABLE_ECC~",
    )
    RAND2_BITS = (
        "RAM_DREAD~",
        "DRIVE_RAM_DATA~",
        "GET_RESPONSE~",
        "MAKE_REQUEST~",
        "RCV_TYPE~",
        "EXIT_PROCEDURE~",
        "CLR_XFER_PERR.Y",
        "CLR_DELAY_EVENT",
    )
    RAND3_BITS = (
        "CLR_SLICE_EVENT",
        "READ_RDR.T~",
        "SET_RUNNING",
        "CLR_RUNNING",
        "TCB_TOP0",
        "TCB_TOP1",
        "TCB_TOP2",
        "TCB_TOP3",
    )
    DFREG1_BITS = (
        "DPREAD~",
        "TRACE.WR",
        "TRACE_ADDR.LD~",
        "FREEZE.EN",
        "DIAG.WCSA_CLR~",
        "DIAG.WCSA_DRV~",
        "DIAG.WCS_WE~",
        "DIAG.DRIVE_WCS~",
    )
    DFREG2_BITS = (
        "DIAG.WCS_CS~",
        "DIAG.UIRS00",
        "DIAG.UIRS01",
        "DIAG.UIRS10",
        "DIAG.UIRS11",
        "DIAG.SET4",
        "DIAG.SET2",
        "DIAG.SET1",
    )
    DFREG3_BITS = (
        "DIAG.SC_CTL~",
        "DIAG.EID_S0",
        "DIAG.EID_S1",
        "DIAG.DSC_S0",
        "DIAG.DSC_S1",
        "CLOCKSTOP.EN",
        "DIAG.WCSA_CNT~",
        "LOAD_RTC~",
    )
    DFREG4_BITS = (
        "RTC.EN~",
        "SFSTOP.EN~",
        "DIAG.CLKSTOP~",
        "DIAG.DIS_RCV",
        "DIAG.UIRCLKEN~",
        "DIAG.TRACE_EN",
        "DIAG.PAREGS0",
        "DIAG.PAREGS1",
    )
    DFREG5_BITS = (
        "DIAG.RAM_EN",
        "DIAG.WCSA_UP",
        "DIAG.TV_OFF",
        "DIAG.TV_ON",
        "DIAG.LD_WDR.EN~",
        "unused_q5",
        "FSM_DONE~",
        "DFSM_STATE0",
    )

    def __init__(self):
        super().__init__("IOC", 4)
    def Ins_bc_(self, adr, lines):
        if self.mem[adr + 1] == 0x51:
            dumsc = {}
            for i in lines:
                if "DUMSC" in i[1]:
                    dumsc[i[1]] = i
            for i, j in sorted(dumsc.items()):
                print("    ", j)
            return True

    def Ins_d2(self, adr, lines):
        if self.mem[adr + 2] == 0x10:
            j = self.mem[adr + 1]
            print("    UIR.PARITY = %x" % ((j >> 7) & 1))
            print("    UIR.SPARE = %x" % ((j >> 6) & 1))
            print("    LOAD.WDR~ = %x" % ((j >> 5) & 1))
            print("    UIR.RANDOM0 = %x" % ((j >> 4) & 1))
            print("    UIR.RANDOM1 = %x" % ((j >> 3) & 1))
            print("    UIR.RANDOM2 = %x" % ((j >> 2) & 1))
            print("    UIR.RANDOM3 = %x" % ((j >> 1) & 1))
            print("    UIR.RANDOM4 = %x" % ((j >> 0) & 1))
            rand = {}
            for i in lines:
                if "RAND" in i[1] or "CTR" in i[1]:
                    rand[i[1]] = i
            for i, j in sorted(rand.items()):
                print("   ", j)
            return True
        if self.mem[adr + 2] == 0x11:
            j = self.mem[adr + 1]
            print("    UIR.ADRBS0 = %x" % ((j >> 7) & 1))
            print("    UIR.ADRBS1 = %x" % ((j >> 6) & 1))
            print("    UIR.FIUBS0 = %x" % ((j >> 5) & 1))
            print("    UIR.FIUBS1 = %x" % ((j >> 4) & 1))
            print("    UIR.TVBS0 = %x" % ((j >> 3) & 1))
            print("    UIR.TVBS1 = %x" % ((j >> 2) & 1))
            print("    UIR.TVBS2 = %x" % ((j >> 1) & 1))
            print("    UIR.TVBS3 = %x" % ((j >> 0) & 1))
            return True
        return False

    def Ins_da(self, adr, lines):
        if self.mem[adr+1] == 0xd0 and self.mem[adr + 3] == 0x20:
            p = self.mem[adr+2]
            l = ["%02x" % self.mem[x] for x in range(p, p + 16)]
            print("    DUMMY = @%02x: " % p + " ".join(l))
            dumsc = {}
            for i in lines:
                if "DUMSC" in i[1]:
                    dumsc[i[1]] = i
            for i, j in sorted(dumsc.items()):
                print("    ", j)
            return True
        if self.mem[adr+1] == 0xd2 and self.mem[adr + 3] == 0x21:
            return True

    def BDDRV1(self, line):
        self.f374(
            line,
            "I.FIU_F.EN~",
            "I.TYP_F.EN~",
            "I.VAL_F.EN~",
            "I.SEQ_F.EN~",
            "I.FIU_A.EN~",
            "I.TYP_A.EN~",
            "I.VAL_A.EN~",
            "I.SEQ_A.EN~",
        )

    def DFREG1(self, line):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        self.explines.append(line + [self.explain_bits(v, self.DFREG1_BITS)])

    def DFREG2(self, line):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        self.explines.append(line + [self.explain_bits(v, self.DFREG2_BITS)])

    def DFREG3(self, line):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        self.explines.append(line + [self.explain_bits(v, self.DFREG3_BITS)])

    def DFREG4(self, line):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        self.explines.append(line + [self.explain_bits(v, self.DFREG4_BITS)])

    def DFREG5(self, line):
        if len(line[-1]) < 8:
            v = int(line[-1], 16)
        else:
            v = int(line[-1], 2)
        self.explines.append(line + [self.explain_bits(v, self.DFREG5_BITS)])

    def DFREG6(self, line):
        self.f374(
            line,
            "HUA0",
            "HUA1",
            "HUA2",
            "HUA3",
            "HUA4",
            "DFMS.STATE1~",
            "DFMS.STATE2~",
            "DFMS.STATE3~",
        )

    def RAND0(self, line):
        v = int(line[-1], 16)
        self.explines.append(line + [self.explain_bits(v, self.RAND0_BITS)])

    def RAND1(self, line):
        v = int(line[-1], 16)
        self.explines.append(line + [self.explain_bits(v, self.RAND1_BITS)])

    def RAND2(self, line):
        v = int(line[-1], 16)
        self.explines.append(line + [self.explain_bits(v, self.RAND2_BITS)])

    def RAND3(self, line):
        v = int(line[-1], 16)
        self.explines.append(line + [self.explain_bits(v, self.RAND3_BITS)])
