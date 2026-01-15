from modules.suboptions.automode import Automode
from modules.suboptions.advanced import Advanced
from modules.suboptions.general import General
from modules.suboptions.hotkeys import Hotkeys
from modules.suboptions.ui import UI
from utils import tk_dynamic as tkd
from tkinter import ttk


class Options(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.tabcontrol = ttk.Notebook(self)
        self.tab1 = General(main_frame, parent=self.tabcontrol)
        self.tab2 = Advanced(main_frame, parent=self.tabcontrol)
        self.tab3 = Hotkeys(main_frame, timer_frame, drop_frame, parent=self.tabcontrol)
        self.tab4 = Automode(main_frame, parent=self.tabcontrol)
        self.tab5 = UI(main_frame, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='General')
        self.tabcontrol.add(self.tab2, text='Adv')
        self.tabcontrol.add(self.tab3, text='Hotkeys')
        self.tabcontrol.add(self.tab4, text='Automode')
        self.tabcontrol.add(self.tab5, text='UI')
        self.tabcontrol.pack(expand=1, fill='both')
