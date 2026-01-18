import tkinter as tk
from tkinter import ttk
from . import LAB_HEIGHT, LAB_WIDTH
from utils import tk_dynamic as tkd, other_utils
from utils.color_themes import available_themes, Theme


class General(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='Always on top', comment='Forces the application to appear on top of other windows (including d2)')
        self.add_flag(flag_name='Tab switch keys global', comment='Controls whether the <Ctrl-Shift-PgUp/PgDn> hotkeys are global or only works when application has focus')
        self.add_flag(flag_name='Check for new version', comment='Choose whether you want to check for new releases in Github every time the application is started')
        self.add_flag(flag_name='Enable sound effects', comment='Enable or disable sound effects when a run is started or stopped')
        self.add_theme_choice(comment='Select which color/style theme to use for the application')

    def add_theme_choice(self, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text='Active theme')
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tkd.create_tooltip(lab, comment)

        self.active_theme = tk.StringVar()
        self.active_theme.set(self.main_frame.active_theme)
        theme_choices = tkd.Combobox(lf, textvariable=self.active_theme, state='readonly', values=available_themes)
        theme_choices.bind("<FocusOut>", lambda e: theme_choices.selection_clear())
        theme_choices.bind("<<ComboboxSelected>>", lambda e: self._change_theme())
        theme_choices.config(width=11)
        theme_choices.pack(side=tk.RIGHT, fill=tk.X, padx=2)

    def _change_theme(self):
        active_theme = self.active_theme.get()
        if active_theme != self.main_frame.active_theme:
            self.main_frame.active_theme = active_theme
            self.main_frame.theme = Theme(used_theme=active_theme)
            self.main_frame.theme.apply_theme_style()
            self.main_frame.theme.update_colors()

    def add_num_entry(self, flag_name, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text=flag_name)
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tkd.create_tooltip(lab, comment)

        flag_attr = flag_name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        setattr(self, flag_attr + '_sv', tk.StringVar())
        sv = getattr(self, flag_attr + '_sv')
        sv.set(other_utils.safe_eval(self.main_frame.cfg['OPTIONS'][flag_attr]))
        tkd.RestrictedEntry(lf, textvariable=sv, num_only=True, width=13).pack(side=tk.RIGHT, padx=3)
        sv.trace_add('write', lambda name, index, mode: setattr(self.main_frame, flag_attr, float('0' + sv.get())))

    def add_flag(self, flag_name, comment=None, pack=True, config_section='OPTIONS'):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        if pack:
            lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text=flag_name)
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tkd.create_tooltip(lab, comment)

        flag_attr = flag_name.lower().replace(' ', '_').replace('-', '_')
        setattr(self, flag_attr, tk.StringVar(lf))
        sv = getattr(self, flag_attr)
        off_button = tkd.Radiobutton(lf, text='Off', variable=sv, indicatoron=False, value=False, width=4, padx=4)
        on_button = tkd.Radiobutton(lf, text='On', variable=sv, indicatoron=False, value=True, width=4, padx=3)

        if other_utils.safe_eval(self.main_frame.cfg[config_section][flag_attr]):
            on_button.invoke()
            setattr(self, flag_attr + '_invoked', True)
        else:
            off_button.invoke()
            setattr(self, flag_attr + '_invoked', False)

        off_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.pack(side=tk.RIGHT)
        off_button.pack(side=tk.RIGHT)
        return lf

    def toggle_button(self, attr):
        val = other_utils.safe_eval(getattr(self, attr).get())
        if bool(val) == getattr(self, attr + '_invoked'):
            return
        setattr(self, attr + '_invoked', bool(val))
        setattr(self.main_frame, attr, val)
        if attr.lower() == 'always_on_top':
            self.main_frame.root.wm_attributes("-topmost", self.main_frame.always_on_top)
        elif attr.lower() == 'tab_switch_keys_global':
            self.main_frame.options_tab.toggle_tab_keys_global()