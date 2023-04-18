#!/usr/local/bin/python3
#
# Copyright (c) 2022 Poul-Henning Kamp
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
   {Front|Back}-Plane
   ==================
'''

import os

import transit
import util

from scmod import SystemCModule
from net import Net

class PlaneSignal():
    ''' A signal on a plane collected from G[BF] parts '''

    def __init__(self, cpu, name, defval = None):
        self.cpu = cpu
        self.planename = name
        self.name = name
        self.sortkey = util.sortkey(name)
        self.nets = []
        self.net = Net(name)
        self.net.on_plane = self
        self.scms = {}
        self.is_supply = False
        self.defval = defval

    def __repr__(self):
        return "<PlaneSignal " + self.name + ">"

    def table_row(self):
        ''' Emit our row in the table '''
        rval = []
        rval.append(self.name)
        rval.append(self.net.name)

        for board in self.cpu.boards:
            net = self.scms.get(board.scm_uname)
            if net is not None:
                nname = net.name.split('/')[-1]
                rval.append(nname)
            else:
                rval.append("-")
        return "".join(x.ljust(19) for x in rval)

    def __lt__(self, other):
        return self.sortkey < other.sortkey

    def add_net(self, net):
        ''' Add a network to this plane signal '''
        assert net.scm
        if net.on_plane == self:
            return
        if net.on_plane is not None:
            print("SS", self, net, net.on_plane)
            assert net.on_plane is None
        self.is_supply |= net.is_supply
        self.nets.append(net)
        assert len(self.nets) == len(set(self.nets))
        assert None not in set(x.scm for x in self.nets)
        bname = net.scm.scm_uname.split('_')[0]
        if bname not in self.scms:
            self.scms[bname] = net
        net.on_plane = self

    def chew(self):
        ''' Chew on things '''
        self.divine_better_name()
        if self.name[0] == "p" and self.name[1:2].isdigit() and self.name[3] == "_":
            self.name = self.name[4:]
        #print("CHPS", self.planename, self, list(sorted(self.scms.keys())))
        self.sortkey = util.sortkey(self.name)
        self.net.name = self.name
        self.cpu.plane.add_net(self.net)
        while self.nets:
            assert self.nets[0].scm
            self.net.adopt(self.nets.pop(0))

        if self.defval is not None:
            self.net.default = self.defval

    def divine_better_name(self):
        ''' Divine a better name '''

        # Entirely heuristic…
        # EMU we control
        # SEQ seems to have more communicative names
        for pfx, bname in (
            (None, "EMU"),
            ("Q.", "SEQ"),
            ("I.", "IOC"),
            ("F.", "FIU"),
            ("T.", "TYP"),
            (None, "MEM32"),
            (None, "SEQ"),
        ):
            net = self.scms.get(bname)
            if not net:
                continue
            nname = net.name
            if not pfx:
                self.name = nname
                return
            if nname[:2] == pfx:
                self.name = nname[2:]
                return

            if nname[0] == "p" and nname[3:6] == "_" + pfx:
                self.name = nname[6:]
                return

        # If there is only one net, use that.
        if len(self.nets) == 1:
            self.name = list(self.nets)[0].name.split('/')[-1]
            if self.name[0].isupper() and self.name[1] == ".":
                self.name = self.name[2:]
            return

        # If all else fails, continue with G[BF]%03d
        print("Plane signal name divination failed", self.name, self.scms)
        for i in self.scms.values():
            print("  avs", i, i.name)

class Planes(SystemCModule):

    ''' {Front|Back}-planes '''

    def __init__(self, cpu):
        self.cpu = cpu
        self.psig = {}

        pusig = PlaneSignal(self.cpu, "PU", defval=True)
        self.psig["PU"] = pusig

        pdsig = PlaneSignal(self.cpu, "PD", defval=False)
        self.psig["PD"] = pdsig

        super().__init__(
            os.path.join(self.cpu.cdir, "planes"),
            self.cpu.chassis_makefile,
        )

    def build_planes(self, cpu):
        ''' Find the plane signals '''
        cpu.recurse(self.chew_pull_up_down)
        cpu.recurse(self.chew_gb_gf)
        cpu.recurse(self.chew_inputs)

        for psig in sorted(self.psig.values()):
            psig.chew()

    def chew_pull_up_down(self, scm):
        ''' Join together all the pu/pd signals '''
        for comp in scm.iter_components():
            if comp.partname in ("PU", "Pull_Up"):
                for node in comp.iter_nodes():
                    node.net.is_supply = True
                    self.psig["PU"].add_net(node.net)
                    node.remove()
                comp.eliminate()
            elif comp.partname in ("PD", "Pull_Down"):
                for node in comp.iter_nodes():
                    node.net.is_supply = True
                    self.psig["PD"].add_net(node.net)
                    node.remove()
                comp.eliminate()

    def chew_inputs(self, scm):
        ''' Tie all unconnected inputs to PU '''
        for net in scm.iter_nets():
            if len(net) > 1 or net.on_plane:
                continue
            for node in net.iter_nodes():
                if not node.pin.type.output:
                    self.psig["PU"].add_net(node.net)

    def chew_gb_gf(self, scm):
        ''' Tie together GB and GF signals '''
        for comp in scm.iter_components():
            if comp.partname not in ("GB", "GF"):
                continue
            oref = comp.ref[:2] + "%03d" % int(comp.ref[2:], 10)
            bname = comp.scm.scm_uname.split("_")[0]
            nref, defval = transit.do_transit(bname, oref)
            psig = self.psig.get(nref)
            if not psig:
                psig = PlaneSignal(self.cpu, nref)
                psig.defval = defval
                self.psig[nref] = psig

            for node in comp.iter_nodes():
                psig.add_net(node.net)
                node.remove()
            comp.eliminate()

    def produce(self):
        ''' Produce the SystemC sources '''
        self.make_table(self.sf_cc)
        self.add_member("sc_trace_file *tf;")
        super().produce()

    def make_table(self, dst):
        ''' Document the resulting planes in C comment '''
        dst.write("//".ljust(47))
        dst.write("".join(x.scm_uname.split("_")[0].ljust(19) for x in self.cpu.boards) + "\n")
        for signame, psig in sorted(self.psig.items()):
            if psig.is_supply:
                dst.write("// " + signame + " <supply>\n")
            else:
                dst.write("// " + signame + " " + psig.table_row() + "\n")
