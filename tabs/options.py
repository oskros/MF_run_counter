from tabs.suboptions.automode import Automode
from tabs.suboptions.general import General
from tabs.suboptions.hotkeys import Hotkeys
from tabs.suboptions.ui import UI
from utils import tk_dynamic as tkd
from tkinter import ttk


class Options(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.tabcontrol = ttk.Notebook(self)
        self.tab1 = General(main_frame, parent=self.tabcontrol)
        self.tab2 = Hotkeys(main_frame, timer_frame, drop_frame, parent=self.tabcontrol)
        self.tab3 = Automode(main_frame, parent=self.tabcontrol)
        self.tab4 = UI(main_frame, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='General')
        self.tabcontrol.add(self.tab2, text='Hotkeys')
        self.tabcontrol.add(self.tab3, text='Automode')
        self.tabcontrol.add(self.tab4, text='UI')
        self.tabcontrol.pack(expand=1, fill='both')
