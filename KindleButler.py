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

__version__ = '0.1'
__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@vulturis.eu>'

import sys
from KindleButler import Interface
from KindleButler import File

if __name__ == '__main__':
    if len(sys.argv) > 1:
        kindle = Interface.Kindle()
        file = File.MOBIFile(sys.argv[1], kindle)
        file.save_file()