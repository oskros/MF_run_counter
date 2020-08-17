from color_themes import available_themes
import sys
import tkinter as tk
from tkinter import messagebox
from color_themes import Theme
import tk_dynamic as tkd
from tkinter import messagebox, ttk
import system_hotkey
import tk_utils
import config
LAB_HEIGHT = 26
LAB_WIDTH = 179


class Options(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.tabcontrol = ttk.Notebook(self)
        self.tab1 = General(main_frame, parent=self.tabcontrol)
        self.tab2 = Hotkeys(main_frame, timer_frame, drop_frame, parent=self.tabcontrol)
        self.tab3 = Automode(main_frame, parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='General')
        self.tabcontrol.add(self.tab2, text='Hotkeys')
        self.tabcontrol.add(self.tab3, text='Automode')
        self.tabcontrol.pack(expand=1, fill='both')


class General(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='Always on top', comment='Forces the application to appear on top of other windows (including d2)')
        self.add_flag(flag_name='Tab switch keys global', comment='Controls whether the <Ctrl-Shift-PgUp/PgDn> hotkeys are global or only works when application has focus')
        self.add_flag(flag_name='Check for new version', comment='Choose whether you want to check for new releases in Github every time the application is started')
        self.add_flag(flag_name='Enable sound effects', comment='Enable or disable sound effects when a run is started or stopped')
        self.add_flag(flag_name='Pop-up drop window', comment='Make the "drops" window appear below the main widget, instead of having it as a separate tab')
        self.add_flag(flag_name='Autocomplete', comment='Enable autocompletion of drop names when adding found items')
        self.add_flag(flag_name='Item Shortnames', comment='Only works when Autocomplete is enabled!\n\nInstead of inserting the full item name, the "slang" name for the item will be used instead, if one exists.\nE.g. "Harlequin Crest" would be inserted as "Shako"')
        self.add_theme_choice(comment='Select which color/style theme to use for the application')
        self.add_delay_option(comment='Add an artificial delay to the "start run" command')

    def add_theme_choice(self, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text='Active theme')
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tk_utils.create_tooltip(lab, comment)

        self.active_theme = tk.StringVar()
        self.active_theme.set(self.main_frame.active_theme)
        theme_choices = ttk.Combobox(lf, textvariable=self.active_theme, state='readonly', values=available_themes)
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

    def _change_delay(self):
        new = self.run_delay.get()
        if new in ['', '-'] or float(new) < 0:
            return
        self.main_frame.run_timer_delay_seconds = float(self.run_delay.get())

    def add_delay_option(self, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text='Start run delay (seconds)')
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tk_utils.create_tooltip(lab, comment)

        self.run_delay = tk.StringVar()
        self.run_delay.set(eval(self.main_frame.cfg['OPTIONS']['run_timer_delay_seconds']))
        tkd.Entry(lf, textvariable=self.run_delay).pack(side=tk.RIGHT)
        self.run_delay.trace_add('write', lambda name, index, mode: self._change_delay())

    def add_flag(self, flag_name, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text=flag_name)
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tk_utils.create_tooltip(lab, comment)

        flag_attr = flag_name.lower().replace(' ', '_').replace('-', '_')
        setattr(self, flag_attr, tk.StringVar(lf))
        sv = getattr(self, flag_attr)
        off_button = tkd.Radiobutton(lf, text='Off', variable=sv, indicatoron=False, value=False, width=5)
        on_button = tkd.Radiobutton(lf, text='On', variable=sv, indicatoron=False, value=True, width=5, padx=3)

        if eval(self.main_frame.cfg['OPTIONS'][flag_attr]):
            on_button.invoke()
            setattr(self, flag_attr + '_invoked', True)
        else:
            off_button.invoke()
            setattr(self, flag_attr + '_invoked', False)

        off_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.pack(side=tk.RIGHT)
        off_button.pack(side=tk.RIGHT)

    def toggle_button(self, attr):
        val = eval(getattr(self, attr).get())
        if bool(val) == getattr(self, attr + '_invoked'):
            return
        setattr(self, attr + '_invoked', bool(val))
        setattr(self.main_frame, attr, val)
        if attr.lower() == 'always_on_top':
            self.main_frame.root.wm_attributes("-topmost", self.main_frame.always_on_top)
        elif attr.lower() == 'pop_up_drop_window':
            self.main_frame.toggle_drop_tab()
        elif attr.lower() == 'tab_switch_keys_global':
            self.main_frame.toggle_tab_keys_global()
        elif attr.lower() == 'automode':
            self.main_frame.toggle_automode()


class Automode(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.add_flag(flag_name='Automode', comment='Enables automode, which monitors your local character files for updates.\nEvery time an update is registered, the current run terminates and a new one is started')

        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text='Game mode')
        lab.pack(side=tk.LEFT)
        tk_utils.create_tooltip(lab, 'If Multiplayer is selected, the .map file is used to check for updates.\nThus, new runs begin every time you enter a new game (since your local .map files will be updated by this)\n'
                                     '\nIf Single Player is selected the .d2s file is used to check for updates.\nThus, a new run begins every time you leave a game (since your .d2s files are saved upon exit)')

        self.game_mode = tk.StringVar()
        self.game_mode.set(self.main_frame.tab4.game_mode.get())
        cb = ttk.Combobox(lf, textvariable=self.game_mode, state='readonly', values=['Single Player', 'Multiplayer'])
        cb.bind("<FocusOut>", lambda e: cb.selection_clear())
        cb.config(width=12)
        cb.pack(side=tk.RIGHT)
        self.game_mode.trace_add('write', lambda name, index, mode: self.update_game_version())

        lf2 = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf2.propagate(False)
        lf2.pack(expand=False, fill=tk.X)

        self.char_var = tk.StringVar()
        self.char_var.set(self.main_frame.tab4.char_name.get())
        cn_lab = tkd.Label(lf2, text='Character name')
        cn_lab.pack(side=tk.LEFT)
        tk_utils.create_tooltip(cn_lab, 'Your character name is inferred from the active profile.\nMake sure the character name in your profile is matching your in-game character name')
        tkd.Label(lf2, textvariable=self.char_var).pack(side=tk.RIGHT)

        tkd.Label(self, text='Game path (Single Player)').pack(pady=[10, 0])
        self.SP_game_path = tk.StringVar()
        self.SP_game_path.set(self.main_frame.SP_game_path)
        tkd.Entry(self, textvariable=self.SP_game_path).pack(fill=tk.BOTH, padx=4)
        bf1 = tkd.Frame(self)
        bf1.pack()
        tkd.Button(bf1, text='Get', command=lambda: self.get_game_path(is_sp=True)).pack(side=tk.LEFT)
        tkd.Button(bf1, text='Apply', command=self.apply_path_ch).pack(side=tk.LEFT)

        tkd.Label(self, text='Game path (Multiplayer)').pack(pady=[10,0])
        self.MP_game_path = tk.StringVar()
        self.MP_game_path.set(self.main_frame.MP_game_path)
        tkd.Entry(self, textvariable=self.MP_game_path).pack(fill=tk.BOTH, padx=4)
        bf2 = tkd.Frame(self)
        bf2.pack()
        tkd.Button(bf2, text='Get', command=lambda: self.get_game_path(is_sp=False)).pack(side=tk.LEFT)
        tkd.Button(bf2, text='Apply', command=self.apply_path_ch).pack(side=tk.LEFT)

    def get_game_path(self, is_sp=True):
        found_path = config.Config.find_SP_game_path() if is_sp else config.Config.find_MP_game_path()
        if found_path:
            if is_sp:
                self.SP_game_path.set(found_path)
            else:
                self.MP_game_path.set(found_path)
        else:
            tk.messagebox.showerror('Path', 'Failed to find save folder path for single player. Please enter manually')

    def update_game_version(self):
        self.main_frame.game_version = self.game_mode.get()
        self.main_frame.toggle_automode()

    def apply_path_ch(self):
        self.main_frame.SP_game_path = self.SP_game_path.get()
        self.main_frame.MP_game_path = self.MP_game_path.get()
        self.main_frame.toggle_automode()


class Hotkeys(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.modifier_options = system_hotkey.modifier_options
        self.character_options = system_hotkey.character_options
        self.hk = system_hotkey.SystemHotkey()

        lf = tkd.Frame(self, height=20, width=179)
        lf.pack(expand=True, fill=tk.BOTH)
        lf.propagate(False)
        tkd.Label(lf, text='Action', font='Helvetica 11 bold', justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(lf, text='Key          ', font='Helvetica 11 bold', justify=tk.LEFT, width=9).pack(side=tk.RIGHT)
        tkd.Label(lf, text=' Modifier', font='Helvetica 11 bold', justify=tk.LEFT, width=7).pack(side=tk.RIGHT)

        self.add_hotkey(label_name='Start new run', keys=eval(main_frame.cfg['KEYBINDS']['start_key']), func=timer_frame.stop_start)
        self.add_hotkey(label_name='End run', keys=eval(main_frame.cfg['KEYBINDS']['end_key']), func=timer_frame.stop)
        self.add_hotkey(label_name='Delete prev', keys=eval(main_frame.cfg['KEYBINDS']['delete_prev_key']), func=timer_frame.delete_prev)
        self.add_hotkey(label_name='Pause', keys=eval(main_frame.cfg['KEYBINDS']['pause_key']), func=timer_frame.pause)
        self.add_hotkey(label_name='Add drop', keys=eval(main_frame.cfg['KEYBINDS']['drop_key']), func=drop_frame.add_drop)
        self.add_hotkey(label_name='Reset lap', keys=eval(main_frame.cfg['KEYBINDS']['reset_key']), func=timer_frame.reset_lap)
        self.add_hotkey(label_name='Make unclickable', keys=eval(main_frame.cfg['KEYBINDS']['make_unclickable']), func=main_frame.set_clickthrough)

    def add_hotkey(self, label_name, keys, func):
        if keys[0].lower() not in map(lambda x: x.lower(), self.modifier_options) or keys[1].lower() not in map(lambda x: x.lower(), self.character_options):
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()
        default_modifier, default_key = keys
        action = label_name.replace(' ', '_').lower()
        setattr(self, '_' + action, keys)
        lf = tkd.LabelFrame(self, height=30, width=179)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)

        lab = tkd.Label(lf, text=label_name)
        lab.pack(side=tk.LEFT)

        setattr(self, action + '_e', tk.StringVar())
        key = getattr(self, action + '_e')
        key.set(default_key)
        drop2 = ttk.Combobox(lf, textvariable=key, state='readonly', values=self.character_options)
        drop2.bind("<FocusOut>", lambda e: drop2.selection_clear())
        drop2.config(width=9)
        drop2.pack(side=tk.RIGHT, fill=tk.X, padx=2)

        setattr(self, action + '_m', tk.StringVar())
        mod = getattr(self, action + '_m')
        mod.set(default_modifier)
        drop1 = ttk.Combobox(lf, textvariable=mod, state='readonly', values=self.modifier_options)
        drop1.bind("<FocusOut>", lambda e: drop1.selection_clear())
        drop1.config(width=7)
        drop1.pack(side=tk.RIGHT)

        mod.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        key.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        if default_key.lower() != 'no_bind':
            reg_key = [keys[1].lower()] if keys[0] == '' else list(map(lambda x: x.lower(), keys))
            self.hk.register(reg_key, callback=lambda event: self.main_frame.queue.put(func))

    def re_register(self, event, old_hotkey, func):
        new_hotkey = [getattr(self, event + '_m').get(), getattr(self, event + '_e').get()]
        new_lower = list(map(lambda x: x.lower(), new_hotkey))
        if new_lower in [list(x) for x in list(self.hk.keybinds.keys())]:
            messagebox.showerror('Reserved bind', 'This keybind is already in use.')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        else:
            if old_hotkey[1].lower() != 'no_bind':
                unreg = [old_hotkey[1].lower()] if old_hotkey[0] == '' else list(map(lambda x: x.lower(), old_hotkey))
                self.hk.unregister(unreg)
            if new_hotkey[1].lower() != 'no_bind':
                reg = [new_hotkey[1].lower()] if new_hotkey[0] == '' else new_lower
                self.hk.register(reg, callback=lambda event: self.main_frame.queue.put(func), overwrite=True)
            setattr(self, '_' + event, new_hotkey)
