#!/usr/local/bin/python3
#
# Copyright (c) 2021 Poul-Henning Kamp
# All rights reserved.
#
# Author: Poul-Henning Kamp <phk@phk.freebsd.dk>
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

'''
   PAL chips
   =========
'''

from part import PartModel, PartFactory

PIN_NAMES = {
    "BUSPAL": {
        1: "q4", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "cmd3", 6: "mcyc2_nxt", 7: "dbusmode0",
        8: "dbusmode1", 9: "dbusmode2", 10: "dbusmode3", 11: "seta_sel", 13: "setb_sel",
        14: "wdrb_sel", 15: "dreg_oe", 16: "tagb_oe", 17: "taga_oe", 18: "int_boe", 19: "int_aoe",
        20: "rdr_sel", 21: "wdra_sel", 22: "tagb_dir", 23: "taga_dir",
    },
    "CMDPAL": {
        1: "h2", 2: "mcmd0", 3: "mcmd1", 4: "mcmd2", 5: "mcmd3", 6: "cmdcont", 7: "early_abort",
        8: "mcyc1_hd", 9: "mcyc2_next_hd", 11: "mcyc2_hd", 13: "refresh", 14: "mcyc2",
        15: "mcyc1", 16: "mcyc2_next", 17: "cmd3", 18: "cmd2", 12: "cmd1", 19: "cmd0",
    },
    "CNTRPAL": {
        1: "q4", 2: "refresh", 3: "diag_0", 4: "diag_1", 5: "diag_2", 6: "diag_3", 7: "d_cnt_op0",
        8: "d_cnt_op1", 9: "d_cnt_op2", 10: "d_cnt_op3", 11: "d_cnt_op4", 13: "cnt8_ovf",
        14: "cnt8_en", 19: "traddr0", 20: "traddr1", 21: "traddr2", 22: "traddr3", 23: "d_cnt_ovf"
    },
    "DIBRPAL": {
        1: "d_state0", 2: "br_sel0", 3: "br_sel1", 4: "br_sel2", 5: "br_sel3", 6: "cnt_ovf",
        7: "d_mode", 8: "d_cond", 9: "par_err", 11: "d_sync", 17: "branch_a", 18: "branch_b",
        12: "continue", 19: "nstate0",
    },
    "DISTPAL": {
        1: "clk", 2: "nstate1", 3: "nstate2", 4: "nstate3", 5: "nstate0", 6: "continue",
        7: "branch", 8: "freeze", 9: "start", 16: "state3", 17: "state2", 18: "state1",
        19: "state0",
    },
    "DRADPAL": {
        1: "clk", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "dis_adr", 6: "h1", 7: "mcyc2",
        8: "phys_hit26", 9: "lar2", 10: "lar3", 11: "trace_dra1", 13: "trace_dra2", 14: "bl_hit",
        15: "be_hit", 16: "al_hit", 17: "ae_hit", 18: "drb_a2lp", 19: "dra_a2lp", 20: "drb_a1",
        21: "dra_a1", 23: "dra2_el_sel",
    },
    "DRCPAL": {
        1: "clk", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "cmd3", 6: "h1", 7: "mcyc2_next",
        8: "mcyc2", 9: "ahit", 10: "bhit", 11: "late_abort", 13: "d_dis_adr", 14: "col_adr_oe",
        15: "row_adr_oe", 16: "tag_write", 17: "nameq", 18: "dr_web", 19: "dr_wea",
        20: "cas_b", 21: "cas_a", 22: "ras_b", 23: "ras_a",
    },
    "LUXXPAL": {
        4: "soil", 5: "lpar", 6: "lru0", 7: "lru1", 8: "lru2", 9: "lru3", 10: "par6",
        11: "hit", 13: "mruisf", 23: "lru0_d", 22: "lru1_d", 21: "lru2_d", 20: "lru3_d",
        19: "par_d", 18: "par_u", 17: "lru0_u", 16: "lru1_u", 15: "lru2_u", 14: "lru3_u",
    },
    "MARPAL": {
        1: "clk", 2: "mar_mode0", 3: "mar_mode1", 4: "mar_mode2", 5: "h1", 6: "clock_stop",
        7: "load_mar", 8: "mar_perr", 9: "freeze", 12: "mar_par_err", 13: "lar_s1", 14: "lar_s0",
        15: "mar_par_oe", 16: "mar_par_s1", 17: "mar_par_s0", 18: "mar_s1", 19: "mar_s0",
    },
    "MUXEPAL": {
        2: "lru_update", 3: "tag49_q", 4: "tag50_q", 5: "mod_q", 6: "h1", 7: "soil_h", 8: "hit_h",
        9: "hit", 19: "lru2_oe", 18: "tag49_d", 17: "tag50_d", 16: "mod_d", 12: "lru0_oe",
    },
    "MUXLPAL": {
        2: "lru_update", 3: "tag49_q", 4: "tag50_q", 5: "mod_q", 6: "h1", 7: "soil_h", 8: "hit_q",
        19: "lru_oe", 18: "tag49_d", 17: "tag50_d", 16: "mod_d", 13: "hit_hd", 12: "lru1_oe",
    },
    "PHITPAL": {
        1: "pset0", 2: "pset1", 3: "pset2", 4: "pset3", 5: "hibrd", 6: "h1", 7: "dbusmode0",
        8: "dbusmode1", 9: "dbusmode2", 11: "dbusmode3", 13: "dforcehit", 14: "physhit26",
        15: "setb_sel", 16: "seta_sel", 17: "phit_bl", 18: "phit_be", 19: "phit_ae", 12: "phit_al"
    },
    "RDRPAL": {
        1: "clk", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "cmd3", 6: "h2", 7: "mcyc2_next",
        8: "seta_sel", 9: "setb_sel", 16: "vprdr", 17: "vbdr", 18: "vadr", 19: "trdr",
    },
    "SETPAL": {
        6: "h1", 8: "ae_hit", 9: "al_hit", 10: "be_hit", 11: "bl_hit", 13: "drive_hit",
        16: "bhit_456", 17: "ahit_012", 18: "hit_0246", 19: "hit_0145",
        20: "bhit_5", 21: "bhit_4", 22: "ahit_1", 23: "ahit_0",
    },
    "TAGAPAL": {
        1: "clk", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "cmd3", 6: "h1", 7: "mcyc2_nxt", 8: "mcyc2",
        9: "phys_set2", 10: "phys_set3", 11: "ts_trace_en", 13: "late_abort", 14: "tsadr_13l",
        15: "tsadr_13e", 16: "lru_update", 17: "check_tsepar", 18: "taga13_y", 19: "taga12_y",
        21: "d_bus_mode3", 22: "tsadr_12l", 23: "tsadr_12e",
    },
    "TPARPAL": {
        1: "check_tsepar", 2: "tag_par_err", 3: "ts_par_mode0", 4: "ts_par_mode1", 5: "h1",
        6: "tsa_perr", 7: "tsa_perr_od", 8: "tsb_perr", 9: "tsb_perr_od", 11: "mar_par_err",
        13: "par_err", 14: "tsa_par_err", 15: "tsb_par_err", 16: "tag_par_err", 12: "ts_par_s1",
        18: "ts_epar_dis", 19: "ts_par_s0",
    },
    "TRACPAL": {
        2: "h1", 3: "t_mode0", 4: "t_mode1", 5: "t_mode2", 6: "t_mode3", 7: "refresh",
        8: "tsa_par_out", 9: "tsb_par_out", 14: "ts_trace_en", 15: "tradr_13", 16: "tradr_12",
        17: "ts_dram_oe", 18: "cntr8_oe", 19: "tracing", 20: "trace_oe", 21: "tradr_oe",
        22: "tram_we", 23: "tram_ce",
    },
    "TSCPAL": {
        1: "clk", 2: "cmd0", 3: "cmd1", 4: "cmd2", 5: "cmd3", 6: "h1", 7: "mcyc2_nxt", 8: "mcyc2",
        9: "seta_sel", 10: "setb_sel", 11: "phys_set3", 13: "late_abort", 15: "tagxoe",
        16: "tagxl_we", 17: "tagxe_we", 18: "tagxx_we", 20: "tagb_ce", 21: "taga_ce",
        22: "tagxl_oe", 23: "tagxe_oe",
    },
    "TSXXPAL": {
        1: "clk", 2: "tag_57", 3: "tag_56", 4: "tag_55", 5: "tag_54", 6: "tag_53", 7: "tag_52",
        8: "tag_51", 9: "phit_al", 10: "phit_al2", 11: "force_hit", 13: "hit_h", 14: "cmd0",
        15: "cmd1", 16: "mcyc1", 17: "lpar_q", 18: "soil_q", 20: "logq", 21: "hitq", 22: "cmd2",
        23: "cmd3",
    },
}

