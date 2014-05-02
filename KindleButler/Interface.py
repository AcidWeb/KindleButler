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
from psutil import disk_partitions, disk_usage


class Kindle:
    def __init__(self):
        self.path = self.find_device()
        self.need_cover = self.check_thumbnails()

    def find_device(self):
        for drive in disk_partitions(False):
            if 'removable' in drive[3]:
                if os.path.isdir(os.path.join(drive[1], 'system')) and \
                        os.path.isdir(os.path.join(drive[1], 'documents')):
                    return drive[1]
        raise OSError('Kindle not found!')

    def check_thumbnails(self):
        if os.path.isdir(os.path.join(self.path, 'system', 'thumbnails')):
            return True
        return False

    def get_free_space(self):
        return disk_usage(self.path)[2]