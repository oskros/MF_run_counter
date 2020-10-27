import tkinter as tk
from modules.suboptions.general import General
from utils import tk_dynamic as tkd
from utils import other_utils


class UI(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame

        self.add_ui_flag(flag_name='Show buttons', comment='Show or hide delete and archive buttons on the UI')
        self.add_ui_flag(flag_name='Show drops section', comment='Show or hide the item drops section on the UI')
        self.add_ui_flag(flag_name='Show advanced tracker', comment='Show or hide the advanced stats tracker')

    def toggle_button(self, attr, first=False):
        val = other_utils.safe_eval(getattr(self, attr).get())
        if not first and bool(val) == getattr(self, attr + '_invoked'):
            return
        setattr(self, attr + '_invoked', bool(val))
        setattr(self.main_frame, attr, val)

        show_drops = other_utils.safe_eval(getattr(self, 'show_drops_section').get()) if hasattr(self, 'show_drops_section') else 0
        show_advanced = other_utils.safe_eval(getattr(self, 'show_advanced_tracker').get()) if hasattr(self, 'show_advanced_tracker') else 0

        if attr.lower() == 'show_buttons':
            btn_height = 30
            if val:
                self.main_frame.root.update()
                self.main_frame.root.config(height=self.main_frame.root.winfo_height() + btn_height)
                self.main_frame.btn_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
            else:
                if not first:
                    self.main_frame.root.update()
                    self.main_frame.root.config(height=self.main_frame.root.winfo_height() - btn_height)
                self.main_frame.btn_frame.forget()

        elif attr.lower() == 'show_drops_section':
            btn_height = 22
            if val:
                self.main_frame.root.update()
                self.main_frame.root.config(height=self.main_frame.root.winfo_height() + btn_height)
                self.main_frame.drops_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
            else:
                if hasattr(self.main_frame, 'drops_caret') and self.main_frame.drops_caret.active:
                    self.main_frame.drops_caret.invoke()
                if not first:
                    self.main_frame.root.update()
                    self.main_frame.root.config(height=self.main_frame.root.winfo_height() - btn_height)
                self.main_frame.drops_frame.forget()

        elif attr.lower() == 'show_advanced_tracker':
            btn_height = 22
            if val:
                self.main_frame.root.update()
                self.main_frame.root.config(height=self.main_frame.root.winfo_height() + btn_height)
                self.main_frame.adv_stats_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
            else:
                if hasattr(self.main_frame, 'advanced_stats_caret') and self.main_frame.advanced_stats_caret.active:
                    self.main_frame.advanced_stats_caret.invoke()
                if not first:
                    self.main_frame.root.update()
                    self.main_frame.root.config(height=self.main_frame.root.winfo_height() - btn_height)
                self.main_frame.adv_stats_frame.forget()

        if show_drops or show_advanced:
            self.main_frame.caret_frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        else:
            self.main_frame.caret_frame.forget()

    def add_ui_flag(self, flag_name, comment):
        attr = flag_name.lower().replace(' ', '_').replace('-', '_')
        self.add_flag(flag_name=flag_name, comment=comment, config_section='UI')
        self.toggle_button(attr, first=True)