class PalPin():
    ''' One pin '''
    def __init__(self, up, nbr):
        self.up = up
        self.palname = up.name.split("_")[0]
        pin_names = PIN_NAMES.setdefault(self.palname, dict())
        suff = pin_names.get(nbr)
        if not suff:
            suff = "%02d" % nbr
        self.nbr = nbr
        self.name = None
        self.var = "p_" + suff
        self.pin = "pin_" + suff
        self.out = "out_" + suff
        self.olmc = None
        self.output = None
        self.inverted = False

    def __lt__(self, other):
        return self.nbr < other.nbr

    def __str__(self):
        if self.inverted:
            return "^" + self.pin
        return self.pin

    def inv(self):
        ''' invert as necessay '''
        if self.inverted:
            return "  " + self.var + " "
        return "(!" + self.var + ")"

    def buf(self):
        ''' invert as necessay '''
        if self.inverted:
            return "(!" + self.var + ")"
        return "  " + self.var + " "

class PalRow():
    ''' One row of fuses '''
    def __init__(self, up, bits):
        self.up = up
        self.bits = bits
        self.disabled = False
        self.inputs = set()
        self.terms = []

        for nbr, term in enumerate(self.up.palterms):
            fuses = self.bits[nbr * 2:nbr * 2 + 2]
            if min(fuses):
                continue
            if not max(fuses):
                self.disabled = True
                return
            self.inputs.add(term)
            if fuses[1]:
                self.terms.append((term, term.buf))
            elif fuses[0]:
                self.terms.append((term, term.inv))

    def cond(self):
        ''' C++ condition string for this row '''
        if self.disabled:
            return "false"
        if not self.terms:
            return "true"
        return " && ".join(i() for j, i in sorted(self.terms))

    def __str__(self):
        return "".join("%d" % i for i in self.bits)

