import tkinter as tk
import time
import win32gui, win32con
from init import *


class TranspTest:
    def __init__(self):
        self.root = tk.Tk()
        self.transp_color = "LightGray"
        self.fg = "LightSlateGray"
        self.title = 'transparent test'
        self.root.title(self.title)
        self.root.geometry('+1500+200')
        self.root.attributes('-topmost', True)

        self.start_time = time.time()
        self.root.attributes("-transparentcolor", self.transp_color)
        self.root.overrideredirect(True)

        self.make_widgets()
        self.update_time()

        self.root.after(50, self.set_clickthrough)
        self.root.mainloop()

    def make_widgets(self):
        fr = tk.Frame(self.root, bg=self.transp_color)
        fr.pack(expand=tk.Y, fill=tk.BOTH)
        l1 = tk.Label(fr, text="Hello world", font='courier 16', bg=self.transp_color, fg=self.fg)
        l1.pack(expand=tk.Y, fill=tk.BOTH)

        self.tvar = tk.StringVar()
        l2 = tk.Label(fr, textvariable=self.tvar, font='courier 16', bg=self.transp_color, fg=self.fg)
        l2.pack(expand=tk.Y, fill=tk.BOTH)

    def update_time(self):
        self.tvar.set(self.build_time_str(time.time() - self.start_time))
        self.root.after(50, self.update_time)

    @staticmethod
    def build_time_str(elap):
        hours = int(elap / 3600)
        minutes = int(elap / 60 - hours * 60.0)
        seconds = int(elap - hours * 3600.0 - minutes * 60.0)
        hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
        return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)

    def set_clickthrough(self):
        hwnd = win32gui.FindWindow(None, self.title)
        l_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        l_ex_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, l_ex_style)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.root.winfo_x(), self.root.winfo_y(), self.root.winfo_width(), self.root.winfo_height(), 0)


TranspTest()