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
   A SystemC Module
   ================
'''

import os

import srcfile
import component
import net
import util

class CtorArg():
    ''' An argument for the SCM constructor function '''

    def __init__(self, ctype, dstname, srcname=None, is_ptr=False):
        self.ctype = ctype
        self.dstname = dstname
        if srcname is None:
            srcname = dstname
        self.srcname = srcname
        self.is_ptr = is_ptr

    def protoform(self):
        ''' proto type form '''
        txt = self.ctype + " "
        if self.is_ptr:
            txt += "*"
        return txt + self.dstname

class ScSignal():
    ''' A SystemC signal '''
    def __init__(self, name, sctype, defval):
        self.name = name
        self.sctype = sctype
        self.defval = defval
        self.sortkey = util.sortkey(name)

    def __lt__(self, other):
        return self.sortkey < other.sortkey

    def decl(self):
        ''' declaration '''
        txt = self.sctype + "\t"
        while len(txt.expandtabs()) < 24:
            txt += "\t"
        txt += self.name + ";"
        return txt

    def init(self):
        ''' initialization '''
        return self.name + '("' + self.name + '", ' + self.defval + ')'

class SystemCModule():
    ''' A SystemC source module '''
    def __init__(self, filename, makefile=None):
        self.scm_filename = filename
        self.scm_makefile = makefile
        self.scm_parent = None
        self.scm_basename = os.path.basename(filename)
        self.scm_lname = self.scm_basename.lower()
        self.scm_uname = self.scm_basename.upper()
        self.sf_cc = srcfile.SrcFile(filename + ".cc")
        self.sf_hh = srcfile.SrcFile(filename + ".hh")
        self.sf_pub = srcfile.SrcFile(filename + "_pub.hh")
        self.add_subst("«mmm»", self.scm_uname)
        self.add_subst("«lll»", self.scm_lname)
        self.scm_ctor_args = []
        self.scm_children = {}
        self.scm_signals = {}
        self.scm_members = []
        self.scm_components = {}
        self.scm_nets = {}
        self.scm_cname_pfx = ""
        self.scm_unique = 0

        self.sf_cc.write("#include <systemc.h>\n")
        self.sf_cc.include("Chassis/r1000sc.h")
        self.sf_cc.include("Infra/context.h")
        self.sf_cc.write("\n")
        self.sf_cc.include(self.sf_hh)

    def recurse(self, call_this, *args, **kwargs):
        ''' Recursively all a function on the entire tree '''
        call_this(self, *args, **kwargs)
        for child in sorted(self.scm_children.values()):
            child.recurse(call_this, *args, **kwargs)

    def __repr__(self):
        return "<SCM " + self.scm_basename + ">"

    def __lt__(self, other):
        return self.scm_filename < other.scm_filename

    def include(self, incl):
        ''' add include file '''
        self.sf_hh.include(incl)

    def add_member(self, cstuff):
        ''' add member items in raw C-form '''
        self.scm_members.append(cstuff)

    def add_component(self, comp):
        ''' add component '''
        assert isinstance(comp, component.Component)
        assert comp.ref not in self.scm_components
        self.scm_components[comp.ref] = comp
        comp.scm = self

    def del_component(self, comp):
        ''' delete component '''
        assert isinstance(comp, component.Component)
        assert comp.ref in self.scm_components
        del self.scm_components[comp.ref]
        comp.scm = None

    def iter_components(self):
        ''' components in sorted order '''
        yield from sorted(self.scm_components.values())

    def add_net(self, newnet):
        ''' add net '''
        assert isinstance(newnet, net.Net)
        if newnet.name in self.scm_nets:
            newnet.name += "_%d" % self.scm_unique
            self.scm_unique += 1
        assert newnet.name not in self.scm_nets, (self, newnet)
        self.scm_nets[newnet.name] = newnet
        newnet.scm = self

    def del_net(self, delnet):
        ''' delete net '''
        assert isinstance(delnet, net.Net)
        assert delnet.name in self.scm_nets
        del self.scm_nets[delnet.name]
        delnet.scm = None

    def iter_nets(self):
        ''' nets in sorted order '''
        yield from list(sorted(self.scm_nets.values()))

    def add_child(self, scm):
        ''' add a child '''
        assert isinstance(scm, SystemCModule)
        name = scm.scm_lname
        assert name not in self.scm_children
        scm.scm_parent = self
        self.scm_children[name] = scm
        self.sf_hh.include(scm.sf_pub)

    def get_child(self, name):
        ''' Get a child by name '''
        return self.scm_children[name]

    def add_signal(self, sig):
        ''' Add a signal '''
        assert isinstance(sig, ScSignal)
        self.scm_signals[sig.name] = sig

    def iter_signals(self):
        ''' Iterate all signals '''
        yield from sorted(self.scm_signals.values())

    def add_ctor_arg(self, *args, **kwargs):
        ''' Add a constructor argument '''
        self.scm_ctor_args.append(CtorArg(*args, **kwargs))

    def commit(self):
        ''' ... '''
        self.sf_cc.commit()
        self.sf_hh.commit()
        self.sf_pub.commit()
        if self.scm_makefile:
            self.makefile_entry(self.scm_makefile)

    def add_subst(self, find, replace):
        ''' Add substituation patterns '''
        for file in (self.sf_cc, self.sf_hh, self.sf_pub):
            file.add_subst(find, replace)

    def makefile_entry(self, makefile):
        ''' ... '''
        bname = self.scm_filename.split("/")[-1]
        hdr = "# " + bname + "\n"
        txt = ""
        obj = "${OBJDIR}/" + bname + ".o"
        txt += "OBJS += " + obj + "\n"
        txt += obj + ":"
        for incl in sorted(self.sf_cc):
            txt += " \\\n    " + incl
        txt += "\n"
        txt += "\t@echo Compiling " + os.path.basename(self.sf_cc.filename) + "\n"
        txt += "\t@${SC_CC} -o " + obj + " " + self.sf_cc.filename + "\n"
        makefile.add_stanza(hdr, txt)

    def std_hh(self, pin_iterator):
        ''' Produce a stanard .sf_hh file '''
        self.sf_hh.fmt('''
		|#ifndef R1000_«mmm»
		|#define R1000_«mmm»
		|
		|struct scm_«lll»_state;
		|
		|SC_MODULE(SCM_«mmm»)
		|{
		|''')

        for i in pin_iterator:
            self.sf_hh.write("\t" + i + "\n")

        self.sf_hh.fmt('''
		|
		|	SC_HAS_PROCESS(SCM_«mmm»);
		|
		|	SCM_«mmm»(sc_module_name nm, const char *arg);
		|
		|	private:
		|	struct scm_«lll»_state *state;
		|	void doit(void);
		|};
		|
		|#endif /* R1000_«mmm» */
		|''')

    def std_cc(self, extra=None, state=None, init=None, sensitive=None, doit=None):
        ''' Produce a standard .sf_cc file '''

        if extra:
            self.sf_cc.write("\n")
            extra(self.sf_cc)

        self.sf_cc.fmt('''
		|
		|struct scm_«lll»_state {
		|	struct ctx ctx;
		|''')

        if state:
            state(self.sf_cc)

        self.sf_cc.fmt('''
		|};
		|
		|SCM_«mmm» ::
		|    SCM_«mmm»(sc_module_name nm, const char *arg)
		|	: sc_module(nm)
		|{
		|	state = (struct scm_«lll»_state *)
		|	    CTX_Get("«lll»", this->name(), sizeof *state);
		|	should_i_trace(this->name(), &state->ctx.do_trace);
		|''')

        if init:
            self.sf_cc.write("\n")
            init(self.sf_cc)

        self.sf_cc.fmt('''
		|
		|	SC_METHOD(doit);
		|''')

        i = []
        for j in sensitive():
            if "BUS" in j and "SENSITIVE" not in j:
                j += "_SENSITIVE()"
            i.append(j)
        if i:
            self.sf_cc.write("\tsensitive\n\t    << ")
            self.sf_cc.write("\n\t    << ".join(i) + ";\n")

        self.sf_cc.fmt('''
		|}
		|
		|void
		|SCM_«mmm» :: doit(void)
		|{
		|	state->ctx.activations++;
		|
		|''')

        doit(self.sf_cc)

        self.sf_cc.write("}\n")

    def instantiate(self, name):
        ''' How to instantiate ourselves '''
        txt = name + " = "
        txt += "make_" + self.scm_lname + "("
        txt += '"' + name + '"'
        for arg in self.scm_ctor_args:
            txt += ", " + arg.srcname
        txt += ");"
        return txt

    def create(self):
        ''' How to create ourselves '''
        txt = self.scm_lname + "("
        txt += "sc_module_name name"
        for arg in self.scm_ctor_args:
            txt += ", " + arg.protoform()
        txt += ");"
        return txt

    def decl(self, name):
        ''' How to declare ourselves '''
        return "struct " + self.scm_lname + " *" + name + ";"

    def emit_pub_hh(self):
        ''' Produce the public .hh file '''
        for arg in self.scm_ctor_args:
            self.sf_pub.fmt(arg.ctype + ";\n")

        self.sf_pub.write("\n")

        self.sf_pub.fmt("struct «lll» *make_«lll»(\n    sc_module_name name")
        for arg in self.scm_ctor_args:
            self.sf_pub.fmt(",\n    " + arg.protoform())
        self.sf_pub.write("\n);\n")

    def emit_hh(self):
        ''' Produce the .hh file '''

        for net in self.iter_nets():
            for sig in net.sc_signals():
                self.add_signal(sig)

        self.sf_hh.include(self.sf_pub)
        incls = set()
        for comp in self.iter_components():
            for incl in comp.part.yield_includes(comp):
                if incl not in incls:
                    self.include(incl)
                incls.add(incl)
        self.sf_hh.write('\n')
        self.sf_hh.fmt('SC_MODULE(«lll»)\n')
        self.sf_hh.fmt('{\n')
        for mbr in self.scm_members:
            self.sf_hh.write('\t' + mbr + "\n")
        for sig in self.iter_signals():
            self.sf_hh.fmt('\t' + sig.decl() + "\n")
        for comp in self.iter_components():
            comp.part.instance(self.sf_hh, comp)
        for name, child in self.scm_children.items():
            self.sf_hh.fmt('\t' + child.decl(name) + "\n")
        self.sf_hh.write('\n')
        self.sf_hh.fmt('\t' + self.create() + "\n")
        self.sf_hh.fmt('};\n')

    def emit_cc(self):
        ''' Produce the .cc file '''
        self.sf_cc.include(self.sf_pub)
        self.sf_cc.write("\n")
        self.sf_cc.fmt("struct «lll» *make_«lll»(\n    sc_module_name name")
        for arg in self.scm_ctor_args:
            self.sf_cc.fmt(",\n    " + arg.protoform())
        self.sf_cc.write("\n)\n")
        self.sf_cc.write("{\n")
        self.sf_cc.fmt('\treturn new «lll»(name')
        for arg in self.scm_ctor_args:
            self.sf_cc.fmt(", " + arg.dstname)
        self.sf_cc.write(');\n}\n\n')

        self.sf_cc.fmt('''«lll» :: «lll»(\n''')
        self.sf_cc.fmt('''    sc_module_name name''')
        for arg in self.scm_ctor_args:
            self.sf_cc.fmt(',\n    ' + arg.protoform())
        self.sf_cc.write('\n) :\n')
        self.sf_cc.fmt('\tsc_module(name)')
        for sig in self.iter_signals():
            self.sf_cc.write(",\n\t" + sig.init())
        for comp in self.iter_components():
            comp.part.initialize(self.sf_cc, comp)
        self.sf_cc.write('\n{\n')
        for name, child in self.scm_children.items():
            self.sf_cc.fmt("\t" + child.instantiate(name) + "\n")
        for comp in self.iter_components():
            comp.part.hookup_comp(self.sf_cc, comp)
        self.sf_cc.fmt('''}\n''')

    def produce(self):
        ''' produce the source files '''
        self.emit_pub_hh()
        self.emit_hh()
        self.emit_cc()
        self.commit()
        for child in self.scm_children.values():
            child.produce()
