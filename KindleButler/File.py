# -*- coding: utf-8 -*-
#
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

__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@vulturis.eu>'

import os
from imghdr import what
from io import BytesIO
from PIL import Image
from uuid import uuid4
from . import MobiProcessing


class MOBIFile:
    def __init__(self, path, kindle, progressbar):
        self.path = path
        self.check_file()
        self.kindle = kindle
        self.asin = str(uuid4())
        self.progressbar = progressbar

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

    def save_file(self):
        if self.kindle.need_cover:
            try:
                ready_cover = self.get_cover_image()
            except:
                raise OSError('Failed to extract cover!')
            ready_cover.save(os.path.join(self.kindle.path, 'system', 'thumbnails', 'thumbnail_' + self.asin +
                                                                                    '_EBOK_portrait.jpg'), 'JPEG')
        try:
            # noinspection PyArgumentList
            ready_file = MobiProcessing.DualMobiMetaFix(self.path, bytes(self.asin, 'UTF-8'))
        except:
            raise OSError('E-Book modification failed!')
        ready_file, source_size = ready_file.get_result()
        if source_size < self.kindle.get_free_space():
            saved = 0
            target = open(os.path.join(self.kindle.path, 'documents', os.path.basename(self.path)), 'wb')
            while True:
                chunk = ready_file.read(32768)
                if not chunk:
                    break
                target.write(chunk)
                saved += len(chunk)
                self.progressbar['value'] = int((saved/source_size)*100)
        else:
            raise OSError('Not enough space on target device!')

    def get_cover_image(self):
        section = MobiProcessing.Sectionizer(self.path)
        mhlst = [MobiProcessing.MobiHeader(section, 0)]
        mh = mhlst[0]
        beg = mh.firstresource
        end = section.num_sections
        for i in range(beg, end):
            data = section.load_section(i)
            imgtype = what(None, data)
            if imgtype is None and data[0:2] == b'\xFF\xD8':
                last = len(data)
                while data[last-1:last] == b'\x00':
                    last -= 1
                if data[last-2:last] == b'\xFF\xD9':
                    imgtype = "jpeg"
            if imgtype is not None:
                cover = Image.open(BytesIO(data))
                cover.thumbnail((1920, 330), Image.ANTIALIAS)
                return cover