class PalMacroCell():
    ''' Output Logic Macro Cell '''
    def __init__(self, up, pin, regd, rows):
        self.up = up
        self.pin = pin
        pin.olmc = self
        pin.output = self
        self.regd = regd
        self.rows = rows
        self.disabled = None
        self.inputs = set()
        self.output_enable = "true"
        self.xor = False
        self.ands = []
        for row in rows:
            self.inputs |= row.inputs

    def __lt__(self, other):
        return self.pin < other.pin

    def __str__(self):
        return "OLMC:%d" % self.pin.nbr

    def cond(self, nls = ""):
        ''' C++ condition for this output '''
        sep = " ||\n" + nls
        if not self.xor:
            return sep.join("(" + i.cond() + ")" for i in self.ands if not i.disabled)
        sep += "    "
        return "!(\n" + nls + "    " + sep.join("(" + i.cond() + ")" for i in self.ands if not i.disabled) + "\n" + nls + ")"


class GAL(PartFactory):
    ''' A generic GAL/PAL chip '''

    def __init__(self, ident, palbits):
        super().__init__(ident)

        self.palbits = palbits
        self.palpins = {}
        self.palterms = []
        self.palrows = []
        self.palolmc = []
        self.palsig = []
        self.palsyn = None
        self.palac0 = None
        self.palac1 = None
        self.palparse()

        self.palinputs = set()
        self.paloutputs = set()
        for out in self.palolmc:
            if not out.disabled:
                self.paloutputs.add(out.pin)
            self.palinputs |= out.inputs

    def palparse(self):
        ''' ... '''
        assert False

    def extra(self, file):
        file.fmt('''
		|static const sc_dt::sc_logic outs[4] = {
		|	sc_dt::sc_logic_Z,
		|	sc_dt::sc_logic_Z,
		|	sc_dt::sc_logic_0,
		|	sc_dt::sc_logic_1,
		|};
		|static const char traces[5] = "ZZ01";
		|''')

    def sensitive(self):
        for node in self.comp:
            nbr = int(node.pin.ident)
            self.palpins[nbr].name = "PIN_" + node.pin.name

        want = set()
        for out in self.paloutputs:
            if not out.olmc:
                continue
            if out.olmc.regd:
                want.add(self.palpins[1].name + ".pos()")
            else:
                for inp in out.olmc.inputs:
                    if not inp.output:
                        want.add(inp.name)
        yield from sorted(want)

    def state(self, file):
        for out in sorted(self.palolmc):
            if not out.disabled:
                file.write('\tint %s;\n' % out.pin.var)

    def doit(self, file):
        ''' The meat of the doit() function '''

        super().doit(file)

        for i in sorted(self.paloutputs):
            file.write("\tassert(0 <= state->%s);\n" % i.var)
            file.write("\tassert(3 >= state->%s);\n" % i.var)

        file.fmt('''
		|
		|	if (state->ctx.job) {
		|		TRACE(
		|''')

        for pin in sorted(self.palinputs - self.paloutputs):
            file.fmt('\t\t|\t\t    << %s?\n' % pin.name)
        file.write('\t\t    << " | "\n')
        for out in self.palolmc:
            if out.disabled:
                continue
            pin = out.pin
            if out.output_enable == "true":
                file.write('\t\t    << state->%s\n' % pin.var)
            else:
                file.write('\t\t    << traces[state->%s]\n' % pin.var)
        file.write('\t\t);\n')

        for out in self.palolmc:
            if out.disabled:
                continue
            pin = out.pin
            if "DIBR" in self.name and "branch" in pin.var:
                # Ugly hack:  SystemC does not handle two tri-state outputs tied together on
                # a single component, so we need to special-case DIBRPAL
                file.fmt('\t\t|\t\tif (state->%s > 1)\n' % pin.var)
                file.fmt('\t\t|\t\t\tPIN_D0 = outs[state->%s];\n' % pin.var)
            elif out.output_enable == "true":
                file.fmt('\t\t|\t\t%s<=(state->%s);\n' % (pin.name, pin.var))
            else:
                file.fmt('\t\t|\t\t%s = outs[state->%s];\n' % (pin.name, pin.var))
        file.write('\t\tstate->ctx.job = 0;\n')
        file.write('\t}\n')

        # Set up the input variables to the equations
        # input pins are read, outputs are set later
        for pin in sorted(self.palinputs):
            out = pin.output
            if out is not None and not out.disabled:
                file.fmt('\t\t|\tbool %s;\n' % pin.var)
            elif self.comp.nodes[pin.name[4:]].net.is_pd():
                file.fmt('\t\t|\tbool %s = false;\n' % pin.var)
            else:
                file.fmt('\t\t|\tbool %s = %s=>;\n' % (pin.var, pin.name))

        # Set up the output variables from the equations
        # registered outputs read their register
        # combinatorial outputs are set later
        for out in self.palolmc:
            if out.disabled:
                pass
            elif out.regd:
                file.write("\tint %s = state->%s & 1;\n" % (out.pin.out, out.pin.var))
            else:
                file.write("\tint %s;\n" % out.pin.out)

        has_combinatorial = False
        for out in self.palolmc:
            if not out.regd and not out.disabled:
                has_combinatorial = True

        if has_combinatorial:
            # Set inputs from outputs
            for pin in sorted(self.palinputs):
                out = pin.output
                if out is not None and not out.disabled:
                    file.write("\t%s = %s;\n" % (pin.var, out.pin.out))

            # Calculate combinatorial outputs
            for out in self.palolmc:
                if not out.regd:
                    out.write_code(file)

        if max(out.regd for out in self.palolmc):

            file.write("\tif (%s.posedge()) {\n" % self.palpins[1].name)

            # Set inputs from outputs, again
            for pin in sorted(self.palinputs):
                out = pin.output
                if out is not None and not out.disabled:
                    file.write("\t\t%s = %s;\n" % (pin.var, out.pin.out))

            # Calculate registered outputs
            for out in self.palolmc:
                if out.regd:
                    out.write_code(file, "\t")

            if has_combinatorial:
                # Set inputs from outputs, again
                for pin in sorted(self.palinputs):
                    out = pin.output
                    if out is not None and not out.disabled:
                        file.write("\t\t%s = %s;\n" % (pin.var, out.pin.out))

                # Recalculate combinatorial outputs
                for out in self.palolmc:
                    if not out.regd:
                        out.write_code(file, "\t")
            file.write("\t}\n")

        file.write("\n")
        for out in self.palolmc:
            if out.disabled:
                continue
            file.write("\tassert(0 <= %s && %s <= 1);\n" % (out.pin.out, out.pin.out))
            if out.output_enable != "true":
                file.write("\tif(%s)\n" % out.output_enable)
                file.write("\t\t%s += 2;\n" % out.pin.out)

        file.write('\n')
        i = []
        j = []
        for out in self.palolmc:
            if out.disabled:
                continue
            i.append("(" + out.pin.out + " != state->" + out.pin.var + ")")
            j.append("\t\tstate->%s = %s;" % (out.pin.var, out.pin.out))
        file.write('\tif (\n\t    %s) {\n' % (" ||\n\t    ".join(i)))
        file.write("\n".join(j) + "\n")
        file.write("\t\tstate->ctx.job = 1;\n")
        file.write("\t\tnext_trigger(5, sc_core::SC_NS);\n")
        file.write('\t}\n')

