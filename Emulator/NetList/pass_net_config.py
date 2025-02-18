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
from pin import Pin, PinTypeOut
from scmod import ScSignal

class PassNetConfig():

    ''' Pass: Configure the `net` '''

    def __init__(self, cpu):
        self.cpu = cpu
        self.netbusses = {}

        cpu.recurse(self.ponder_bool)

        cpu.recurse(self.find_cnames)

    def find_cnames(self, scm):
        cnames = set()
        for net in scm.iter_nets():
            net.find_cname()
            if net.cname in cnames:
                print("Dup net.cname", self, net.cname, cnames)
            assert net.cname not in cnames
            cnames.add(net.cname)

    def ponder_bool(self, scm):
        ''' Determine if network needs hiz state '''
        for net in scm.iter_nets():
            if not len(net):
                print("Empty net ?", net)
            assert len(net)
            if len(net) == 1:
                for node in net.iter_nodes():
                    if not node.pin.type.input and node.pin.type.output:
                        #print("N2", net, node)
                        net.sc_type = "bool"
                        node.pin.type = PinTypeOut
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
