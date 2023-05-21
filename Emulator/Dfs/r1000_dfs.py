#!/bin/env python3
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
   Structure of the DFS filesystem
   ===============================

   typedef uint16_t lba_t;

   The `superblock` is in sector four, (byteoffset 0x1000 on the disk)
   and contains:

       uint16_t		magic;		// == 0x7fed
       lba_t		freelist;
       lba_t		rank[8];
       xxx_t		unknown_at_14;	// copy of first free-list entry ?

   Each `rank` is an array of 256 sectors of 16 `dirent` slots each.

   A `dirent` slot is unused if the first byte is 0xff

   The `dirent` is 64 bytes and contains:

       char		filename[0x1e];
       uint16_t		hash;
       uint16_t		used_sectors;
       uint16_t		allocated_sectors;
       lba_t		first_sector;
       uint16_t		zero[10];
       uint16_t		time;		// seconds_since_midnight // 2
       uint16_t		date;		// ((YYYY - 1901) << 9) | (MM << 4) | DD
       uint16_t		unknown[1];	// Non-zero only on .M200 files

   Filenames can contain:

       $.0-9?A-Z[\\]_

   Lower case a-z is folded to upper case.

   The 16 bit `hash` is calculated as:

       hash = sum((n+1)*(x&0x3f)**3 for n, x in enumerate(filename)) & 0xffff

   The `hash` determines the `rank` and `bucket` the file belongs in:

       rank = hash >> 13
       bucket = (hash >> 5) & 0xff

   The first sector of a `freelist` entry contains:

       uint16_t		n_sectors;
       lba_t		next_entry;

   The last entry in the freelist has `next_entry=0`

   The freelist does not seem to be sorted.

