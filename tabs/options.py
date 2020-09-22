from utils.color_themes import available_themes
import sys
import tkinter as tk
from tkinter import messagebox
from utils.color_themes import Theme
from utils import tk_dynamic as tkd, tk_utils, config, other_utils, stats_tracker
from tkinter import messagebox, ttk
import system_hotkey
import win32gui

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
        self.add_flag(flag_name='Show drops tab below', comment='Make the "drops" tabs appear below the main widget, instead of having it as a separate tab')
        self.add_flag(flag_name='Auto upload herokuapp', comment='Automatically upload newly found grailers to d2-holy-grail.herokuapp.com')
        self.add_theme_choice(comment='Select which color/style theme to use for the application')
        self.add_num_entry(flag_name='Start run delay (seconds)', comment='Add an artificial delay to the "start run" command')
        self.add_num_entry(flag_name='Auto archive (hours)', comment='Automatically calls "Archive & Reset" if more than configured number\nof hours have passed since last time the profile was used\nDisabled when equal to zero (0.0)\n\nThis is checked when app is opened and when profile is changed')

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

    def add_num_entry(self, flag_name, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text=flag_name)
        lab.pack(side=tk.LEFT)
        if comment is not None:
            tkd.create_tooltip(lab, comment)

        flag_attr = flag_name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        self.run_delay = tk.StringVar()
        self.run_delay.set(other_utils.safe_eval(self.main_frame.cfg['OPTIONS'][flag_attr]))
        tkd.RestrictedEntry(lf, textvariable=self.run_delay, num_only=True, width=13).pack(side=tk.RIGHT, padx=3)
        self.run_delay.trace_add('write', lambda name, index, mode: setattr(self.main_frame, flag_attr, float('0' + self.run_delay.get())))

    def add_flag(self, flag_name, comment=None):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
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

        if other_utils.safe_eval(self.main_frame.cfg['OPTIONS'][flag_attr]):
            on_button.invoke()
            setattr(self, flag_attr + '_invoked', True)
        else:
            off_button.invoke()
            setattr(self, flag_attr + '_invoked', False)

        off_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.config(command=lambda: self.toggle_button(flag_attr))
        on_button.pack(side=tk.RIGHT)
        off_button.pack(side=tk.RIGHT)
        return off_button, on_button

    def toggle_button(self, attr):
        val = other_utils.safe_eval(getattr(self, attr).get())
        if bool(val) == getattr(self, attr + '_invoked'):
            return
        setattr(self, attr + '_invoked', bool(val))
        setattr(self.main_frame, attr, val)
        if attr.lower() == 'always_on_top':
            self.main_frame.root.wm_attributes("-topmost", self.main_frame.always_on_top)
        elif attr.lower() == 'show_drops_tab_below':
            self.main_frame.toggle_drop_tab()
        elif attr.lower() == 'tab_switch_keys_global':
            self.main_frame.toggle_tab_keys_global()


