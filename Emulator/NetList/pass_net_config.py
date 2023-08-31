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
   Pass: Configure networks
   ========================
'''

import util

from component import Component
from net import Net
from node import Node
from pin import Pin
from scmod import ScSignal

USE_MUXBUS = False

MIN_BUS_WIDTH = 3

class MuxBus():

    ''' ... '''

    def __init__(self, netbus, width, file):
        self.netbus = netbus
        self.width = width
        self.length = len(self.netbus.nets)

        net0 = self.netbus.nets[0]
        comp0 = net0.nnodes[0].component
        self.scm = comp0.scm
        self.cpu = self.scm.cpu

        self.partref = "UBMX%d" % self.scm.scm_unique
        self.scm.scm_unique += 1

        self.muxtype = "XBUSMUX%dX%d" % (self.length, self.width)
        self.part = self.cpu.part_lib[self.muxtype]

        if 0 and net0.on_plane:
            file.write("MUX candidate but is plane\t")
            self.netbus.create_as_bus(file)
            return

        if not self.part:
            file.write("MUX candidate but no mux-part (%s)\t" % self.muxtype)
            self.netbus.create_as_bus(file)
            return

        # print("PART", self.muxtype, self.part, self.partref)

        self.pins = {}
        for j in range(self.length):

            pin = Pin(
                "Q%d" % j,
                "Q%d" % j,
                "output",
            )
            self.pins[pin.name] = pin

            for i in range(self.width):
                if not j:
                    pin = Pin(
                        "OE%c" % (i + 65),
                        "OE%c" % (i + 65),
                        "input",
                    )
                    self.pins[pin.name] = pin

                pin = Pin(
                    "I%c%d" % (i + 65, j),
                    "I%c%d" % (i + 65, j),
                    "input",
                )
                self.pins[pin.name] = pin
        # print("PINS", list(self.pins.keys()))

        file.write("MUX_CANDIDATE\t")

        self.create_mux()

        group = 64
        busgroups = []
        for key, nodes in list(self.netbus.components.items()):
            comp, pinbus = key

            if comp == self.comp or nodes[0].pin.type.name == "in":
                continue

            group += 1
            # print("GRP", group, pinbus.pins[0].type.name, pinbus.pins[0])

            # print("DN", comp, pinbus, pinbus.pins[0].type.name)
            self.netbus.detach_component(comp, pinbus)
            n = 0
            nets = []
            for oldnode in sorted(nodes):
                pin = oldnode.pin
                oldnode.remove()
                pin.set_role("output")
                newname = ""
                j = True
                for i in oldnode.net.name:
                    if j and i.isdigit():
                        newname += "_%c_" % group
                        j = False
                    newname += i
                net = Net(newname)
                self.scm.add_net(net)
                net.sc_type = "bool"
                oldnode.net = net
                oldnode.insert()
                Node(
                    net,
                    self.comp,
                    self.pins["I%c%d" % (group, n)]
                )
                n += 1
                net.move_home()
                net.find_cname()
                nets.append(net)

            busgroups.append(nets)

            oenode = comp[pinbus.oe]
            pin3 = self.pins["OE%c" % group]
            Node(
                oenode.net,
                self.comp,
                pin3,
            )
            oenode.net.move_home()
            oenode.net.find_cname()
            # print("SOE", self.comp, oenode, oenode.net)

        self.comp.make_busses()

        for nets in busgroups:
            nb2 = NetBus(self.partref, *nets)
            nb2.sort_nets()
            nb2.create(file)

        pinbus = self.pins["Q0"].pinbus
        # print("PQ0", pinbus)
        self.netbus.attach_component(self.comp, pinbus)

        self.netbus.sort_nets()
        self.netbus.create_as_bus(file)

    def create_mux(self):
        ''' Create a bus-mux '''
        self.comp = Component(
            self.partref,
            "BMX_" + self.netbus.cname,
            self.muxtype,
        )
        self.scm.add_component(self.comp)
        self.comp.name = self.partref
        # print("COMP", self.comp.name)
        self.comp.part = self.part
        self.comp.part.assign(self.comp, self.cpu.part_lib)
        for n, net in enumerate(self.netbus.nets):
            Node(
                net,
                self.comp,
                self.pins["Q%d" % n],
            )
            net.sc_type = "bool"

class NetBus():

    ''' ... '''


    def __init__(self, sig, *nets):
        self.sig = sig
        self.nodes = {}
        self.components = {}
        self.nets = None
        self.cname = None
        self.ctype = None
        self.best = []

        for net in nets:
            self.add_net(net)

    def __repr__(self):
        return "<MBUS %d×%d>" % (len(self.nets), len(self.nodes))

    def __len__(self):
        return len(self.nets)

    def __lt__(self, other):
        return self.cname < other.cname

    def add_net(self, net):
        ''' Add another net '''
        if not self.nets:
            self.nets = [net]
            for node in net.nnodes:
                key = (node.component, node.pin.pinbus)
                self.components[key] = [node]
                self.nodes[key] = {node.net: node}
        else:
            self.nets.append(net)
            for node in net.nnodes:
                key = (node.component, node.pin.pinbus)
                self.components[key].append(node)
                self.nodes[key][node.net] = node

    def attach_component(self, comp, pinbus):
        ''' Attach yet a component to this bus '''
        assert pinbus is not None
        key = (comp, pinbus)
        self.components[key] = []
        self.nodes[key] = {}
        for node in comp.nodes.values():
            if node.pin.pinbus == pinbus:
                self.components[key].append(node)
                self.nodes[key][node.net] = node

    def detach_component(self, comp, pinbus):
        ''' Deattach a component to this bus '''
        key = (comp, pinbus)
        assert key in self.components
        del self.components[key]
        del self.nodes[key]

    def the_only_one_driver(self):
        ''' Only has one driver '''
        comp = None
        for node in self.nets[0].nnodes:
            if node.pin.type.output:
                if comp:
                    return None
                comp = node.component
        return comp

    def sort_nets(self):
        ''' Sort the nets into (pressumed) bus-order '''
        pivot_node = self.nets[0].nnodes[0]
        pivot_key = (pivot_node.component, pivot_node.pin.pinbus)
        nodes = self.components[pivot_key]
        nodes.sort(key=lambda x: x.pin.sortkey)
        self.nets = list(x.net for x in nodes)
        for idx, net in enumerate(self.nets):
            for node in net.nnodes:
                node.pin.netbusidx = idx

    def invalid(self, file):
        ''' Detect mixed signal types and non-busable components '''
        sc_type = set(x.sc_type for x in self.nets)
        if len(sc_type) > 1:
            file.write("\nMixed bus " + str(sc_type) + "\n")
            self.table(file, "\t")
            return True
        for comp, _pinbus in self.components:
            if not comp.part.busable:
                file.write("\nComponent not busable ")
                file.write(comp.part.name + " " + comp.scm.scm_lname + " " + comp.name + "\n")
                self.table(file, "\t")
                return True
        return False

    def is_valid_bus(self, nets):
        ''' Test if nets constitute a proper bus '''
        for key in self.components:
            sks = list(self.nodes[key][net].pin.sortkey for net in nets)
            spread = 1 + sks[-1][-1] - sks[0][-1]
            if sks != sorted(sks) or spread != len(nets):
                return False
        return True

    def unordered(self):
        ''' Find the largest bus, if any, in self.nets '''
        best = (0, 0, [])
        i = 0
        anets = list(self.nets)
        while len(anets) >= MIN_BUS_WIDTH:
            tnets = list(anets)
            j = 1
            while len(tnets) >= MIN_BUS_WIDTH:
                if not self.is_valid_bus(tnets):
                    tnets.pop(-1)
                    continue
                if len(tnets) > best[0]:
                    best = (len(tnets), i, tnets)
                j = len(tnets)
                break
            anets = anets[j:]
        if best[2]:
            self.best = best[2]
        return len(best[2]) != len(self.nets)

    def table(self, file, pfx=""):
        ''' render in table format '''
        file.write(pfx + "BUS")
        file.write(" %d×%d" % (len(self.nets), len(self.nodes)))
        file.write(" \t" + str(self.cname) + " " + str(self.ctype) + "\n")
        file.write(pfx + "   [" + self.sig + "]\n")

        i = [""]
        for component, _pinbus in self.components:
            i.append(component.scm.scm_lname)
        file.write(pfx + "\t".join(i) + "\n")

        i = [""]
        for component, _pinbus in self.components:
            i.append(component.name)
        file.write(pfx + "\t".join(i) + "\n")

        i = [""]
        for node in self.nets[0].nnodes:
            i.append(node.pin.type.name)
        file.write(pfx + "\t".join(i) + "\n")

        for net in sorted(self.nets):
            i = [""]
            for node in net.nnodes:
                i.append(node.pin.name)
            i.append(net.name)
            file.write(pfx + "\t".join(i) + "\n")

    def decide_cname(self):
        ''' Find name '''
        i = str(util.sortkey(self.nets[-1].cname)[-1]).rsplit("->", maxsplit=1)[-1]
        self.cname = self.nets[0].cname + "_to_" + i

    def sc_signals(self, net):
        ''' enumerate our SystemC signals '''
        if net != self.nets[0]:
            return
        lname = self.cname.split("->")[-1].split(".")[-1]
        if net.sc_type != "bool":
            yield ScSignal(
                lname,
                "sc_signal_rv <%d>" % (len(self.nets)),
                '"' + "z" * len(self.nets) + '"'
            )
        else:
            yield ScSignal(
                lname,
                "sc_signal <" + self.ctype + ">",
                '0x%xULL' % ((1 << len(self.nets)) - 1)
            )

    def instantiate(self, file):
        ''' Make this bus real, if possible '''
        assert len(self.nets) >= MIN_BUS_WIDTH

        if self.invalid(file):
            return

        self.sort_nets()
        if not self.unordered():
            self.create(file)
            return

        if len(self.best) < MIN_BUS_WIDTH:
            file.write("\nResidual:\t")
            self.table(file)
            return

        target = set(self.best)
        rest = set(self.nets) - target
        target = list(target)
        rest = list(rest)

        newbus = NetBus(self.sig, *target)
        newbus.create(file)

        maybebus = NetBus(self.sig, *rest)
        if len(maybebus.nets) < MIN_BUS_WIDTH:
            file.write("\nResidual:\t")
            maybebus.table(file)
        else:
            maybebus.instantiate(file)

    def create_as_bus(self, file):
        ''' Create as a bus '''
        for net in self.nets:
            net.netbus = self
            for node in net.nnodes:
                node.netbus = self
        net = self.nets[0]
        if net.sc_type != "bool":
            self.ctype = "_rv <%d>" % len(self.nets)
        elif len(self.nets) <= 16:
            self.ctype = "uint16_t"
        elif len(self.nets) <= 32:
            self.ctype = "uint32_t"
        else:
            self.ctype = "uint64_t"
        self.decide_cname()
        if file:
            file.write("\nAccepted:\t")
            self.table(file)

    def create(self, file):
        ''' create network '''
        self.sort_nets()
        self.decide_cname()
        pintypes = set()
        for net in self.nets:
            for node in net.nnodes:
                pintypes.add(node.pin.type.name)

        if "zio" in pintypes or "zo" not in pintypes:
            self.create_as_bus(file)
            return

        good = True
        width = 0
        for node in self.nets[0].nnodes:
            if node.pin.type.name == "zo":
                width += 1
                specoe = node.pin.pinbus.name + "OE"
                if specoe in node.component:
                    node.pin.pinbus.oe = specoe
                    print("PBOE", node.pin, specoe)
                elif "OE" in node.component:
                    node.pin.pinbus.oe = "OE"
                else:
                    file.write("MUX has no OE or " + specoe + " in " + str(node.component) + "\n")
                    good = False
            elif node.pin.type.name != "in":
                file.write("MUX has pintype " + node.pin.type.name + "\n")
                good = False

        if not good or width == 1 or not USE_MUXBUS:
            self.create_as_bus(file)
        else:
            MuxBus(self, width, file)

class PassNetConfig():

    ''' Pass: Configure the `net` '''

    def __init__(self, cpu):
        self.cpu = cpu
        self.netbusses = {}

        cpu.recurse(self.home_nets)
        cpu.recurse(self.ponder_bool)
        self.ponder_bool(cpu.plane)

        cpu.recurse(self.find_cnames)
        self.find_cnames(cpu.plane)

        with open("_bus_%s.txt" % self.cpu.branch, "w") as file:
            self.bus_candidates(file)

        cpu.recurse(self.find_cnames)
        self.find_cnames(cpu.plane)

    def home_nets(self, scm):
        ''' Move nets to their natural home '''
        for net in scm.iter_nets():
            assert not net.on_plane
            if not net.nnodes:
                net.remove()
                continue
            net.move_home()

    def find_cnames(self, scm):
        cnames = set()
        for net in scm.iter_nets():
            net.find_cname()
            assert net.cname not in cnames
            cnames.add(net.cname)

    def ponder_bool(self, scm):
        ''' Determine if network needs hiz state '''
        for net in scm.iter_nets():
            assert len(net)
            hizs = 0
            outputs = 0
            roles = set()
            for node in net.iter_nodes():
                roles.add(node.pin.type)
                if node.pin.type.hiz:
                    hizs += 1
                if node.pin.type.output:
                    outputs += 1

            if outputs == 0 and net.name not in ("PD", "PU"):
                print("Undriven", net, len(net), roles)
                for i in net.nnodes:
                    print("  udn ", i)

            if hizs == 0 and outputs <= 1:
                net.sc_type = "bool"

    def chew_nets(self, scm):

        for net in scm.iter_nets():
            if len(net.nnodes) < 2:
                continue

            if None in (x.pin.pinbus for x in net.nnodes):
                continue

            uniq_comps = set((x.component, x.pin.pinbus) for x in net.nnodes)
            if len(uniq_comps) != len(net.nnodes):
                # Signals which connect multiple times to a single component
                # are disqualified, because we cannot (easily) figure out
                # which of the multiple connections to assign where in the bus.
                #print("Mult", net)
                #print("  NN", len(net.nnodes))
                #print("  UC", uniq_comps)
                continue


            sig = " ".join(
                sorted(
                    ":".join((x.component.scm.scm_lname, x.component.ref, x.pin.pinbus.name))
                    for x in net.nnodes
                )
            )
            i = self.netbusses.get(sig)
            if i:
                i.add_net(net)
            else:
                self.netbusses[sig] = NetBus(sig, net)

    def bus_candidates(self, file):
        ''' Find networks which are candidates for bus-membership '''

        self.cpu.recurse(self.chew_nets)
        self.chew_nets(self.cpu.plane)

        for maybebus in self.netbusses.values():
            if len(maybebus.nets) >= MIN_BUS_WIDTH:
                file.write("\n===============\n")
                maybebus.instantiate(file)

        for board in self.cpu.boards:
            for comp in board.iter_components():
                comp.optimize()

        netbusses = set([None])
        for net in self.cpu.nets.values():
            netbus = net.netbus
            if netbus in netbusses:
                continue
            netbusses.add(netbus)
            if netbus.ctype[0] != "_":
                continue
            comp =  netbus.the_only_one_driver()
            if not comp:
                continue
            # print("*****", net, net.netbus, comp)
            for net2 in netbus.nets:
                net2.sc_type = "bool"
            netbus.create_as_bus(None)

        netbusses.remove(None)

        file.write("\n")
        file.write("FINAL NETBUSSES\n")
        file.write("===============\n")
        for netbus in sorted(netbusses):
            file.write("\n")
            netbus.table(file)
