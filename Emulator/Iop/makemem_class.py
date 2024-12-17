'''
   Classes to produce memory-space .h and .c files
   -----------------------------------------------
'''

class Range():
    ''' One subrange of memory space '''
    def __init__(
        self,
        name,
        lo,
        hi,
        mask=None,
        shift=0,
        bidir=True,
        pre_read=None,
        post_write=None,
        read_only=False,
        write_only=False,
        sc_read=False,
        sc_write=False,
    ):
        self.name = name
        self.lo = lo
        self.hi = hi
        self.mask = mask
        self.shift = shift
        self.bidir = bidir
        self.pre_read = pre_read
        self.post_write = post_write
        self.read_only = read_only
        self.write_only = write_only
        self.sc_read = sc_read
        self.sc_write = sc_write

        if not (1 + self.hi) & self.hi and self.hi < self.lo:
            self.hi = self.lo + self.hi + 1

        assert self.lo <= self.hi

        if self.bidir:
            self.rd_space = name + "_space"
            self.wr_space = self.rd_space
        else:
            self.rd_space = name + "_rd_space"
            self.wr_space = name + "_wr_space"

        self.pegs = name + "_pegs"
        self.struct_name = "mem_desc_" + name

        if self.mask:
            assert not self.mask & (self.mask + 1) # Must be (power of two - 1)
            assert not self.mask & self.lo # General sanity
            assert self.mask == (self.mask & (self.hi-1)) # General sanity
            self.effective_address = "((address-0x%x) & 0x%x)" % (self.lo, self.mask)
            self.length = self.mask + 1
        else:
            if self.lo:
                self.effective_address = "(address-0x%x)" % self.lo
            else:
                self.effective_address = "address"
            self.length = self.hi - self.lo
            if self.shift:
                self.length >>= self.shift
                self.effective_address = "((" + self.effective_address + ")>>0x%x)" % self.shift

        if self.pre_read is True:
            self.pre_read = self.name + "_pre_read"

    def cond(self, width, fo):
        ''' emit our conditional '''
        fo.write("if (")
        i = []
        if self.lo:
            i.append("0x%x <= address" % self.lo)
        j = self.hi + 1 - width
        if j < 1<<32:
            i.append("address < 0x%x" % j)
        fo.write(" && ".join(i) + ") {\n")

    def produce_h(self, fo):
        ''' Emit .h file stuff '''

        fo.write("extern struct memdesc %s;\n" % self.struct_name)
        fo.write("extern uint8_t *%s;\n" % self.rd_space)
        if not self.bidir:
            fo.write("extern uint8_t %s[0x%x];\n" % (self.wr_space, self.length))
        if self.pre_read:
            fo.write("mem_pre_read %s_pre_read;\n" % self.name)
        if self.post_write:
            fo.write("mem_post_write %s_post_write;\n" % self.name)

    def produce_data(self, fo):
        ''' Produce the data parts of .c '''

        peglength = (self.length + 1) // 2
        fo.write("uint8_t *%s;\n" % self.rd_space)
        if not self.bidir:
            fo.write("uint8_t %s[0x%x];\n" % (self.wr_space, self.length))
        fo.write("static uint8_t %s[0x%x];\n" % (self.pegs, peglength))
        fo.write("struct memdesc %s = {\n" % self.struct_name)
        fo.write('\t.name = "%s",\n' % self.name)
        fo.write('\t.lo = 0x%x,\n' % self.lo)
        fo.write('\t.hi = 0x%x,\n' % self.hi)
        if self.mask:
            fo.write('\t.mask = 0x%x,\n' % self.mask)
        else:
            fo.write('\t.mask = 0xffffffff,\n')

        fo.write('\t.pegs = %s,\n' % (self.pegs))
        fo.write('\t.space_length = 0x%x,\n' % self.length)
        fo.write('\t.pegs_length = 0x%x,\n' % peglength)
        fo.write('};\n')

    def produce_init(self, fo):
        fo.write('\t%s = CTX_GetRaw("IOP.%s", %d);\n' % (self.rd_space, self.rd_space, self.length))
        fo.write("\tassert(%s != NULL);\n" % self.rd_space);

    def peg_check(self, fo, what, val, width):
        ''' call the peg_check function '''
        fo.write("\t\tpeg = " + self.pegs + "[" + self.effective_address + ">>1];\n")
        fo.write('\t\tif (peg & PEG_CHECK) {\n')
        fo.write('\t\t\tmem_peg_check(')
        fo.write("mem_op_" + what)
        fo.write(', &%s, address, %s, %d, peg);\n' % (self.struct_name, val, width))
        fo.write('\t\t}\n')

    def produce_read_call(self, what, width, fo):
        ''' Produce a read call function '''

        self.cond(width, fo)

        if self.write_only:
            if 'debug' in what:
                fo.write('\t\tmem_error_cause = "%s is write_only";\n' % self.name)
            else:
                fo.write('\t\t/* %s is write_only */\n' % self.name)
            fo.write("\t}")
            return

        if self.pre_read:
            j = "\t\t" + self.name + "_pre_read("
            if 'debug' in what:
                j += "1, "
            else:
                j += "0, "
            if self.pre_read is 1:
                fo.write(j + self.rd_space + ", 1," + self.effective_address + ");\n")
                for i in range(1, width):
                    fo.write(j + self.rd_space + ", 1," + self.effective_address + "+ %d);\n" % i)
            else:
                fo.write(j + self.rd_space + ", %d, " % width + self.effective_address + ");\n")

        fo.write("\t\tvalue = ")
        if self.sc_read:
            fo.write("ioc_bus_xact_schedule(5, address, 0, %d, 0);\n" % width)
        elif width == 1:
            fo.write(self.rd_space + "[" + self.effective_address + "];\n")
        elif width == 2:
            fo.write("vbe16dec(" + self.rd_space + " + " + self.effective_address + ");\n")
        elif width == 4:
            fo.write("vbe32dec(" + self.rd_space + " + " + self.effective_address + ");\n")
        else:
            assert False, "Bogo Width"

        if not 'debug' in what:
            self.peg_check(fo, what, "value", width)

        fo.write("\t\treturn (value);\n")
        fo.write("\t}")

    def produce_write_call(self, what, width, fo):
        ''' Produce a write call function '''

        self.cond(width, fo)

        if self.read_only:
            if 'debug' in what:
                fo.write('\t\tmem_error_cause = "%s is read_only";\n' % self.name)
            else:
                fo.write('\t\t/* %s is read_only */\n' % self.name)
            fo.write("\t}")
            return

        if not 'debug' in what:
            self.peg_check(fo, what, "value", width)

        if width == 1:
            fo.write("\t\t" + self.wr_space + "[" + self.effective_address + "] = value;\n")
        elif width == 2:
            fo.write("\t\tvbe16enc(" + self.wr_space + " + " + self.effective_address + ", value);\n")
        elif width == 4:
            fo.write("\t\tvbe32enc(" + self.wr_space + " + " + self.effective_address + ", value);\n")
        else:
            assert False, "Bogo Width"

        if self.sc_write:
            fo.write("\t\t(void)ioc_bus_xact_schedule(5, address, value, %d, 1);\n" % width)
        if self.post_write:
            j = "\t\t" + self.name + "_post_write" + "("
            if 'debug' in what:
                j += "1, "
            else:
                j += "0, "
            if self.post_write is 1:
                fo.write(j + self.wr_space + ", 1," + self.effective_address + ");\n")
                for i in range(1, width):
                    fo.write(j + self.wr_space + ", 1," + self.effective_address + "+ %d);\n" % i)
            else:
                fo.write(j + self.wr_space + ", %d," % width + self.effective_address + ");\n")

        elif self.post_write:
            if 'debug' in what:
                fo.write("\t\t" + self.post_write + "(1, ")
            else:
                fo.write("\t\t" + self.post_write + "(0, ")
            fo.write(self.wr_space + ", %d," % width + self.effective_address + ");\n")
        fo.write("\t}")

    def produce_find_peg(self, fo):
        ''' return the proper peg '''
        self.cond(1, fo)
        fo.write("\t\treturn(&" + self.pegs + "[" + self.effective_address + ">>1]);\n")
        fo.write("\t}")

