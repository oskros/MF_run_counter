from init import *
import os
import time
import webbrowser
import sound
import tk_utils
import tkinter as tk
import tk_dynamic as tkd
from tkinter import ttk
# import pandas as pd


class MFRunTimer(tkd.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self._start = 0.0
        self._session_start = time.time()
        self.session_time = 0.0
        self._laptime = 0.0
        self.is_running = False
        self.is_paused = False
        self._waiting_for_delay = False
        self.sessionstr = tk.StringVar()
        self.timestr = tk.StringVar()
        self.no_of_laps = tk.StringVar()
        self.min_lap = tk.StringVar()
        self.avg_lap = tk.StringVar()
        self.laps = []
        self._make_widgets()
        self.automode_active = self.main_frame.automode
        # self.toggle_automode(char_name=self.main_frame.tab4.char_name.get())

        self._update_session_time()

    def _make_widgets(self):
        flt = tkd.Frame(self)
        flt.pack(fill=tk.X, expand=tk.NO)
        self.c1, self.circ_id = tk_utils.add_circle(flt, 14, 'red')
        self.c1.grid(row=0, column=0, padx=3, pady=3)
        tkd.Label(flt, textvariable=self.sessionstr, font=('arial', 10)).grid(row=0, column=1, sticky=tk.N, padx=20)
        self._set_time(self.session_time, for_session=True)

        tkd.Label(self, textvariable=self.timestr, font='arial 20').pack(fill=tk.X, expand=tk.NO, pady=4)
        self._set_time(0, for_session=False)

        l2f = tkd.Frame(self)
        l2f.pack(pady=2)
        tkd.Label(l2f, text='---- Run count:', font=('arial', 12)).pack(side=tk.LEFT)
        tkd.RunLabel(l2f, textvariable=self.no_of_laps, font='arial 15').pack(side=tk.LEFT)
        tkd.Label(l2f, text='----', font=('arial', 12)).pack(side=tk.LEFT)
        self._set_laps(is_running=False)

        tkd.Label(self, textvariable=self.min_lap, font=('arial', 11)).pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        self._set_fastest()

        tkd.Label(self, textvariable=self.avg_lap, font=('arial', 11)).pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        self._set_average()

        lf0 = tkd.Frame(self)
        lf0.pack()
        scrollbar = ttk.Scrollbar(lf0, orient=tk.VERTICAL)
        self.m = tkd.Listbox(lf0, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none', font=('courier', 12))
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.bind('<MouseWheel>', lambda e: self.m.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.m.bindtags((self.m, self, "all"))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=1)

        # self.automode_lab = tk.Button(self, font='arial 24 bold', text='You are\nrunning in\nAUTOMODE!', bg='red', fg='black')
        # self.automode_lab.pack()
        # self.automode_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # self.automode_lab.config(command=self.automode_lab.destroy)

    def _update_lap_time(self):
        self._laptime = time.time() - self._start
        self._set_time(self._laptime, for_session=False)
        self._timer = self.after(50, self._update_lap_time)

    def _update_session_time(self):
        self.session_time = time.time() - self._session_start
        self._set_time(self.session_time, for_session=True)
        self._sess_timer = self.after(50, self._update_session_time)

    def _check_entered_game(self):
        stamp = os.stat(self.char_file_path).st_mtime
        if self.cached_file_stamp != stamp and not self.is_paused:
            self.StopStart()
            self.cached_file_stamp = stamp
        self._game_check = self.after(50, self._check_entered_game)

    def _set_time(self, elap, for_session):
        time_str = tk_utils.build_time_str(elap)
        if for_session:
            self.session_time_str = time_str
            self.sessionstr.set('Session time: ' + self.session_time_str)
        else:
            self.timestr.set(time_str)

    def _set_laps(self, is_running):
        run_count = len(self.laps)
        if is_running:
            run_count += 1
        self.no_of_laps.set(run_count)

    def _set_fastest(self):
        if self.laps:
            self.min_lap.set('Fastest time: %s' % tk_utils.build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % tk_utils.build_time_str(sum(self.laps) / len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    def load_from_state(self, state):
        self.laps = []
        self.m.delete(0, tk.END)
        self.session_time = state.get('session_time', 0)
        self._session_start = time.time() - self.session_time
        for lap in state.get('laps', []):
            self.Lap(lap, force=True)
        self._set_laps(is_running=False)
        self._set_fastest()
        self._set_average()
        self._set_time(self.session_time, for_session=True)

    def Start(self, play_sound=True):
        def update_start():
            if self.is_paused:
                self.Pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            self._update_lap_time()
            self.is_running = True
            self._set_laps(self.is_running)
            self._waiting_for_delay = False

        if not self.is_running:
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)
            delay = self.main_frame.run_timer_delay_seconds
            if delay > 0:
                if self._waiting_for_delay:
                    return
                self._waiting_for_delay = True
                self.after(int(delay*1000), update_start)
            else:
                update_start()

    def Stop(self, play_sound=True):
        if self.is_running:
            self.Lap(self._laptime)
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self.is_running = False
            self._set_time(0, for_session=False)
            self.after_cancel(self._timer)
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)

    def StopStart(self):
        self.Stop(play_sound=False)
        self.Start(play_sound=True)

    def Lap(self, laptime, force=False):
        if self.is_running or force:
            self.laps.append(laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + tk_utils.build_time_str(self.laps[-1]))
            self.m.yview_moveto(1)
            self._set_laps(is_running=False)
            self._set_fastest()
            self._set_average()

    def DeletePrev(self):
        if self.laps:
            self.m.delete(tk.END)
            self.laps.pop()
            self._set_laps(is_running=self.is_running)
            self._set_fastest()
            self._set_average()

    def Pause(self):
        if not self.is_paused:
            self.pause_lab = tkd.PauseButton(self, font='arial 24 bold', text='Resume', command=self.Pause,
                                             bg=self.main_frame.theme.pause_button_color,
                                             fg=self.main_frame.theme.pause_button_text)
            self.pause_lab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self.session_time, for_session=True)
            if self.is_running:
                self.after_cancel(self._timer)
            self.after_cancel(self._sess_timer)
            # if hasattr(self, '_game_check'):
            #     self.after_cancel(self._game_check)
            self.is_paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self.session_time
            if self.is_running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                self._update_lap_time()
            self._update_session_time()

            if self.automode_active:
                self.cached_file_stamp = os.stat(self.char_file_path).st_mtime
                # self._check_entered_game()
            self.is_paused = False

    def ResetLap(self):
        if self.is_running:
            self._start = time.time()
            self._laptime = 0.0
            self._set_time(self._laptime, for_session=False)

    def ResetSession(self):
        if self.is_running:
            self.Stop()
        self._start = time.time()
        self._laptime = 0.0
        self.session_time = 0.0
        self._session_start = time.time()
        self.laps = []
        self.m.delete(0, tk.END)
        self._set_time(self._laptime, for_session=False)
        self._set_time(self.session_time, for_session=True)
        self._set_laps(is_running=self.is_running)
        self._set_fastest()
        self._set_average()

    def SaveState(self):
        return dict(laps=self.laps, session_time=self.session_time)

    def toggle_automode(self, char_name):
        if self.main_frame.automode:
            if hasattr(self, '_game_check'):
                self.after_cancel(self._game_check)

            d2_save_path = os.path.normpath(self.main_frame.game_path)
            char_extension = char_name + self.main_frame.character_file_extension()
            self.char_file_path = os.path.join(d2_save_path, char_extension)

            if tk_utils.test_mapfile_path(d2_save_path, char_extension):
                self.cached_file_stamp = os.stat(self.char_file_path).st_mtime
                self._check_entered_game()

                self.automode_active = True
            else:
                self.automode_active = False
                self.main_frame.am_lab.destroy()
        elif hasattr(self, '_game_check'):
            self.after_cancel(self._game_check)
            self.automode_active = False


class Drops(tkd.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        # self.drops = []
        self.drops = dict()
        self.tab1 = tab1
        lf = tkd.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL)
        self.m = tkd.Listbox(lf, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none', font=('courier', 12))
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(2, 1), padx=1)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(2, 1), padx=0)

        btn = tkd.Button(self, text='Delete selection', command=self.delete)
        btn.bind_all('<Delete>', lambda e: self.delete())
        btn.pack(side=tk.BOTTOM, pady=(1, 2))

        # self.load_item_library()

    def AddDrop(self):
        # drop = tk_utils.mebox(entries=['Item alias', 'Stats'], title='Add drop')
        drop = tk_utils.mbox('Input drop', entry=True, title='Add drop')
        # if drop is None or drop[0] == '':
        if not drop:
            return
        run_no = len(self.tab1.laps)
        if self.tab1.is_running:
            run_no += 1
        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)
        # lookup = self.lookup_item(drop[0])
        # lookup['Stats'] = drop[1]
        # lookup['Run'] = run_no
        # self.drops.append(lookup)
        # self.display_drop(lookup)

    # def display_drop(self, lookup):
    def display_drop(self, drop, run_no):
        # self.m.insert(tk.END, 'Run %s: %s' % (str(lookup['Run']), ' '.join([lookup['Alias'], lookup['Stats']])))
        self.m.insert(tk.END, 'Run %s: %s' % (run_no, drop))
        self.m.yview_moveto(1)

    def delete(self):
        selection = self.m.curselection()
        if selection:
            # self.drops.pop(selection[0])
            ss = self.m.get(selection[0])
            run_no = ss[4:ss.find(':')]
            drop = ss[ss.find(':')+2:]
            self.drops[run_no].remove(drop)
            self.m.delete(selection[0])

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.m.delete(0, tk.END)
        # self.drops = state.get('drops', [])
        self.drops = state.get('drops', dict())
        # for drop in self.drops:
        #     self.display_drop(drop)
        for run in sorted(self.drops.keys(), key=lambda x: int(x)):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)

    # def load_item_library(self):
    #     lib = pd.read_csv('item_library.csv', index_col='Item')
    #     alias_cols = [c for c in lib.columns if c.lower().startswith('alias')]
    #     lib['Alias'] = lib[alias_cols].values.tolist()
    #     pre_dict = lib['Alias'].to_dict()
    #     self.item_alias = {l: k for k, v in pre_dict.items() for l in v if str(l) != 'nan'}
    #
    #     for c in alias_cols + ['Alias']:
    #         del lib[c]
    #     self.item_library = lib

    # def lookup_item(self, item_alias):
    #     x = item_alias.lower()
    #     item_name = ' '.join(w.capitalize() for w in self.item_alias.get(x, x).split())
    #     return dict(Name=item_name, Alias=item_alias)


class About(tkd.Frame):
    def __init__(self, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        label0 = tkd.Label(self, text="""Run counter for Diablo 2 developed in July 
and August 2019 by Oskros#1889 on Discord. Please see the README.md file 
available on Github""", justify=tk.LEFT)
        label0.pack()
        link0 = tkd.Hyperlink(self, text="Open Readme", cursor="hand2")
        link0.pack()
        link0.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo.rstrip('releases') + 'blob/master/README.md'))

        label = tkd.Label(self, text="\n\nVisit the page below for new releases")
        label.pack()

        link1 = tkd.Hyperlink(self, text="Release Hyperlink", cursor="hand2")
        link1.pack()
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo))

        lab2 = tkd.Label(self, text="\n\nCurrent version: %s" % version)
        lab2.pack(side=tk.BOTTOM)