class Automode(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.automode_off_btn, _, _ = self.add_automode_flag()

        self.make_widgets()

    def make_widgets(self):
        self.gamemode_frame = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        self.gamemode_frame.propagate(False)

        self.gamemode_lab = tkd.Label(self.gamemode_frame, text='Game mode')
        tkd.create_tooltip(self.gamemode_lab, 'If Multiplayer is selected, the .map file is used to check for updates.\nThus, new runs begin every time you enter a new game (since your local .map files will be updated by this)\n'
                                     '\nIf Single Player is selected the .d2s file is used to check for updates.\nThus, a new run begins every time you leave a game (since your .d2s files are saved upon exit)')

        self.game_mode = tk.StringVar()
        self.game_mode.set(self.main_frame.profile_tab.game_mode.get())
        self.gamemode_cb = ttk.Combobox(self.gamemode_frame, textvariable=self.game_mode, state='readonly', values=['Single Player', 'Multiplayer'])
        self.gamemode_cb.bind("<FocusOut>", lambda e: self.gamemode_cb.selection_clear())
        self.gamemode_cb.config(width=11)
        self.game_mode.trace_add('write', lambda name, index, mode: self.update_game_mode())

        self.charname_frame = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        self.charname_frame.propagate(False)

        self.char_var = tk.StringVar()
        self.char_var.set(self.main_frame.profile_tab.char_name.get())
        self.charname_text_lab = tkd.Label(self.charname_frame, text='Character name')
        tkd.create_tooltip(self.charname_text_lab, 'Your character name is inferred from the active profile.\nMake sure the character name in your profile is matching your in-game character name')
        self.charname_val_lab = tkd.Label(self.charname_frame, textvariable=self.char_var)

        self.sp_path_lab = tkd.Label(self, text='Game path (Single Player)')
        self.SP_game_path = tk.StringVar()
        self.SP_game_path.set(self.main_frame.SP_game_path)
        self.sp_path_entry = tkd.Entry(self, textvariable=self.SP_game_path)

        self.sp_path_frame = tkd.Frame(self)
        self.sp_path_get = tkd.Button(self.sp_path_frame, text='Get', command=lambda: self.get_game_path(is_sp=True),
                                      tooltip='The app tries to automatically find your game path for single player\nIf nothing is returned you have to type it in manually')
        self.sp_path_apply = tkd.Button(self.sp_path_frame, text='Apply', command=self.apply_path_ch, tooltip='Apply the current specified path')

        self.mp_path_lab = tkd.Label(self, text='Game path (Multiplayer)')
        self.MP_game_path = tk.StringVar()
        self.MP_game_path.set(self.main_frame.MP_game_path)
        self.mp_path_entry = tkd.Entry(self, textvariable=self.MP_game_path)
        self.mp_path_frame = tkd.Frame(self)

        self.mp_path_get = tkd.Button(self.mp_path_frame, text='Get', command=lambda: self.get_game_path(is_sp=False),
                                      tooltip='The app tries to automatically find your game path for multiplayer\nIf nothing is returned you have to type it in manually')
        self.mp_path_apply = tkd.Button(self.mp_path_frame, text='Apply', command=self.apply_path_ch, tooltip='Apply the current specified path')

        # Stuff for advanced mode
        self.exp_tracker = tkd.Button(self, text='Pop-up advanced\nstats tracker', height=2, font='20', command=lambda: stats_tracker.StatsTracker(main_frame=self.main_frame))

        self.toggle_automode_btn(first=True)

    def toggle_automode_btn(self, first=False, show_error=True):
        got_val = other_utils.safe_eval(self.automode_var.get())
        if first is False and self.main_frame.automode == got_val:
            return
        self.main_frame.automode = got_val
        if got_val == 1:
            self.gamemode_frame.pack(expand=False, fill=tk.X)
            self.gamemode_lab.pack(side=tk.LEFT)
            self.gamemode_cb.pack(side=tk.RIGHT)

            self.charname_frame.pack(expand=False, fill=tk.X)
            self.charname_text_lab.pack(side=tk.LEFT)
            self.charname_val_lab.pack(side=tk.RIGHT)

            self.sp_path_lab.pack(pady=[0, 0])
            self.sp_path_entry.pack(fill=tk.BOTH, padx=4)
            self.sp_path_frame.pack()
            self.sp_path_get.pack(side=tk.LEFT, padx=1)
            self.sp_path_apply.pack(side=tk.LEFT)

            self.mp_path_lab.pack(pady=[0, 0])
            self.mp_path_entry.pack(fill=tk.BOTH, padx=4)
            self.mp_path_frame.pack()
            self.mp_path_get.pack(side=tk.LEFT, padx=1)
            self.mp_path_apply.pack(side=tk.LEFT)
        else:
            self.gamemode_frame.forget()
            self.gamemode_lab.forget()
            self.gamemode_cb.forget()

            self.charname_frame.forget()
            self.charname_text_lab.forget()
            self.charname_val_lab.forget()

            self.sp_path_lab.forget()
            self.sp_path_entry.forget()
            self.sp_path_frame.forget()
            self.sp_path_get.forget()
            self.sp_path_apply.forget()

            self.mp_path_lab.forget()
            self.mp_path_entry.forget()
            self.mp_path_frame.forget()
            self.mp_path_get.forget()
            self.mp_path_apply.forget()

        if got_val == 2:
            if first is False and not tk_utils.mbox(
                    msg='Activating "Advanced automode" is highly discouraged when playing multiplayer, and might result in a ban.\n\n'
                        'Explanation: Advanced automode utilizes "Memory reading" of the D2 process\n'
                        'to discover information about the current game state, and this could be deemed cheating\n\n'
                        'If you still wish to continue, click "OK"'):
                self.automode_off_btn.invoke()
                self.automode_var.set('0')
                return self.toggle_automode_btn(first=first, show_error=show_error)
            else:
                self.main_frame.load_memory_reader(show_err=show_error)
                if not self.main_frame.is_user_admin:
                    self.automode_off_btn.invoke()
                    self.automode_var.set('0')
                    return self.toggle_automode_btn(first=first, show_error=show_error)
                else:
                    self.exp_tracker.pack(pady=20)
        else:
            self.exp_tracker.forget()

        if not first:
            self.main_frame.toggle_automode()

    def get_game_path(self, is_sp=True):
        found_path = config.Config.find_SP_game_path() if is_sp else config.Config.find_MP_game_path()
        if found_path:
            if is_sp:
                self.SP_game_path.set(found_path)
            else:
                self.MP_game_path.set(found_path)
        else:
            tk.messagebox.showerror('Path', 'Failed to find save folder path for single player. Please enter manually')

    def update_game_mode(self):
        self.main_frame.profile_tab.game_mode.set(self.game_mode.get())
        self.main_frame.toggle_automode()

    def apply_path_ch(self):
        self.main_frame.SP_game_path = self.SP_game_path.get()
        self.main_frame.MP_game_path = self.MP_game_path.get()
        self.main_frame.toggle_automode()

    def add_automode_flag(self):
        lf = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        lf.propagate(False)
        lf.pack(expand=False, fill=tk.X)

        lab = tkd.Label(lf, text='Automode', tooltip='Enable automode for monitoring when you enter and exit games')
        lab.pack(side=tk.LEFT)

        self.automode_var = tk.StringVar(lf)
        off_btn = tkd.Radiobutton(lf, text='Off', variable=self.automode_var, indicatoron=False, value=0, width=5, padx=4)
        simple_btn = tkd.Radiobutton(lf, text='Simple', variable=self.automode_var, indicatoron=False, value=1, width=5, padx=3)
        adv_btn = tkd.Radiobutton(lf, text='Advanced', variable=self.automode_var, indicatoron=False, value=2, width=7, padx=3)

        cfg_mode = other_utils.safe_eval(self.main_frame.cfg['OPTIONS']['automode'])
        if cfg_mode == 2:
            adv_btn.invoke()
        elif cfg_mode == 1:
            simple_btn.invoke()
        else:
            off_btn.invoke()

        off_btn.config(command=self.toggle_automode_btn)
        simple_btn.config(command=self.toggle_automode_btn)
        adv_btn.config(command=self.toggle_automode_btn)
        adv_btn.pack(side=tk.RIGHT)
        simple_btn.pack(side=tk.RIGHT)
        off_btn.pack(side=tk.RIGHT)
        return off_btn, simple_btn, adv_btn


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

        self.add_hotkey(label_name='Start new run', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['start_key']), func=timer_frame.stop_start)
        self.add_hotkey(label_name='End run', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['end_key']), func=timer_frame.stop)
        self.add_hotkey(label_name='Delete prev', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['delete_prev_key']), func=timer_frame.delete_prev)
        self.add_hotkey(label_name='Pause', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['pause_key']), func=timer_frame.pause)
        self.add_hotkey(label_name='Add drop', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['drop_key']), func=drop_frame.add_drop)
        self.add_hotkey(label_name='Reset lap', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['reset_key']), func=timer_frame.reset_lap)
        self.add_hotkey(label_name='Make unclickable', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['make_unclickable']), func=main_frame.set_clickthrough)

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
            self.hk.register(reg_key, callback=lambda event: '' if win32gui.FindWindow(None, 'Add drop') else self.main_frame.queue.put(func))

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