'''

import sys
import collections
import struct

class DiskAccess():

    ''' A trivial class to read sectors from a disk(-image) '''

    def __init__(self, filename):
        self.filename = filename
        self.filedesc = open(filename, "rb")

    def pread(self, lba):
        ''' Read sector ``lba`` '''
        self.filedesc.seek(lba << 10, 0)
        return self.filedesc.read(1024)

class DiskLabel():

    ''' Disklabel information '''

    def __init__(self, disk):
        self.chstype = collections.namedtuple("CHS", ["cyl", "head", "sect", "lba"])
        self.disk = disk
        self.octets = disk.pread(2)
        self.disk.unfree[2] = self
        self.geom = self.make_chs(self.octets[8:12])
        self.part = []

        for j in range(12, 52, 8):
            self.part.append(
                (
                    self.make_chs(self.octets[j:j + 4]),
                    self.make_chs(self.octets[j + 4:j + 8]),
                )
            )

        self.serial = self.octets[0x36:0x3a].decode('ascii')
        self.label = self.octets[0x65:0x85].decode('ascii')

    def make_chs(self, octets):
        ''' CHS+LBA disk address '''
        cyl, head, sect = struct.unpack(">HBB", octets[:4])
        geom = getattr(self, "geom", None)
        if geom:
            lba = sect
            lba += head * geom.sect
            lba += cyl * geom.head * geom.sect
        else:
            lba = cyl * head * sect
        lba >>= 1
        return self.chstype(cyl, head, sect, lba)

def filename_hash(name):
    ''' The filename hash function '''
    return sum((n+1)*(x&0x3f)**3 for n, x in enumerate(name)) & 0xffff

class DirEnt():

    ''' A DFS directory entry '''

    def __init__(self, disk, idx, octets):
        self.disk = disk
        self.idx = idx

        rawname = octets[:30].rstrip(b'\x00')
        self.name = rawname.decode('ascii')
        ''' The name of the file '''

        self.fields = struct.unpack(">" + "H"*17, octets[30:])
        for i in range(4, 14):
            assert self.fields[i] == 0
        self.fields = self.fields[:4] + self.fields[14:]

        dfshash = filename_hash(rawname)
        self.rank = dfshash >> 13
        self.bucket = 0xff & (dfshash >> 5)
        assert self.rank == self.idx[0]
        assert self.bucket == self.idx[1]

        self.used = self.fields[1]
        ''' 1KB sectors used '''

        self.allocated = self.fields[2]
        ''' 1KB sectors allocated '''

        self.first = self.fields[3]
        ''' LBA of first data sector '''

        for i in range(self.first, self.first+self.allocated):
            self.disk.unfree[i] = self

        secs = self.fields[4] << 1
        self.hour = secs // 3600
        ''' Timestamp hour '''

        self.minute = (secs // 60) % 60
        ''' Timestamp minute '''

        self.second = secs % 60
        ''' Timestamp second (granularity: 2 seconds) '''

        self.year = (self.fields[5] >> 9) + 1901
        ''' Timestamp year [1901…2028]'''

        self.month = (self.fields[5] >> 5) & 0xf
        ''' Timestamp month '''

        self.day = self.fields[5] & 0x1f
        ''' Timestamp day '''

        self.flags = self.fields[6]

    def __repr__(self):
        ''' Return textual directory entry '''
        txt = self.name.ljust(32)
        txt += "%02d:%02d:%02d" % (self.hour, self.minute, self.second)
        txt += " %04d-%02d-%02d" % (self.year, self.month, self.day)
        txt += " %5d" % self.used
        txt += " %5d" % self.allocated
        #txt += " %5d" % self.first
        txt += " 0x%04x" % self.flags
        return txt

    def __lt__(self, value):
        ''' Compares filenames '''
        return self.name < value.name

    def yield_sectors(self):
        ''' Yield the sectors in the file '''
        for lba in range(self.first, self.first + self.used):
            yield self.disk.pread(lba)

    def read_binary(self):
        ''' Return file contents as bytes '''
        return b''.join(self.yield_sectors())

    def read_text(self):
        ''' Return file contents as string '''
        octets = b''.join(self.yield_sectors())
        first_nul = octets.find(b'\x00')
        return octets[:first_nul].decode("ASCII")

class DirRank():

    ''' One rank of 256 directory sectors '''

    def __init__(self, disk, rank, lba):
        self.disk = disk
        self.rank = rank
        self.lba = lba
        self.buckets = []
        self.dirents = []

        for order in range(256):
            self.buckets.append([])
            sector = self.disk.pread(lba + order)
            self.disk.unfree[lba + order] = self
            for pos in range(len(sector) >> 6):
                j = pos << 6
                if sector[j] != 0xff:
                    dirent = DirEnt(self.disk, (self.rank, order, pos), sector[j:j+64])
                    self.dirents.append(dirent)
                    self.buckets[-1].append(dirent)

    def __iter__(self):
        yield from self.dirents

class FreeBlock():

    ''' A freelist sector '''

    def __init__(self, disk, nbr, lba):
        self.disk = disk
        self.nbr = nbr
        self.lba = lba
        i = self.disk.pread(lba)
        self.length, self.next = struct.unpack(">HH", i[:4])
        for i in range(self.length):
            self.disk.unfree[lba + i] = self

    def __repr__(self):
        return "<Free#0x%x 0x%x => 0x%04x>" % (self.nbr, self.length, self.next)

class DFS():

    ''' A DFS filesystem '''

    def __init__(self, disk):
        self.disk = disk
        self.dirranks = []
        self.free = []
        self.files = {}

        self.sblk = self.disk.pread(4)
        self.disk.unfree[4] = self

        for rank in range(8):
            i = struct.unpack(">H", self.sblk[rank * 2 + 4:rank * 2 + 6])
            dirrank = DirRank(self.disk, rank, i[0])
            self.dirranks.append(dirrank)
            for dirent in dirrank:
                self.files[dirent.name] = dirent

        i = struct.unpack(">H", self.sblk[0x2:0x4])
        self.free.append(FreeBlock(self.disk, 0, i[0]))
        while self.free[-1].next:
            self.free.append(FreeBlock(self.disk, self.free[-1].nbr + 1, self.free[-1].next))

    def __iter__(self):
        ''' Iterate all DFS file dirents '''
        for rank in self.dirranks:
            yield from rank

    def __getitem__(self, filename):
        ''' Get a DFS dirent by name '''
        dirent = self.files.get(filename, None)
        if not dirent:
            raise NameError("DFS file '" + filename + "' not found")
        return dirent

class R1kDisk():

    ''' A Rational 1000 disk image '''

    def __init__(self, accessor=None, filename=None):
        if not accessor and filename:
            accessor = DiskAccess(filename)
        self.accessor = accessor
        self.unfree = {}
        self.lbl = DiskLabel(self)
        self.dfs = DFS(self)

    def pread(self, lba):
        ''' Read sector lba '''
        return self.accessor.pread(lba)

    def audit(self, file=sys.stdout):
        ''' Print audit of all sectors on the disk '''
        prev = 0
        last = 0
        for lba, owner in sorted(self.unfree.items()):
            if last != owner:
                if last:
                    file.write("0x%04x-0x%04x %s\n" % (last_start, prev, str(last)))
                last = owner
                last_start = lba
            while prev < lba:
                blk = self.pread(prev)
                file.write("0x%04x UnAcct %s\n" % (prev, blk[:32].hex()))
                prev += 1
            prev = lba + 1
        if last:
            file.write("0x%04x-0x%04x %s\n" % (last_start, prev, str(last)))


def main():
    ''' List DFS directory, give disk image file as command line argument '''
    disk0 = R1kDisk(filename=sys.argv[1])
    for dirent in sorted(disk0.dfs):
        print(dirent)

if __name__ == "__main__":
    main()
