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
from tkinter import Tk, ttk
from threading import Thread
from KindleButler import Interface
from KindleButler import File


class KindleButlerGUI:
    def __init__(self):
        self.root, self.pbar, self.label = self.draw_gui()

    def draw_gui(self):
        main = Tk()
        main.title('KindleButler')
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


class KindleButlerWorker:
    def main_thread(self, ui):
        try:
            kindle = Interface.Kindle()
            file = File.MOBIFile(sys.argv[1], kindle, ui.pbar)
            file.save_file()
            ui.root.quit()
        except OSError as e:
            ui.label.grid(row=1)
            ui.label['text'] = e


if __name__ == '__main__':
    if len(sys.argv) > 1:
        gui = KindleButlerGUI()
        Thread(target=KindleButlerWorker.main_thread, args=(None, gui)).start()
        gui.root.mainloop()
