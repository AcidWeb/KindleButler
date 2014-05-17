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
import paramiko
from psutil import disk_partitions, disk_usage


class Kindle:
    def __init__(self, config):
        self.config = config
        self.ssh = None
        self.path = self.find_device()
        self.need_cover = self.check_thumbnails()

    def find_device(self):
        for drive in disk_partitions(False):
            if 'removable' in drive[3]:
                if os.path.isdir(os.path.join(drive[1], 'system')) and \
                        os.path.isdir(os.path.join(drive[1], 'documents')):
                    return drive[1]
        if self.config['GENERAL']['SSHEnabled']:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                key = paramiko.RSAKey.from_private_key_file(self.config['SSH']['PrivateKeyPath'])
                ssh.connect(self.config['SSH']['KindleIP'], port=22, username='root', allow_agent=True, pkey=key)
                self.ssh = ssh
                return ''
            except:
                raise OSError('Can\'t connect to Kindle!')
        else:
            raise OSError('Not found any connected Kindle!')

    def check_thumbnails(self):
        if self.ssh:
            _, stdout, _ = self.ssh.exec_command('if test -d /mnt/us/system/thumbnails; then echo "True"; fi')
            for line in stdout.readlines():
                if line.rstrip() == 'True':
                    return True
                else:
                    return False
        else:
            if os.path.isdir(os.path.join(self.path, 'system', 'thumbnails')):
                return True
            return False

    def get_free_space(self):
        if self.ssh:
            _, stdout, _ = self.ssh.exec_command("df /mnt/us | awk \'{ print $4 }\' | tail -n 1")
            for line in stdout.readlines():
                return int(line.rstrip())*1024
        else:
            return disk_usage(self.path)[2]