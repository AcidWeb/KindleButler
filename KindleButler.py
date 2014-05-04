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

import os
import sys
import argparse
import configparser
from tkinter import Tk, ttk, filedialog
from threading import Thread
from KindleButler import Interface
from KindleButler import File


class KindleButlerGUI:
    def __init__(self):
        self.root, self.pbar, self.label = self.draw_gui()

    def draw_gui(self):
        main = Tk()
        main.title('KindleButler ' + __version__)
        main.resizable(0, 0)
        main.wm_attributes('-toolwindow', 1)
        x = (main.winfo_screenwidth() - main.winfo_reqwidth()) / 2
        y = (main.winfo_screenheight() - main.winfo_reqheight()) / 2
        main.geometry('+%d+%d' % (x, y))
        progressbar = ttk.Progressbar(orient='horizontal', length=200, mode='determinate')
        progressbar.grid(row=0)
        style = ttk.Style()
        style.configure('BW.TLabel', foreground='red')
        label = ttk.Label(style='BW.TLabel')
        return main, progressbar, label

    def load_file(self, source):
        fname = filedialog.askopenfilename(title='Select cover', initialdir=os.path.split(source)[0],
                                           filetypes=(('Image files', '*.jpg;*.jpeg;*.png;*.gif'),))
        return fname


class KindleButlerWorker:
    def __init__(self, input_file, cover, ui, config):
        try:
            kindle = Interface.Kindle(config)
            file = File.MOBIFile(input_file, kindle, config, ui.pbar)
            file.save_file(cover)
            ui.root.quit()
        except OSError as e:
            ui.label.grid(row=1)
            ui.label['text'] = e


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        class FakeSTD(object):
            def write(self, string):
                pass

            def flush(self):
                pass
        sys.stdout = FakeSTD()
        sys.stderr = FakeSTD()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cover', dest='custom_cover', action='store_true')
    parser.add_argument('input_file', type=str)
    args = parser.parse_args()
    configFile = configparser.ConfigParser()
    configFile.read('KindleButler.ini')
    if args.input_file != '':
        gui = KindleButlerGUI()
        if args.custom_cover:
            cover_file = gui.load_file(args.input_file)
            if cover_file == '':
                exit(0)
        else:
            cover_file = ''
        Thread(target=KindleButlerWorker, args=(args.input_file, cover_file, gui, configFile)).start()
        gui.root.mainloop()