class System():
    ''' A memory subsystem '''
    def __init__(
        self,
        name,
        lo,
        hi,
    ):
        self.name = name
        self.lo = lo
        self.hi = hi
        self.ranges = []

    def __iadd__(self, rng):
        assert isinstance(rng, Range)
        self.ranges.append(rng)
        return self

    def produce_c(self, filename):
        ''' Produce the *.c file '''
        fo = open(filename + ".c", "w")
        fo.write('#include <assert.h>\n')
        fo.write('#include <stdint.h>\n')
        fo.write('#include <stdio.h>\n')
        fo.write('\n')
        fo.write('#include "Infra/vend.h"\n')
        fo.write('#include "Infra/vqueue.h"\n')
        fo.write('#include "Infra/context.h"\n')
        fo.write('#include "Iop/iop_sc_68k20.hh"\n')
        fo.write('#include "Iop/memspace.h"\n')
        self.produce_data(fo)
        for i in (1, 2, 4):
            self.produce_read_x_bit("read", i, fo)
            self.produce_read_x_bit("debug_read", i, fo)
            self.produce_write_x_bit("write", i, fo)
            self.produce_write_x_bit("debug_write", i, fo)
        self.produce_peg_find(fo)

        fo.write('\n')
        fo.write('void\n')
        fo.write('Memory_Init(void)\n')
        fo.write('{\n')
        fo.write('\n')
        for i in self.ranges:
            i.produce_init(fo)
        fo.write('}\n')

    def produce_h(self, filename):
        ''' Produce the *.h file '''
        fo = open(filename + ".h", "w")
        for i in self.ranges:
            i.produce_h(fo)
        fo.write('void Memory_Init(void);\n')

    def produce_data(self, fo):
        ''' Produce the data part of *.c '''
        for i in self.ranges:
            fo.write("\n")
            i.produce_data(fo)
        fo.write("\n")
        fo.write("struct memdesc *memdesc[] = {\n")
        for i in self.ranges:
            fo.write("\t&%s,\n" % i.struct_name)
        fo.write("\tNULL\n")
        fo.write("};\n")
        fo.write("const unsigned n_memdesc = 0x%x;\n" % len(self.ranges))

    def produce_read_x_bit(self, what, width, fo):
        ''' Produce the read functions '''
        fo.write("\n")
        fo.write("unsigned\n")
        fo.write("m68k_%s_memory_%d(unsigned address)\n" % (what, width * 8))
        fo.write("{\n")
        if not 'debug' in what:
            fo.write("\tunsigned peg;\n\n")
        fo.write("\tunsigned value;\n\n")
        sep = "\t"
        for i in self.ranges:
            if i.lo < i.hi + 1 - width:
                fo.write(sep)
                sep = " else "
                i.produce_read_call(what, width, fo)

        fo.write(sep + "{\n")
        if 'debug' in what:
            fo.write('\t\tmem_error_cause = "Read %d from undefined address";\n' % width)
        else:
            fo.write('\t\tmem_fail("%s", %d, address, 0);\n' % (what, width))
        fo.write('\t\treturn(0);\n')
        fo.write("\t}\n")

        fo.write("}\n")

    def produce_write_x_bit(self, what, width, fo):
        ''' Produce the write functions '''
        fo.write("\n")
        fo.write("void\n")
        fo.write("m68k_%s_memory_%d(unsigned address, unsigned value)\n" % (what, width * 8))
        fo.write("{\n")
        if not 'debug' in what:
            fo.write("\tunsigned peg;\n\n")
        sep = "\t"
        for i in self.ranges:
            if i.lo < i.hi + 1 - width:
                fo.write(sep)
                sep = " else "
                i.produce_write_call(what, width, fo)

        fo.write(sep + "{\n")
        if 'debug' in what:
            fo.write('\t\tmem_error_cause = "Write %d to ndefined address";\n' % width)
        else:
            fo.write('\t\tmem_fail("%s", %d, address, value);\n' % (what, width))
        fo.write("\t}\n")

        fo.write("}\n")

    def produce_peg_find(self, fo):
        ''' Produce peg finder function '''
        fo.write("\n")
        fo.write("uint8_t *\n")
        fo.write("mem_find_peg(unsigned address)\n")
        fo.write("{")
        for i in self.ranges:
            fo.write("\n\t")
            i.produce_find_peg(fo)
        fo.write("\n\treturn (NULL);\n}\n")

def main():
    ''' test code '''
    ioc = System("ioc", 0, 1<<32)

    ioc += Range("ram", 0x00000000, 0x00080000)
    ioc += Range("ioc_eeprom", 0x80000000, 0x80008000, read_only=True)
    ioc += Range("resha_eeprom1", 0x9303e00a, 0x9303e00c, pre_read = True)
    ioc += Range("resha_eeprom2", 0x9303e300, 0xff, pre_read = True)
    ioc += Range("scsi_ctl", 0x9303e000, 0x9303e000, pre_read = True, post_write = True)
    ioc += Range("scsi_d", 0x9303e800, 0x9303e900, mask = 0x1f, pre_read = True, post_write = True)
    ioc += Range("scsi_t", 0x9303ec00, 0x9303ec20, pre_read = True, post_write = True)
    ioc += Range("io_map", 0xa1000000, 0xa1002000)

    ioc.produce_c("_memspace")
    ioc.produce_h("_memspace")


if __name__ == "__main__":
    main()
