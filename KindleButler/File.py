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
import sys
import imghdr
from uuid import uuid4
from . import MobiProcessing


class MOBIFile:
    def __init__(self, path, kindle):
        self.path = path
        self.check_file()
        self.kindle = kindle
        self.asin = str(uuid4())

    def check_file(self):
        if not os.path.isfile(self.path):
            raise OSError('File don\'t exist!')
        file_extension = os.path.splitext(self.path)[1].upper()
        if file_extension not in ['.MOBI', '.AZW', '.AZW3']:
            raise OSError('This is not E-Book!')
        mobi_header = open(self.path, 'rb').read(100)
        palm_header = mobi_header[0:78]
        ident = palm_header[0x3C:0x3C+8]
        if ident != b'BOOKMOBI':
            raise OSError('This is not E-Book!')

    def save_file(self):
        if self.kindle.need_cover:
            try:
                ready_cover = self.get_cover_image()
            except:
                raise OSError('Cover extraction failed!')
            open(os.path.join(self.kindle.path, 'system', 'thumbnails', 'thumbnail_' + self.asin + '_EBOK_portrait.'
                                                                        + ready_cover[0]), 'wb').write(ready_cover[1])
        try:
            # noinspection PyArgumentList
            ready_file = MobiProcessing.DualMobiMetaFix(self.path, bytes(self.asin, 'UTF-8'))
        except:
            raise OSError('Failed to clean file!')
        # noinspection PyArgumentList
        if sys.getsizeof(ready_file.get_result()) < self.kindle.get_free_space():
            open(os.path.join(self.kindle.path, 'documents',
                              os.path.basename(self.path)), 'wb').write(ready_file.get_result())
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
            imgtype = imghdr.what(None, data)
            if imgtype is None and data[0:2] == b'\xFF\xD8':
                last = len(data)
                while data[last-1:last] == b'\x00':
                    last -= 1
                if data[last-2:last] == b'\xFF\xD9':
                    imgtype = "jpeg"
            if imgtype is not None:
                return imgtype, data
