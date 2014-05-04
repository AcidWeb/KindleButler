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
from subprocess import STDOUT, PIPE
from psutil import disk_partitions, disk_usage, Popen


class Kindle:
    def __init__(self, config):
        self.config = config
        self.ssh = False
        self.path = self.find_device()
        self.need_cover = self.check_thumbnails()

    def find_device(self):
        for drive in disk_partitions(False):
            if 'removable' in drive[3]:
                if os.path.isdir(os.path.join(drive[1], 'system')) and \
                        os.path.isdir(os.path.join(drive[1], 'documents')):
                    return drive[1]
        if self.config['GENERAL']['SSHEnabled']:
            ssh = Popen('"' + self.config['SSH']['PLinkPath'] + '" root@' + self.config['SSH']['KindleIP']
                        + ' whoami', stdout=PIPE, stderr=STDOUT, shell=True)
            ssh_check = ssh.wait()
            if ssh_check == 0:
                self.ssh = True
                return self.config['SSH']['KindleIP']
            else:
                raise OSError('Can\'t connect to Kindle!')
        else:
            raise OSError('Not found any connected Kindle!')

    def check_thumbnails(self):
        if self.ssh:
            ssh = Popen('"' + self.config['SSH']['PLinkPath'] + '" root@' + self.config['SSH']['KindleIP'] +
                        ' "if test -d /mnt/us/system/thumbnails; then echo "True"; fi"',
                        stdout=PIPE, stderr=STDOUT, shell=True)
            for line in ssh.stdout:
                if line.decode('utf-8').rstrip() == 'True':
                    return True
                else:
                    return False
        else:
            if os.path.isdir(os.path.join(self.path, 'system', 'thumbnails')):
                return True
            return False

    def get_free_space(self):
        if self.ssh:
            ssh = Popen('"' + self.config['SSH']['PLinkPath'] + '" root@' + self.config['SSH']['KindleIP'] +
                        ' "df /mnt/us | awk \'{ print $4 }\' | tail -n 1"', stdout=PIPE, stderr=STDOUT, shell=True)
            for line in ssh.stdout:
                return int(line.decode('utf-8').rstrip()*1024)
        else:
            return disk_usage(self.path)[2]