# -*- coding: utf-8 -*-
#
# Based on:
# DualMetaFix by K. Hendricks
# KindleUnpack Copyright (c) 2009 Charles M. Hannum <root@ihack.net>
# Improvements Copyright (C) 2009-2012 P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding
# Copyright (c) 2014 Pawel Jastrzebski <pawelj@vulturis.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

########################################################################################################################
# Warning - This script is Frankenstein stiched from parts of DualMetaFix, KindleUnpack, glue, and corrugated sheets.
# I highly recommend to research original code.
# Readability of this code is quite low and should be considered as the box filled with dirty hacks.
########################################################################################################################

__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@vulturis.eu>'

import struct

number_of_pdb_records = 76
first_pdb_record = 78
mobi_header_base = 16
mobi_header_length = 20
mobi_version = 36
title_offset = 84


def getint(data, ofs, sz='L'):
    i, = struct.unpack_from('>'+sz, data, ofs)
    return i


def writeint(data, ofs, n, lenght='L'):
    if lenght == 'L':
        return data[:ofs]+struct.pack('>L', n)+data[ofs+4:]
    else:
        return data[:ofs]+struct.pack('>H', n)+data[ofs+2:]


def getsecaddr(datain, secno):
    nsec = getint(datain, number_of_pdb_records, 'H')
    if (secno < 0) | (secno >= nsec):
        raise OSError
    secstart = getint(datain, first_pdb_record+secno*8)
    if secno == nsec-1:
        secend = len(datain)
    else:
        secend = getint(datain, first_pdb_record+(secno+1)*8)
    return secstart, secend


def readsection(datain, secno):
    secstart, secend = getsecaddr(datain, secno)
    return datain[secstart:secend]


def replacesection(datain, secno, secdata):
    secstart, secend = getsecaddr(datain, secno)
    seclen = secend - secstart
    if len(secdata) != seclen:
        raise OSError
    datalst = [datain[0:secstart], secdata, datain[secend:]]
    dataout = b"".join(datalst)
    return dataout


def get_exth_params(rec0):
    ebase = mobi_header_base + getint(rec0, mobi_header_length)
    if rec0[ebase:ebase+4] != b'EXTH':
        raise OSError
    elen = getint(rec0, ebase+4)
    enum = getint(rec0, ebase+8)
    rlen = len(rec0)
    return ebase, elen, enum, rlen


def add_exth(rec0, exth_num, exth_bytes):
    ebase, elen, enum, rlen = get_exth_params(rec0)
    newrecsize = 8+len(exth_bytes)
    newrec0 = rec0[0:ebase+4] + struct.pack('>L', elen+newrecsize) + struct.pack('>L', enum+1) + \
        struct.pack('>L', exth_num) + struct.pack('>L', newrecsize) + exth_bytes+rec0[ebase+12:]
    newrec0 = writeint(newrec0, title_offset, getint(newrec0, title_offset)+newrecsize)
    sectail = newrec0[-newrecsize:]
    if sectail != b'\0'*newrecsize:
        raise OSError
    newrec0 = newrec0[0:rlen]
    return newrec0


def read_exth(rec0, exth_num):
    exth_values = []
    ebase, elen, enum, rlen = get_exth_params(rec0)
    ebase += 12
    while enum > 0:
        exth_id = getint(rec0, ebase)
        if exth_id == exth_num:
            exth_values.append(rec0[ebase+8:ebase+getint(rec0, ebase+4)])
        enum -= 1
        ebase = ebase+getint(rec0, ebase+4)
    return exth_values


def del_exth(rec0, exth_num):
    ebase, elen, enum, rlen = get_exth_params(rec0)
    ebase_idx = ebase+12
    enum_idx = 0
    while enum_idx < enum:
        exth_id = getint(rec0, ebase_idx)
        exth_size = getint(rec0, ebase_idx+4)
        if exth_id == exth_num:
            newrec0 = rec0
            newrec0 = writeint(newrec0, title_offset, getint(newrec0, title_offset)-exth_size)
            newrec0 = newrec0[:ebase_idx]+newrec0[ebase_idx+exth_size:]
            newrec0 = newrec0[0:ebase+4]+struct.pack('>L', elen-exth_size)+struct.pack('>L', enum-1)+newrec0[ebase+12:]
            newrec0 += b'\0' * exth_size
            if rlen != len(newrec0):
                raise OSError
            return newrec0
        enum_idx += 1
        ebase_idx = ebase_idx+exth_size
    return rec0


