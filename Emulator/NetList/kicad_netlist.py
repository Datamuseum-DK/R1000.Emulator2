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
S-Expressions
'''

from sexp import SExp
from part import LibPartSexp
from board import Board
from scmod import SystemCModule
from component import Component
from net import Net
from node import Node
from pin import Pin

class KiCadNetList():
    ''' A NetList from KiCad '''

    def __init__(self, filename):
        self.sexp = SExp(None)
        with open(filename, encoding="utf8") as file:
            self.sexp.parse(file.read())
        self.comps = {}
        self.board = None

    def build(self, cpu):
        ''' Build everything '''

        self.build_parts(cpu)

        bname = self.find_board_name()
        self.board = Board(cpu, bname)
        cpu.add_board(self.board)
        # self.board.add_ctor_arg("struct planes", "planes", is_ptr=True)

        self.build_sheets(cpu)
        self.build_components(cpu)
        self.build_nets()

    def build_parts(self, cpu):
        ''' Build parts '''

        for sexp in self.sexp.find("libparts.libpart"):
            part = LibPartSexp(sexp)
            cpu.add_part(part.name, part)

    def build_sheets(self, cpu):
        ''' Build sheets '''

        for sexp in self.sexp.find("design.sheet"):
            name = sexp.find_first("name")[0].name
            self.board.add_sheet(self.path_to_sheet(name))

    def build_components(self, cpu):
        ''' Build sheets '''

        for sexp in self.sexp.find("components.comp"):
            path = sexp.find_first("sheetpath.names")[0].name
            sheet_name = self.path_to_sheet(path)
            sheet = self.board.get_child(sheet_name)
            comp = ComponentSexp(sexp)
            sheet.add_component(comp)
            self.comps[comp.ref] = comp
            if comp.location[0] == 'z':
                cpu.add_z_code(comp, comp.location)

    def build_nets(self):
        ''' Build nets '''

        for sexp in self.sexp.find("nets.net"):
            path = sexp[1][0].name
            sheet_name = self.path_to_sheet(path)
            if sheet_name is None:
                parent = self.board
            else:
                parent = self.board.get_child(sheet_name)
            if "/Page " in path:
                path = path.replace("/Page ", "p")
                path = path.replace("/", "_")
            name = path.split('/')[-1]
            net = Net(name)
            parent.add_net(net)
            self.add_nodes_to_net(net, sexp)

    def add_nodes_to_net(self, net, net_sexp):
        ''' Add the nodes to a network '''
        for sexp in net_sexp.find("node"):
            pinfunc = sexp.find_first("pinfunction")
            if pinfunc:
                pinname = pinfunc[0].name
            else:
                pinname = "W"
            comp = self.comps[sexp[0][0].name]
            role = sexp.find_first("pintype")[0].name
            pin = Pin(
                pinident=sexp[1][0].name,
                pinname=pinname,
                pinrole=role,
            )
            Node(net, comp, pin)

    def find_board_name(self):
        ''' We dont trust the filename '''
        title = self.sexp.find_first('design.sheet.title_block.title')
        i = title[0].name.split()
        assert i[1] == "Main"
        assert i[0].upper() == i[0]
        return i[0]

    def path_to_sheet(self, text):
        ''' Convert a sheets name to (our) sheet number '''
        if text == "/":
            return self.board.scm_lname + "_00"
        j = text.split('/')
        if len(j) == 1:
            return None
        assert j.pop(0) == ''
        assert j[0][:5] == "Page "
        return self.board.scm_lname + "_%02d" % int(j[0][5:], 10)

class ComponentSexp(Component):

    ''' Create a `component` from netlist-sexp '''

    def __init__(self, sexp):
        i = sexp.find_first("libsource.part")
        partname = i[0].name

        ref = sexp[0][0].name
        #if ref[:2] not in ("GB", "GF", "PU", "PD"):
        #    ref = pfx + ref

        super().__init__(
            compref = ref,
            compvalue = sexp.find_first("value")[0].name,
            comppart = partname,
        )

        for i in sexp.find("property"):
            if i[0][0].name == 'Location':
                self.location = i[1][0].name
            elif i[0][0].name == 'Name':
                self.name = i[1][0].name
