import tkinter as tk
from tkinter import ttk, messagebox
from . import LAB_HEIGHT, LAB_WIDTH
from modules.suboptions.general import General
from utils import tk_dynamic as tkd, other_utils, tk_utils, config


class Automode(General):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.automode_off_btn, _, _ = self.add_automode_flag()

        self.make_widgets()
        # if self.main_frame.automode == 2 and other_utils.safe_eval(self.main_frame.cfg['AUTOMODE']['advanced_tracker_open']):
        #     self.open_stats_tracker()

    def make_widgets(self):
        self.gamemode_frame = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        self.gamemode_frame.propagate(False)

        self.gamemode_lab = tkd.Label(self.gamemode_frame, text='Game mode', tooltip=
        'If Multiplayer is selected, the .map file is used to check for updates.\n'
        'Thus, new runs begin every time you enter a new game (since your local .map files will be updated by this)\n\n'
        'If Single Player is selected the .d2s file is used to check for updates.\n'
        'Thus, a new run begins every time you leave a game (since your .d2s files are saved upon exit)')

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
        self.charname_text_lab = tkd.Label(self.charname_frame, text='Character name', tooltip=
        'Your character name is inferred from the active profile.\n'
        'Make sure the character name in your profile is matching your in-game character name')
        self.charname_val_lab = tkd.Label(self.charname_frame, textvariable=self.char_var)

        self.sp_path_lab = tkd.Label(self, text='Game path (Single Player)')
        self.SP_game_path = tk.StringVar()
        self.SP_game_path.set(self.main_frame.SP_game_path)
        self.sp_path_entry = tkd.Entry(self, textvariable=self.SP_game_path)

        self.sp_path_frame = tkd.Frame(self)
        self.sp_path_get = tkd.Button(self.sp_path_frame, text='Get', command=lambda: self.get_game_path(is_sp=True), tooltip=
        'The app tries to automatically find your game path for single player\n'
        'If nothing is returned you have to type it in manually')
        self.sp_path_apply = tkd.Button(self.sp_path_frame, text='Apply', command=self.apply_path_ch, tooltip='Apply the current specified path')

        self.mp_path_lab = tkd.Label(self, text='Game path (Multiplayer)')
        self.MP_game_path = tk.StringVar()
        self.MP_game_path.set(self.main_frame.MP_game_path)
        self.mp_path_entry = tkd.Entry(self, textvariable=self.MP_game_path)
        self.mp_path_frame = tkd.Frame(self)

        self.mp_path_get = tkd.Button(self.mp_path_frame, text='Get', command=lambda: self.get_game_path(is_sp=False), tooltip=
        'The app tries to automatically find your game path for multiplayer\n'
        'If nothing is returned you have to type it in manually')
        self.mp_path_apply = tkd.Button(self.mp_path_frame, text='Apply', command=self.apply_path_ch, tooltip='Apply the current specified path')

        # Stuff for advanced mode
        self.advanced_mode_stop = self.add_flag(
            flag_name='End run in menu',
            comment='On: Stops the current run when you exit to menu.\nOff: The run counter will continue ticking until you enter a new game',
            pack=False,
            config_section='AUTOMODE'
        )
        self.advanced_pause_on_esc_menu = self.add_flag(
            flag_name='Pause on ESC menu',
            comment='When activated, the counter will be paused when ESC menu\nis open inside d2 (not working for 1.14b and 1.14c)',
            pack=False,
            config_section='AUTOMODE'
        )
        self.advanced_automode_warning = tkd.Label(self, text=
        '"Advanced automode" is highly \n'
        'discouraged when playing\n'
        'multiplayer, as it might result\n'
        'in a ban.\n'
        'Explanation: Advanced automode\n'
        'utilizes "memory reading" of the\n'
        'D2 process to discover information\n'
        'about the current game state,\n'
        'and this could be deemed cheating.', justify=tk.LEFT)

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

            if self.game_mode.get() == 'Single Player':
                self.sp_path_lab.pack(pady=(7, 0))
                self.sp_path_entry.pack(fill=tk.BOTH, padx=4)
                self.sp_path_frame.pack()
                self.sp_path_get.pack(side=tk.LEFT, padx=1)
                self.sp_path_apply.pack(side=tk.LEFT)
            else:
                self.mp_path_lab.pack(pady=(7, 0))
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
            if first is False and not tk_utils.MessageBox(
                    msg='Activating "Advanced automode" is highly discouraged when playing multiplayer, as it might result in a ban.\n\n'
                        'Explanation: Advanced automode utilizes "memory reading" of the D2 process\n'
                        'to discover information about the current game state, and this could be deemed cheating\n\n'
                        'If you still wish to continue, click "OK"').returning:
                self.automode_var.set('0')
                return self.toggle_automode_btn(first=first, show_error=show_error)
            else:
                self.main_frame.load_memory_reader(show_err=show_error)
                if self.main_frame.advanced_error_thrown:
                    self.automode_var.set('0')
                    return self.toggle_automode_btn(first=first, show_error=show_error)
                else:
                    self.advanced_mode_stop.pack(expand=False, fill=tk.X, pady=[4,0])
                    self.advanced_pause_on_esc_menu.pack(expand=False, fill=tk.X)
                    self.advanced_automode_warning.pack(pady=6)
        else:
            if not first and self.main_frame.advanced_stats_caret.active:
                self.main_frame.advanced_stats_caret.invoke()
            self.advanced_automode_warning.forget()
            self.advanced_mode_stop.forget()
            self.advanced_pause_on_esc_menu.forget()
            self.main_frame.d2_reader = None

        if not first:
            self.main_frame.toggle_automode()

    def get_game_path(self, is_sp=True):
        found_path = config.Config.find_SP_game_path(True) if is_sp else config.Config.find_MP_game_path(True)
        if found_path:
            if is_sp:
                self.SP_game_path.set(found_path)
            else:
                self.MP_game_path.set(found_path)
        else:
            tk.messagebox.showerror('Path', f'Failed to find save folder path for {"single " if is_sp else "multi"}player. Please enter manually')

    def update_game_mode(self):
        game_mode = self.game_mode.get()

        if game_mode == 'Single Player':
            self.mp_path_lab.forget()
            self.mp_path_entry.forget()
            self.mp_path_frame.forget()
            self.mp_path_get.forget()
            self.mp_path_apply.forget()

            self.sp_path_lab.pack(pady=(0, 0))
            self.sp_path_entry.pack(fill=tk.BOTH, padx=4)
            self.sp_path_frame.pack()
            self.sp_path_get.pack(side=tk.LEFT, padx=1)
            self.sp_path_apply.pack(side=tk.LEFT)

        elif game_mode == 'Multiplayer':
            self.sp_path_lab.forget()
            self.sp_path_entry.forget()
            self.sp_path_frame.forget()
            self.sp_path_get.forget()
            self.sp_path_apply.forget()

            self.mp_path_lab.pack(pady=(0, 0))
            self.mp_path_entry.pack(fill=tk.BOTH, padx=4)
            self.mp_path_frame.pack()
            self.mp_path_get.pack(side=tk.LEFT, padx=1)
            self.mp_path_apply.pack(side=tk.LEFT)

        self.main_frame.profile_tab.game_mode.set(game_mode)
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

        cfg_mode = other_utils.safe_eval(self.main_frame.cfg['AUTOMODE']['automode'])
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