class MobiHeader:
    def __init__(self, sect, sect_number):
        self.sect = sect
        self.start = sect_number
        self.header = self.sect.load_section(self.start)
        if len(self.header) > 20 and self.header[16:20] == b'MOBI':
            self.palm = False
        elif self.sect.ident == b'TEXtREAd':
            self.palm = True
        else:
            raise OSError

        self.records, = struct.unpack_from('>H', self.header, 0x8)
        self.title = self.sect.palmname
        self.length = len(self.header)-16
        self.type = 3
        self.codepage = 1252
        self.codec = b'windows-1252'
        self.unique_id = 0
        self.version = 0
        self.has_exth = False
        self.exth = b''
        self.exth_offset = self.length + 16
        self.exth_length = 0
        self.crypto_type = 0
        self.firstnontext = self.start+self.records + 1
        self.firstresource = self.start+self.records + 1
        self.ncxidx = 0xffffffff
        self.meta_orth_index = 0xffffffff
        self.meta_infl_index = 0xffffffff
        self.skelidx = 0xffffffff
        self.dividx = 0xffffffff
        self.othidx = 0xffffffff
        self.fdst = 0xffffffff
        self.mlstart = self.sect.load_section(self.start+1)[:4]

        if self.palm:
            return

        self.length, self.type, self.codepage, self.unique_id, self.version =\
            struct.unpack('>LLLLL', self.header[20:40])
        codec_map = {
            1252: b'windows-1252',
            65001: b'utf-8',
        }
        if self.codepage in codec_map.keys():
            self.codec = codec_map[self.codepage]

        toff, tlen = struct.unpack('>II', self.header[0x54:0x5c])
        tend = toff + tlen
        self.title = self.header[toff:tend]

        exth_flag, = struct.unpack('>L', self.header[0x80:0x84])
        self.has_exth = exth_flag & 0x40
        self.exth_offset = self.length + 16
        self.exth_length = 0
        if self.has_exth:
            self.exth_length, = struct.unpack_from('>L', self.header, self.exth_offset+4)
            self.exth_length = ((self.exth_length + 3) >> 2) << 2
            self.exth = self.header[self.exth_offset:self.exth_offset+self.exth_length]
        self.crypto_type, = struct.unpack_from('>H', self.header, 0xC)

        self.firstresource, = struct.unpack_from('>L', self.header, 0x6C)
        self.firstnontext, = struct.unpack_from('>L', self.header, 0x50)
        if self.firstresource != 0xffffffff:
            self.firstresource += self.start
        if self.firstnontext != 0xffffffff:
            self.firstnontext += self.start

        if self.version < 8:
            self.meta_orth_index, = struct.unpack_from('>L', self.header, 0x28)
            if self.meta_orth_index != 0xffffffff:
                self.meta_orth_index += self.start

            # Dictionary metaInflIndex
            self.meta_infl_index, = struct.unpack_from('>L', self.header, 0x2C)
            if self.meta_infl_index != 0xffffffff:
                self.meta_infl_index += self.start

        # handle older headers without any ncxindex info and later
        # specifically 0xe4 headers
        if self.length + 16 < 0xf8:
            return

        # NCX Index
        self.ncxidx, = struct.unpack('>L', self.header[0xf4:0xf8])
        if self.ncxidx != 0xffffffff:
            self.ncxidx += self.start

        # K8 specific Indexes
        if self.start != 0 or self.version == 8:
            # Index into <xml> file skeletons in RawML
            self.skelidx, = struct.unpack_from('>L', self.header, 0xfc)
            if self.skelidx != 0xffffffff:
                self.skelidx += self.start

            # Index into <div> sections in RawML
            self.dividx, = struct.unpack_from('>L', self.header, 0xf8)
            if self.dividx != 0xffffffff:
                self.dividx += self.start

            # Index into Other files
            self.othidx, = struct.unpack_from('>L', self.header, 0x104)
            if self.othidx != 0xffffffff:
                self.othidx += self.start

            # dictionaries do not seem to use the same approach in K8's
            # so disable them
            self.meta_orth_index = 0xffffffff
            self.meta_infl_index = 0xffffffff

            # need to use the FDST record to find out how to properly unpack
            # the rawML into pieces
            # it is simply a table of start and end locations for each flow piece
            self.fdst, = struct.unpack_from('>L', self.header, 0xc0)
            self.fdstcnt, = struct.unpack_from('>L', self.header, 0xc4)
            # if cnt is 1 or less, fdst section mumber can be garbage
            if self.fdstcnt <= 1:
                self.fdst = 0xffffffff
            if self.fdst != 0xffffffff:
                self.fdst += self.start
                # setting of fdst section description properly handled in mobi_kf8proc


class Sectionizer:
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        self.palmheader = self.data[:78]
        self.palmname = self.data[:32]
        self.num_sections, = struct.unpack_from('>H', self.palmheader, 76)
        self.ident = self.palmheader[0x3C:0x3C+8]
        self.filelength = len(self.data)
        sectionsdata = struct.unpack_from('>%dL' % (self.num_sections*2), self.data, 78) + (self.filelength, 0)
        self.sectionoffsets = sectionsdata[::2]

    def load_section(self, section):
        before, after = self.sectionoffsets[section:section+2]
        return self.data[before:after]


class DualMobiMetaFix:
    def __init__(self, infile, asin):
        self.datain = open(infile, 'rb').read()
        self.datain_rec0 = readsection(self.datain, 0)

        rec0 = self.datain_rec0
        rec0 = del_exth(rec0, 501)
        rec0 = del_exth(rec0, 113)
        rec0 = del_exth(rec0, 504)
        rec0 = add_exth(rec0, 501, b"EBOK")
        rec0 = add_exth(rec0, 113, asin)
        rec0 = add_exth(rec0, 504, asin)
        self.datain = replacesection(self.datain, 0, rec0)

        ver = getint(self.datain_rec0, mobi_version)
        self.combo = (ver != 8)
        if not self.combo:
            return

        exth121 = read_exth(self.datain_rec0, 121)
        if len(exth121) == 0:
            self.combo = False
            return
        else:
            datain_kf8, = struct.unpack_from('>L', exth121[0], 0)
            if datain_kf8 == 0xffffffff:
                self.combo = False
                return
        self.datain_kfrec0 = readsection(self.datain, datain_kf8)

        rec0 = self.datain_kfrec0
        rec0 = del_exth(rec0, 501)
        rec0 = del_exth(rec0, 113)
        rec0 = del_exth(rec0, 504)
        rec0 = add_exth(rec0, 501, b"EBOK")
        rec0 = add_exth(rec0, 113, asin)
        rec0 = add_exth(rec0, 504, asin)
        self.datain = replacesection(self.datain, datain_kf8, rec0)

    def get_result(self):
        return bytes(self.datain)