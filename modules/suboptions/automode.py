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
        self.charname_frame = tkd.LabelFrame(self, height=LAB_HEIGHT, width=LAB_WIDTH)
        self.charname_frame.propagate(False)

        self.path_label = tkd.Label(self, text='Game path')
        self.game_path = tk.StringVar()
        self.game_path.set(self.main_frame.game_path)
        self.path_entry = tkd.Entry(self, textvariable=self.game_path)

        self.path_frame = tkd.Frame(self)
        self.path_infer = tkd.Button(self.path_frame, text='Infer path', command=lambda: self.get_game_path(False), tooltip=
        'The app tries to automatically find your game path\n'
        'If nothing is returned you have to browse for the path manually')
        self.path_browse = tkd.Button(self.path_frame, text='Browse...', command=lambda: self.get_game_path(True))
        self.path_apply = tkd.Button(self.path_frame, text='Apply', command=self.activate_simple, tooltip='Apply the current specified path')

        self.simple_disclaimer = tkd.Label(self, text=
        'Disclaimer: While using simple \n'
        'automode, you need to manually \n'
        'start the first run, and manually \n'
        'end the last run (this can be done \n'
        'using hotkeys)', justify=tk.LEFT)

        # Stuff for advanced mode
        self.advanced_mode_stop = self.add_flag(
            flag_name='End run in menu',
            comment='On: Stops the current run when you exit to menu.\nOff: The run counter will continue ticking until you enter a new game',
            pack=False,
            config_section='AUTOMODE'
        )
        self.advanced_pause_on_esc_menu = self.add_flag(
            flag_name='Pause on ESC menu',
            comment='When activated, the counter will be paused when ESC menu is open inside d2 (not working for 1.14b and 1.14c)',
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
            self.path_label.pack(pady=(7, 0))
            self.path_entry.pack(fill=tk.BOTH, padx=4)
            self.path_frame.pack()
            self.path_infer.pack(side=tk.LEFT, padx=1)
            self.path_browse.pack(side=tk.LEFT)
            self.path_apply.pack(side=tk.LEFT)
            self.simple_disclaimer.pack(pady=(10,0))
        else:
            self.path_label.forget()
            self.path_entry.forget()
            self.path_frame.forget()
            self.path_infer.forget()
            self.path_browse.forget()
            self.path_apply.forget()
            self.simple_disclaimer.forget()

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

    def get_game_path(self, force_find):
        found_path = config.Config.find_game_path(force_find=force_find)
        if found_path:
            self.game_path.set(found_path)
        elif not force_find:
            tk.messagebox.showinfo('Path', f'Failed to find save folder path. Please enter manually')

    def activate_simple(self):
        self.main_frame.game_path = self.game_path.get()
        self.main_frame.toggle_automode()

        if not self.main_frame.timer_tab.automode_active:
            messagebox.showerror('Wrong path', 'Chosen path does not contain any character files (files with extensions ctl/ctlo/d2x)\n\nTry another path...')

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