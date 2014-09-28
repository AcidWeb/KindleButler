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

__version__ = '0.2'
__license__ = 'GPL-3'
__copyright__ = '2014, Pawel Jastrzebski <pawelj@iosphe.re>'

import os
import sys
import argparse
import configparser
from PyQt5 import QtCore, QtNetwork, QtWidgets, QtGui
from KindleButler import GUI
from KindleButler import Interface
from KindleButler import File


class QApplicationMessaging(QtWidgets.QApplication):
    jobRequest = QtCore.pyqtSignal(bytes)

    def __init__(self, argv):
        QtWidgets.QApplication.__init__(self, argv)
        self._key = 'KindleButler'
        self._timeout = 1000
        self._locked = False
        socket = QtNetwork.QLocalSocket(self)
        socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
        if not socket.waitForConnected(self._timeout):
            self._server = QtNetwork.QLocalServer(self)
            # noinspection PyUnresolvedReferences
            self._server.newConnection.connect(self.handle_message)
            self._server.listen(self._key)
        else:
            self._locked = True
        socket.disconnectFromServer()

    def __del__(self):
        if not self._locked:
            self._server.close()

    def is_running(self):
        return self._locked

    def handle_message(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.jobRequest.emit(socket.readAll().data())

    def send_message(self, message):
        socket = QtNetwork.QLocalSocket(self)
        socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
        socket.waitForConnected(self._timeout)
        socket.write(bytes(message, 'UTF-8'))
        socket.waitForBytesWritten(self._timeout)
        socket.disconnectFromServer()


class QMainWindowKindleButler(QtWidgets.QMainWindow):
    progressBarEdit = QtCore.pyqtSignal(str, bool)
    reduceQueue = QtCore.pyqtSignal()


class KindleButler(GUI.Ui_MainWindow):
    def __init__(self):
        self.setupUi(MW)
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(1)
        self.queue = -1
        self.stop = False
        self.error = False

        self.errorFont = QtGui.QFont()
        self.errorFont.setPointSize(8)
        self.errorFont.setBold(True)
        self.errorFont.setWeight(75)
        self.defaultFont = QtGui.QFont()
        self.defaultFont.setPointSize(13)
        self.defaultFont.setBold(True)
        self.defaultFont.setWeight(75)

        App.jobRequest.connect(self.handle_job)
        MW.setWindowTitle('KindleButler ' + __version__)
        MW.setWindowFlags(MW.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint & ~QtCore.Qt.WindowMinimizeButtonHint)
        MW.setWindowFlags(MW.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        MW.progressBarEdit.connect(self.progressbar_edit)
        MW.reduceQueue.connect(self.reduce_queue)
        MW.closeEvent = self.close
        MW.show()
        MW.raise_()

    def close(self, event):
        self.stop = True
        if not self.queue == -1:
            event.ignore()

    def handle_job(self, message):
        MW.raise_()
        MW.activateWindow()
        if type(message) is bytes:
            message = message.decode('UTF-8').split('#####')
        else:
            message = message.split('#####')
        if message[1] == 'True':
            cover_file = self.select_cover(message[0])
        else:
            cover_file = ''
        self.queue += 1
        self.stop = False
        worker = KindleButlerWorker(message[0], cover_file, ConfigFile)
        self.pool.start(worker)

    def select_cover(self, path):
        # noinspection PyCallByClass,PyTypeChecker
        fname = QtWidgets.QFileDialog.getOpenFileName(MW, 'Select cover', path, '*.jpg *.png *.gif')
        if sys.platform.startswith('win'):
            fname = fname[0].replace('/', '\\')
        return fname

    def progressbar_edit(self, command, error=False):
        if command.isdigit():
            if self.queue > 0:
                UI.progressBar.setFormat('Queue: ' + str(self.queue))
            else:
                UI.progressBar.setFormat('')
            UI.progressBar.setStyleSheet('color: rgb(0, 0, 0);')
            UI.progressBar.setValue(int(command))
        else:
            if error:
                UI.queue = -1
                UI.stop = True
                UI.progressBar.setFont(self.errorFont)
                UI.progressBar.setStyleSheet('color: rgb(255, 0, 0);')
            else:
                UI.progressBar.setFont(self.defaultFont)
                UI.progressBar.setStyleSheet('color: rgb(0, 0, 0);')
            UI.progressBar.setFormat(command)

    def reduce_queue(self):
        if UI.stop:
            self.queue = -1
            MW.progressBarEdit.emit('100', False)
        else:
            self.queue -= 1

    def check_config(self, config):
        error = False
        if len(config.sections()) != 2:
                error = True
        try:
            if config['GENERAL']['SSHEnabled'] != 'True' and config['GENERAL']['SSHEnabled'] != 'False':
                error = True
            elif config['GENERAL']['SSHEnabled'] == 'True':
                if not os.path.isfile(config['SSH']['PrivateKeyPath']):
                    error = True
                if not self.validate_ip(config['SSH']['KindleIP']):
                    error = True
        except KeyError:
            error = True
        if error:
            raise OSError('Failed to parse config!')

    def validate_ip(self, s):
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True


class KindleButlerWorker(QtCore.QRunnable):
    def __init__(self, input_file, cover, config):
        super(KindleButlerWorker, self).__init__()
        self.file = input_file
        self.cover = cover
        self.config = config

    def run(self):
        try:
            if not UI.stop:
                UI.check_config(self.config)
                kindle = Interface.Kindle(self.config, MW.progressBarEdit)
                file = File.MOBIFile(self.file, kindle, self.config, MW.progressBarEdit)
                file.save_file(self.cover)
                if kindle.ssh:
                    file.sftp.close()
                    kindle.ssh.close()
                MW.reduceQueue.emit()
        except OSError as e:
            MW.progressBarEdit.emit('0', False)
            MW.progressBarEdit.emit(str(e), True)


if __name__ == '__main__':
    global App, MW, UI, Arg, ConfigFile
    if getattr(sys, 'frozen', False):
        class FakeSTD(object):
            def write(self, string):
                pass

            def flush(self):
                pass
        sys.stdout = FakeSTD()
        sys.stderr = FakeSTD()
    if sys.platform.startswith('win'):
        if getattr(sys, 'frozen', False):
            os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cover', dest='custom_cover', action='store_true', help='Use custom cover')
    parser.add_argument('input_file', type=str, help='Input file')
    Arg = parser.parse_args()

    ConfigFile = configparser.ConfigParser()
    ConfigFile.read(['KindleButler.ini', os.path.expanduser('~/.KindleButler')])

    App = QApplicationMessaging(sys.argv)
    if App.is_running():
        if Arg.input_file != '':
            App.send_message(Arg.input_file + '#####' + str(Arg.custom_cover))
            sys.exit(0)
    MW = QMainWindowKindleButler()
    UI = KindleButler()
    if Arg.input_file != '':
        UI.handle_job(Arg.input_file + '#####' + str(Arg.custom_cover))
    sys.exit(App.exec_())