class PalMacroCell16(PalMacroCell):
    ''' GAL16V8 Output Logic Macro Cell '''

    def __init__(self, up, pin, regd, rows, xor, ac1):
        super().__init__(up, pin, regd, rows)
        self.xor = xor
        self.ac1 = ac1
        if self.ac1:
            self.ands = self.rows[1:]
        else:
            self.ands = self.rows
        self.disabled = min(i.disabled for i in rows)
        if not self.regd:
            self.output_enable = rows[0].cond()
        elif "DIBR" in self.up.name:
            p11 = self.up.palpins.get(11)
            if p11 is None:
                p11 = PalPin(up, 11)
                self.up.palpins[11] = p11
            self.output_enable = "!" + p11.var
            self.inputs.add(p11)
        for i in rows:
            self.inputs |= i.inputs

    def dump(self):
        ''' ... '''
        print(self)
        if self.ac1:
            print("\tOE = ", self.rows[0].cond())
        else:
            print("\tOE = pin11")
        cond = self.cond()
        print("\t%s =\n\t   " % self.pin, cond + ";")
        for i in self.rows:
            print(i)

    def write_code_regd_ac01(self, file, pfx):
        ''' Write code for registered mode '''
        assert not self.ac1
        file.write(pfx + self.pin.out + " =\n" + pfx + "    ")
        file.write(self.cond(pfx + "    ") + ";\n")

    def write_code_comb_ac01(self, file, pfx):
        ''' Write code for combinatorial mode '''
        assert self.ac1
        file.write(pfx + self.pin.out + " =\n" + pfx + "    ")
        file.write(self.cond(pfx + "    ") + ";\n")

    def write_code(self, file, pfx=""):
        ''' Write code for this output '''
        if self.disabled:
            return
        pfx = pfx + "\t"
        if self.regd and self.up.palac0:
            self.write_code_regd_ac01(file, pfx)
        else:
            self.write_code_comb_ac01(file, pfx)

    def __str__(self):
        return "OLMC:%d regd %d ac1 %d xor %d" % (self.pin.nbr, self.regd, self.ac1, self.xor)

