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
   Fetch the R1000 firmware files from the Datamuseum.dk BitStore
   --------------------------------------------------------------
   And put them in the Infra/firmware.c "library"

'''

import http.client

def firmwarelist():
    ''' See: https://datamuseum.dk/wiki/Bits:Keyword/RATIONAL_1000/SW '''
    yield from range(30000502, 30000504)	# IOC+RESHA EEPROM
    yield from range(30002543, 30002544)	# PB011
    yield from range(30002551, 30002555)	# PA045…048
    yield from range(30002563, 30002566)	# PA025…027
    yield from range(30002578, 30002581)	# PA059, PA060, PA068
    yield from range(30002636, 30002641)	# PA040…044
    yield from range(30002886, 30002887)	# PA010-02
    yield from range(30002888, 30002889)	# PA011-02
    yield from range(30002893, 30002894)	# PA028-02
    yield from range(30003101, 30003107)	# NOVRAMS

def getone(http_conn, nbr):
    ''' Fetch one artifact from the Bitstore '''

    http_conn.request("GET", "/bits/%d" % nbr)
    resp = http_conn.getresponse()
    body = resp.read()

    for hdr in resp.getheaders():
        if hdr[0] == 'Content-Disposition':
            flds = hdr[1].split('"')
            assert flds[0] == 'attachment; filename='
            assert flds[2] == ''
            assert '..' not in flds[1]
            assert '/' not in flds[1]
            return (flds[1], body)

    return None, None

def main():
    ''' ... '''

    hconn = http.client.HTTPSConnection('datamuseum.dk')

    namelist = []
    with open("Infra/firmware.c", "w", encoding="ASCII") as file:
        file.write('/* MACHINE GENERATED, see make_firmware_c.py */\n')
        file.write('\n')
        file.write('#include <stdint.h>\n')
        file.write('#include <stdint.h>\n')
        file.write('#include <string.h>\n')
        file.write('#include <Infra/r1000.h>\n')
        for artifact in firmwarelist():
            print("Fetching", artifact)
            fname, body = getone(hconn, artifact)
            fname = fname.replace(".bin", "")
            fname = fname.replace(".BIN", "")
            cname = fname.replace("-", "_")
            namelist.append((fname, cname, len(body)))
            file.write('\nstatic uint8_t %s[0x%x] = {\n' % (cname, len(body)))
            stride = 16
            for subrange in range(0, len(body), stride):
                octets = body[subrange:subrange + stride]
                file.write("    " + ",".join("0x%02x" % x for x in octets) + ",\n")
            file.write("};\n")
            file.flush()

        file.write('\n')
        file.write('uint8_t *\n')
        file.write('Firmware_Get(const char *name, size_t *size)\n')
        file.write('{\n')
        for fname, cname, size in sorted(namelist):
            file.write('\tif (!strcmp(name, "%s")) {' % fname)
            file.write(' *size = 0x%x;' % size)
            file.write(' return(%s);' % cname)
            file.write(' }\n')
        file.write('\treturn(NULL);\n')
        file.write('}\n')
        file.write('\n')
        file.write('int\n')
        file.write('Firmware_Copy(void *dst, size_t size, const char *name)\n')
        file.write('{\n')
        file.write('\tsize_t sz;\n')
        file.write('\tuint8_t *ptr;\n')
        file.write('\n')
        file.write('\tptr = Firmware_Get(name, &sz);\n')
        file.write('\tif (ptr == NULL)\n')
        file.write('\t\treturn(-1);\n')
        file.write('\tassert(size == sz);\n')
        file.write('\tmemcpy(dst, ptr, sz);\n')
        file.write('\treturn(0);\n')
        file.write('}\n')

if __name__ == "__main__":
    main()
