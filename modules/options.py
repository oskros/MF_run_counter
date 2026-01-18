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

        self.main_frame = main_frame

    def toggle_tab_keys_global(self, initial_run=False):
        """
        Change whether tab switching keybind (ctrl-shift-pgup/pgdn) works only when the app has focus, or also when
        the app doesn't have focus. Added this feature, as some users might have this keybind natively bound to sth else
        """
        if self.main_frame.tab_switch_keys_global:
            self.main_frame.root.unbind_all('<Control-Shift-Next>')
            self.main_frame.root.unbind_all('<Control-Shift-Prior>')
            self.tab3.hk.register(['control', 'shift', 'next'], callback=lambda event: self.main_frame.queue.put(self.main_frame.tabcontrol.next_tab))
            self.tab3.hk.register(['control', 'shift', 'prior'], callback=lambda event: self.main_frame.queue.put(self.main_frame.tabcontrol.prev_tab))
        else:
            if not initial_run:
                self.tab3.hk.unregister(['control', 'shift', 'next'])
                self.tab3.hk.unregister(['control', 'shift', 'prior'])
            self.main_frame.root.bind_all('<Control-Shift-Next>', lambda event: self.main_frame.tabcontrol.next_tab())
            self.main_frame.root.bind_all('<Control-Shift-Prior>', lambda event: self.main_frame.tabcontrol.prev_tab())
