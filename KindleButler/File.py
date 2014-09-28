# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Pawel Jastrzebski <pawelj@iosphe.re>
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

__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@iosphe.re>'

import os
import random
import string
from imghdr import what
from io import BytesIO
from PIL import Image
from uuid import uuid4
from tempfile import gettempdir
from . import DualMetaFix
from . import KindleUnpack


class MOBIFile:
    def __init__(self, path, kindle, config, progressbar):
        self.config = config
        self.path = path
        self.kindle = kindle
        self.asin = str(uuid4())
        self.progressbar = progressbar
        self.check_file()
        if kindle.ssh:
            self.sftp = kindle.ssh.open_sftp()

    def sftp_callback(self, transferred, totalsize):
        self.progressbar.emit(str(int((transferred/totalsize)*100)), False)

    def id_generator(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    def check_file(self):
        if not os.path.isfile(self.path):
            raise OSError('The specified file does not exist!')
        file_extension = os.path.splitext(self.path)[1].upper()
        if file_extension not in ['.MOBI', '.AZW', '.AZW3']:
            raise OSError('The specified file is not E-Book!')
        mobi_header = open(self.path, 'rb').read(100)
        palm_header = mobi_header[0:78]
        ident = palm_header[0x3C:0x3C+8]
        if ident != b'BOOKMOBI':
            raise OSError('The specified file is not E-Book!')

    def save_file(self, cover):
        if self.kindle.need_cover:
            if cover != '':
                try:
                    ready_cover = Image.open(cover)
                    ready_cover.thumbnail((217, 330), Image.ANTIALIAS)
                    ready_cover = ready_cover.convert('L')
                except:
                    raise OSError('Failed to load custom cover!')
            else:
                try:
                    ready_cover = self.get_cover_image()
                except:
                    raise OSError('Failed to extract cover!')
            if self.kindle.ssh:
                tmp_cover = os.path.join(gettempdir(), 'KindleButlerCover-' + self.id_generator())
                ready_cover.save(tmp_cover, 'JPEG')
                try:
                    self.sftp.put(tmp_cover, '/mnt/us/system/thumbnails/thumbnail_' + self.asin + '_EBOK_portrait.jpg')
                    os.remove(tmp_cover)
                except:
                    raise OSError('Failed to upload cover!')
            else:
                ready_cover.save(os.path.join(self.kindle.path, 'system',
                                              'thumbnails', 'thumbnail_' + self.asin + '_EBOK_portrait.jpg'), 'JPEG')
        tmp_book = os.path.join(gettempdir(), 'KindleButlerTmpFile-' + self.id_generator())
        try:
            # noinspection PyArgumentList
            DualMetaFix.DualMobiMetaFix(self.path, tmp_book, bytes(self.asin, 'UTF-8'))
        except:
            os.remove(tmp_book)
            raise OSError('E-Book modification failed!')
        source_size = os.path.getsize(tmp_book)
        self.kindle.cleanup()
        if source_size < self.kindle.get_free_space():
            if self.kindle.ssh:
                try:
                    self.sftp.put(tmp_book, '/mnt/us/documents/' + os.path.basename(self.path), self.sftp_callback)
                    self.kindle.ssh.exec_command('dbus-send --system /default com.lab126.powerd.resuming int32:1')
                except:
                    raise OSError('Failed to upload E-Book!')
            else:
                ready_file = open(tmp_book, 'r+b')
                saved = 0
                target = open(os.path.join(self.kindle.path, 'documents', os.path.basename(self.path)), 'wb')
                while True:
                    chunk = ready_file.read(32768)
                    if not chunk:
                        break
                    target.write(chunk)
                    saved += len(chunk)
                    self.progressbar.emit(str(int((saved/source_size)*100)), False)
                ready_file.close()
            os.remove(tmp_book)
        else:
            raise OSError('Not enough space on target device!')

    def get_cover_image(self):
        section = KindleUnpack.Sectionizer(self.path)
        mhlst = [KindleUnpack.MobiHeader(section, 0)]
        mh = mhlst[0]
        metadata = mh.getmetadata()
        coverid = int(metadata['CoverOffset'][0])
        beg = mh.firstresource
        end = section.num_sections
        imgnames = []
        for i in range(beg, end):
            data = section.load_section(i)
            tmptype = data[0:4]
            if tmptype in ["FLIS", "FCIS", "FDST", "DATP"]:
                imgnames.append(None)
                continue
            elif tmptype == "SRCS":
                imgnames.append(None)
                continue
            elif tmptype == "CMET":
                imgnames.append(None)
                continue
            elif tmptype == "FONT":
                imgnames.append(None)
                continue
            elif tmptype == "RESC":
                imgnames.append(None)
                continue
            if data == chr(0xe9) + chr(0x8e) + "\r\n":
                imgnames.append(None)
                continue
            imgtype = what(None, data)
            if imgtype is None and data[0:2] == b'\xFF\xD8':
                last = len(data)
                while data[last-1:last] == b'\x00':
                    last -= 1
                if data[last-2:last] == b'\xFF\xD9':
                    imgtype = "jpeg"
            if imgtype is None:
                imgnames.append(None)
            else:
                imgnames.append(i)
            if len(imgnames)-1 == coverid:
                cover = Image.open(BytesIO(data))
                cover.thumbnail((217, 330), Image.ANTIALIAS)
                cover = cover.convert('L')
                return cover
        raise OSError