class GAL16V8(GAL):
    ''' Lattice GAL16V8 '''

    def palparse(self):

        self.palsyn = self.palbits[2192]
        self.palac0 = self.palbits[2193]

        for i in range(1, 20):
            if i != 10:
                self.palpins[i] = PalPin(self, i)

        if not self.palsyn:
            for nbr in range(8):
                self.palterms.append(self.palpins[2 + nbr])
                self.palterms.append(self.palpins[19 - nbr])
        else:
            for nbr in range(8):
                self.palterms.append(self.palpins[2 + nbr])
                if nbr == 0:
                    self.palterms.append(self.palpins[1])
                elif nbr < 7:
                    self.palterms.append(self.palpins[19 - nbr])
                else:
                    self.palterms.append(self.palpins[11])

        for nbr, start in enumerate(range(0, 2048, 32)):
            self.palrows.append(PalRow(self, self.palbits[start:start+32]))
            assert self.palbits[2128 + nbr] # PTD bit

        for nbr in range(8):
            self.palolmc.append(
                PalMacroCell16(
                    self,
                    self.palpins[19 - nbr],
                    not self.palsyn,
                    self.palrows[nbr * 8: nbr * 8 + 8],
                    not self.palbits[2048 + nbr],
                    self.palbits[2120 + nbr],
                )
            )

        for nbr in range(8):
            i = ''.join("%d" % i for i in self.palbits[2056+nbr*8:2056+8+nbr*8])
            self.palsig.append(i)


