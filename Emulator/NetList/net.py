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
   Turn kicad netlist files into SystemC source code
   =================================================
'''

import util
import scmod

class Net():
    ''' A `net` from the netlist file '''
    def __init__(self, name):
        self.scm = None
        self.name = name
        self.nnodes = []
        self.netbus = None
        self.is_supply = False
        self.on_plane = None
        self.sc_type = "sc_logic"
        self.default = True
        self.sortkey = util.sortkey(self.name)
        self.cname = None
        self.bare_cname = None

    def remove(self):
        ''' ... '''
        self.scm.del_net(self)

    def add_node(self, node):
        ''' ... '''
        assert node not in self.nnodes
        self.nnodes.append(node)

    def del_node(self, node):
        ''' ... '''
        assert node in self.nnodes
        self.nnodes.remove(node)
        if self.netbus:
            self.netbus.remove_node(node)

    def adopt(self, other):
        ''' Adopt another network '''
        for node in list(other.iter_nodes()):
            node.remove()
            node.net = self
            node.insert()
        other.remove()

    def iter_nodes(self):
        ''' ... '''
        yield from self.nnodes

    def __repr__(self):
        return "_".join(("Net", self.name))

    def __lt__(self, other):
        try:
            return self.sortkey < other.sortkey
        except:
            pass
        return str(self.sortkey) < str(other.sortkey)

    def __len__(self):
        return len(self.nnodes)

    def is_pd(self):
        ''' Is this network a constant low value '''
        return self.name == "PD"

    def is_pu(self):
        ''' Is this network a constant high value '''
        return self.name == "PU"

    def is_const(self):
        ''' Value will not change '''
        return self.name in ("PD", "PU") or len(self) == 1

    def sc_signals(self):
        ''' enumerate our SystemC signals '''
        if self.netbus:
            yield from self.netbus.sc_signals(self)
        else:
            retval = [self.bare_cname]
            if self.sc_type == "bool":
                retval.append("sc_core::sc_signal <bool>")
            else:
                retval.append("sc_core::sc_signal_resolved")
            if self.sc_type == "bool" and self.default:
                retval.append("true")
            elif self.sc_type == "bool":
                retval.append("false")
            elif self.default:
                retval.append("sc_dt::sc_logic_1")
            else:
                retval.append("sc_dt::sc_logic_1")
            yield scmod.ScSignal(*retval)

    def find_cname(self):
        cname = self.name
        if cname[0].isdigit():
            cname = "z" + cname
        if len(self.nnodes) == 1 and "unconnected" in cname:
            node = self.nnodes[0]
            cname = "u_" + node.component.name + "_" + node.pin.ident
        for i, j in (
            ("Net-", ""),
            ("/Page ", "p"),
            (">", "gt"),
            ("<", "lt"),
            ("=", "eq"),
            ("~", "not"),
            ("unconnected-", ""),
            ("(", ""),
            (")", ""),
            ("-", "_"),
            (".", "_"),
            ("/", "_"),
        ):
            cname = cname.replace(i, j)
        self.bare_cname = cname
        self.cname = self.scm.scm_cname_pfx + cname

    def move_home(self):
        ''' Move network to it's natural home '''

        scms = set()
        pscms = set()
        for node in self.iter_nodes():
            scms.add(node.component.scm)
            pscms.add(node.component.scm.scm_parent)
        scms = list(sorted(scms))
        if len(scms) == 1:
            if scms[0] != self.scm:
                self.remove()
                scms[0].add_net(self)
            return
        scms = list(sorted(pscms))
        if len(scms) == 1:
            if scms[0] != self.scm:
                self.remove()
                scms[0].add_net(self)
            return
        dscm = scms[0].cpu.plane
        if dscm != self.scm:
            self.remove()
            dscm.add_net(self)