class PalMacroCell22(PalMacroCell):
    ''' GAL22V10 Output Logic Macro Cell '''

    def __init__(self, up, pin, rows, s0, s1):
        super().__init__(up, pin, not s1, rows)
        self.s1 = s1
        self.xor = not s0
        if s0 and not s1:
            pin.inverted = True
        self.disabled = min(i.disabled for i in rows)
        self.output_enable = rows[0].cond()
        self.ands = self.rows[1:]
        for i in rows:
            self.inputs |= i.inputs

    def write_code(self, file, pfx=""):
        ''' Write C++ code to evaluate this output '''
        if self.disabled:
            return
        pfx = pfx + "\t"
        dst = self.pin.out
        file.write(pfx + dst + " =\n" + pfx + "    ")
        file.write(self.cond(pfx + "    ") + ";\n")

    def dump(self):
        ''' ... '''
        print(self)
        if self.s1:
            print("\tOE = ", self.rows[0].cond())
        else:
            print("\tOE = pin11")
        cond = self.cond()
        print("\t%s =\n\t   " % self.pin, cond + ";")

    def __str__(self):
        return "OLMC:%d xor %d s1 %d" % (self.pin.nbr, self.xor, self.s1)

class GAL22V10(GAL):

    ''' Lattice GAL22V10 '''

    def palparse(self):

        for i in range(24):
            if i not in (0, 12):
                self.palpins[i] = PalPin(self, i)

        for nbr in range(11):
            self.palterms.append(self.palpins[1 + nbr])
            if nbr < 10:
                self.palterms.append(self.palpins[23 - nbr])
            else:
                self.palterms.append(self.palpins[13])

        for start in range(0, 5808, 44):
            self.palrows.append(PalRow(self, self.palbits[start:start+44]))

        nxr = 1
        for nbr, rows in enumerate(
            (
                8, 10, 12, 14, 16, 16, 14, 12, 10, 8
            )
        ):
            self.palolmc.append(
                PalMacroCell22(
                    self,
                    self.palpins[23 - nbr],
                    self.palrows[nxr: nxr + rows + 1],
                    self.palbits[5808 + nbr * 2],
                    self.palbits[5809 + nbr * 2],
                )
            )
            nxr += rows + 1

        for nbr in range(8):
            i = ''.join("%d" % i for i in self.palbits[5828+nbr*8:5828+8+nbr*8])
            self.palsig.append(i)

        # Async reset not implemented
        assert self.palrows[0].cond() == "false"
        # Sync preset not implemented
        assert self.palrows[-1].cond() == "false"

class PALModel(PartModel):
    ''' ... '''

    def __init__(self, name, octets):
        self.octets = octets
        self.cls = {
            2194: GAL16V8,
            5892: GAL22V10,
        }.get(len(octets))
        assert self.cls
        super().__init__(name, self.cls)
        self.busable = False

    def create(self, ident):
        return self.factory(ident, self.octets)

    def assign(self, comp, part_lib):
        #for node in comp:
            #if node.pin.name == "OE":
            #    print("PN", node)
            # NB: For now make all outputs sc_logic
            #if "output" in node.pin.role:
            #    node.pin.role = "sc_out <sc_logic>"
        super().assign(comp, part_lib)

def iter_pals():
    ''' Read PAL bitstreams out of firmware.c "library" '''
    with open("Infra/firmware.c") as file:
        sect = []
        for line in file:
            if line[:6] != "static":
                sect.append(line)
                continue
            if "GAL" in sect[0]:
                palname = sect[0].split()[2]
                palname = palname.split('[')[0]
                palname = palname.split('_')[0]
                palname = palname.replace("GAL", "PAL")
                body = bytearray()
                for j in sect[1:]:
                    if j[0] == '}':
                        break
                    j = j.replace(",", " ")
                    j = j.replace("0x", " ")
                    body += bytearray.fromhex(j)
                yield [palname, body]
            sect = [line]

def register(part_lib):
    ''' Register component models '''

    for palname, octets in iter_pals():
        assert len(octets) in (2194, 5892)
        part_lib.add_part(palname, PALModel(palname, octets))
