from init import *
from options import Options
from config import Config
import github_releases
import tk_utils
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sound
import sys
import time
import os
import webbrowser
import json
exec(blocks[1])


class MFRunTimer(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self._start = 0.0
        self._session_start = time.time()
        self._sessiontime = 0.0
        self._laptime = 0.0
        self._running = False
        self._paused = False
        self.sessionstr = tk.StringVar()
        self.timestr = tk.StringVar()
        self.no_of_laps = tk.StringVar()
        self.min_lap = tk.StringVar()
        self.avg_lap = tk.StringVar()
        self.laps = []
        self._make_widgets()

        exec(blocks[5])

        self._update_session_time()

    def _make_widgets(self):
        flt = tk.Canvas(self)
        flt.pack(fill=tk.X, expand=tk.NO)
        self.c1, self.circ_id = tk_utils.add_circle(flt, 14, 'red')
        self.c1.grid(row=0, column=0, padx=3, pady=3)
        l0 = tk.Label(flt, textvariable=self.sessionstr, font=('arial', 10))
        self._set_time(self._sessiontime, for_session=True)
        l0.grid(row=0, column=1, sticky=tk.N, padx=20)

        l1 = tk.Label(self, textvariable=self.timestr, font='arial 20')
        self._set_time(0, for_session=False)
        l1.pack(fill=tk.X, expand=tk.NO, pady=4)

        l2f = tk.Frame(self)
        l2f.pack(pady=2)
        l2_1 = tk.Label(l2f, text='---- Run count:', font=('arial', 12))
        l2_1.pack(side=tk.LEFT)
        l2_2 = tk.Label(l2f, textvariable=self.no_of_laps, font='arial 15', fg='red')
        l2_2.pack(side=tk.LEFT)
        l2_3 = tk.Label(l2f, text='----', font=('arial', 12))
        l2_3.pack(side=tk.LEFT)
        self._set_laps(is_running=False)

        l3 = tk.Label(self, textvariable=self.min_lap)
        self._set_fastest()
        l3.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l3.config(font=('arial', 11))

        l4 = tk.Label(self, textvariable=self.avg_lap)
        self._set_average()
        l4.pack(fill=tk.X, expand=tk.NO, pady=3, padx=2)
        l4.config(font=('arial', 11))

        lf0 = tk.Frame(self)
        lf0.pack()
        scrollbar = tk.Scrollbar(lf0, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf0, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none')
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.bindtags((self.m, self, "all"))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_lap_time(self):
        self._laptime = time.time() - self._start
        self._set_time(self._laptime, for_session=False)
        self._timer = self.after(50, self._update_lap_time)

    def _update_session_time(self):
        self._sessiontime = time.time() - self._session_start
        self._set_time(self._sessiontime, for_session=True)
        self._sess_timer = self.after(50, self._update_session_time)

    exec(blocks[6])

    def _set_time(self, elap, for_session):
        time_str = self._build_time_str(elap)
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
            self.min_lap.set('Fastest time: %s' % self._build_time_str(min(self.laps)))
        else:
            self.min_lap.set('Fastest time: --:--:--.-')

    def _set_average(self):
        if self.laps:
            self.avg_lap.set('Average time: %s' % self._build_time_str(sum(self.laps)/len(self.laps)))
        else:
            self.avg_lap.set('Average time: --:--:--.-')

    @staticmethod
    def _build_time_str(elap):
        hours = int(elap / 3600)
        minutes = int(elap / 60 - hours * 60.0)
        seconds = int(elap - hours * 3600.0 - minutes * 60.0)
        hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
        return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)

    def load_from_state(self, state):
        self._sessiontime = state['session_time']
        self._session_start = time.time() - self._sessiontime
        for lap in state['laps']:
            self.Lap(lap, force=True)

    def Start(self, play_sound=True):
        def update_start():
            if self._paused:
                self.Pause()
            self.c1.itemconfigure(self.circ_id, fill='green3')
            self._start = time.time() - self._laptime
            self._update_lap_time()
            self._set_laps(is_running=True)
            self._running = True

        if not self._running:
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)
            delay = eval(self.main_frame.cfg.get('DEFAULT', 'run_timer_delay_seconds'))
            if delay > 0:
                self.after(int(delay*1000), update_start)
            else:
                update_start()

    def Stop(self, play_sound=True):
        if self._running:
            self.Lap(self._laptime)
            self.c1.itemconfigure(self.circ_id, fill='red')
            self._laptime = 0.0
            self._running = False
            self._set_time(0, for_session=False)
            self.after_cancel(self._timer)
            if play_sound and self.main_frame.enable_sound_effects:
                sound.queue_sound(self)

    def StopStart(self):
        self.Stop(play_sound=False)
        self.Start(play_sound=False)
        if self.main_frame.enable_sound_effects:
            sound.queue_sound(self)

    def Lap(self, laptime, force=False):
        if self._running or force:
            self.laps.append(laptime)
            str_n = ' ' * max(3 - len(str(len(self.laps))), 0) + str(len(self.laps))
            self.m.insert(tk.END, 'Run ' + str_n + ': ' + self._build_time_str(self.laps[-1]))
            self.m.yview_moveto(1)
            self._set_laps(is_running=False)
            self._set_fastest()
            self._set_average()

    def DeletePrev(self):
        if self.laps:
            self.m.delete(tk.END)
            self.laps.pop()
            self._set_laps(is_running=self._running)
            self._set_fastest()
            self._set_average()

    def Pause(self):
        if not self._paused:
            self.pause_lab = tk.Button(self.main_frame.root, font='arial 24 bold', text='Resume', bg='deep sky blue', command=self.Pause)
            self.pause_lab.pack()
            self.pause_lab.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

            self.c1.itemconfigure(self.circ_id, fill='red')
            self._set_time(self._laptime, for_session=False)
            self._set_time(self._sessiontime, for_session=True)
            if self._running:
                self.after_cancel(self._timer)
            self.after_cancel(self._sess_timer)
            exec(blocks[7])
            self._paused = True
        else:
            self.pause_lab.destroy()
            self._start = time.time() - self._laptime
            self._session_start = time.time() - self._sessiontime
            if self._running:
                self.c1.itemconfigure(self.circ_id, fill='green3')
                self._update_lap_time()
            self._update_session_time()
            exec(blocks[8])
            self._paused = False

    def ResetLap(self):
        if self._running:
            self._start = time.time()
            self._laptime = 0.0
            self._set_time(self._laptime, for_session=False)

    def ResetSession(self):
        if self._paused:
            self.Pause()
        self._start = time.time()
        self._laptime = 0.0
        self._session_start = time.time()
        self.laps = []
        self.m.delete(0, tk.END)
        self._set_time(self._laptime, for_session=False)
        self._set_time(self._sessiontime, for_session=True)
        self._set_laps(is_running=self._running)
        self._set_fastest()
        self._set_average()

    def SaveState(self):
        return dict(laps=self.laps, session_time=self._sessiontime)


class Drops(tk.Frame):
    def __init__(self, tab1, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.drops = dict()
        self.tab1 = tab1
        lf = tk.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(lf, orient=tk.VERTICAL)
        self.m = tk.Listbox(lf, selectmode=tk.EXTENDED, height=5, yscrollcommand=scrollbar.set, activestyle='none')
        self.m.bind('<FocusOut>', lambda e: self.m.selection_clear(0, tk.END))
        self.m.config(font=('courier', 12))
        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=5, padx=2)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(self, text='Delete selection', command=self.delete).pack(side=tk.BOTTOM)

    def AddDrop(self):
        drop = tk_utils.mbox('Input your drop', entry=True, title='Add drop')
        if drop is False:
            return
        run_no = len(self.tab1.laps)
        if self.tab1._running:
            run_no += 1
        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)

    def display_drop(self, drop, run_no):
        self.m.insert(tk.END, 'Run %s: %s' % (run_no, drop))
        self.m.yview_moveto(1)

    def delete(self):
        selection = self.m.curselection()
        if selection:
            ss = self.m.get(selection[0])
            run_no = ss[4:ss.find(':')]
            drop = ss[ss.find(':')+2:]
            self.drops[run_no].remove(drop)
            self.m.delete(selection[0])

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.drops = state['drops']
        for run in sorted(self.drops.keys()):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)


class Profile(tk.Frame):
    def __init__(self, main_frame, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        self.root = parent
        self.main_frame = main_frame
        self._make_widgets()

    def _make_widgets(self):
        # Choose active profile
        profile_frame = tk.Frame(self, height=25, width=238, pady=2, padx=2)
        profile_frame.propagate(False)
        profile_frame.pack()

        self.active_profile = tk.StringVar()
        self.active_profile.set(self.main_frame.active_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.active_profile, state='readonly', values=self.main_frame.profiles)
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._set_active_profile())
        self.profile_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        temp_lab = tk.Label(self, text="""
NOT WORKING YET!
        
This section is still work in progress
Hopefully I will be able to finish it soon""")
        temp_lab.pack()

        new_profile = tk.Button(profile_frame, text='New profile..', command=self._add_new_profile, borderwidth=1, height=1)
        new_profile.pack(side=tk.LEFT)

    def _set_active_profile(self):
        act = self.active_profile.get()
        self.main_frame.active_profile = act

    def _add_new_profile(self):
        xc = self.root.winfo_rootx() + self.root.winfo_width()//8
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        profile = tk_utils.mbox('Add new profile', entry=True, coords=(xc,yc))
        if profile:
            if profile in self.profile_dropdown['values']:
                messagebox.showerror('Duplicate name', 'Profile name already in use - please choose another name.')
                return
            self.main_frame.profiles.append(profile)
            self.profile_dropdown['values'] = self.main_frame.profiles


class About(tk.Frame):
    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)
        label0 = tk.Label(self, text="""Run counter for Diablo 2 developed in July 
2019 by *oskros on Path of Diablo. Please 
see the readme.md file available on Github""", justify=tk.LEFT)
        label0.pack()
        link0 = tk.Label(self, text="Open Readme", fg="blue", cursor="hand2")
        link0.pack()
        link0.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo.rstrip('releases') + 'blob/master/README.md'))

        label = tk.Label(self, text="\n\nVisit the page below for new releases")
        label.pack()

        link1 = tk.Label(self, text="Release Hyperlink", fg="blue", cursor="hand2")
        link1.pack()
        link1.bind("<Button-1>", lambda e: webbrowser.open_new(release_repo))

        lab2 = tk.Label(self, text="\n\nCurrent version: %s" % version)
        lab2.pack(side=tk.BOTTOM)


class Main(Config):
    def __init__(self):
        # Create root
        self.root = tk.Tk()

        # Build/load config file
        self.cfg = self.load_config_file()
        self.always_on_top = eval(self.cfg['FLAGS']['always_on_top'])
        self.tab_keys_global = eval(self.cfg['FLAGS']['tab_keys_global'])
        self.check_for_new_version = eval(self.cfg['FLAGS']['check_for_new_version'])
        self.enable_sound_effects = eval(self.cfg['FLAGS']['enable_sound_effects'])
        # Check for version
        if self.check_for_new_version:
            github_releases.check_newest_version()

        # Load state file
        self.state = self.load_state_file()
        self.active_profile = self.cfg['PROFILE']['active_profile']
        self.profiles = eval(self.cfg['PROFILE']['profiles'])

        # Modify root window
        self.root.resizable(False, False)
        # self.root.attributes('-type', 'dock')
        # self.root.overrideredirect(True)
        self.root.config(borderwidth=3, relief='raised', height=405, width=240)
        self.root.geometry('+%d+%d' % eval(self.cfg['DEFAULT']['window_start_position']))
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.title('MF run counter')
        self.root.focus_get()
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)
        self.root.iconbitmap(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'icon.ico'))
        self.root.pack_propagate(False)

        # Build banner image
        d2icon = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath('.')), 'd2icon.png')
        img = tk.PhotoImage(file=d2icon)
        img_panel = tk.Label(self.root, image=img)
        img_panel.pack()

        # Build tabs
        self.tabcontrol = ttk.Notebook(self.root)
        self.tab1 = MFRunTimer(self, parent=self.tabcontrol)
        self.tab2 = Drops(self.tab1, parent=self.tabcontrol)
        self.tab3 = Options(self, self.tab1, self.tab2, parent=self.tabcontrol)
        self.tab4 = Profile(self, parent=self.tabcontrol)
        self.tab5 = About(parent=self.tabcontrol)
        self.tabcontrol.add(self.tab1, text='Timer')
        self.tabcontrol.add(self.tab2, text='Drops')
        self.tabcontrol.add(self.tab3, text='Options')
        self.tabcontrol.add(self.tab4, text='Profile')
        self.tabcontrol.add(self.tab5, text='About')
        self.tabcontrol.pack(expand=1, fill='both')

        # Add buttons to main widget
        lf = tk.LabelFrame(self.root, height=35)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Start\nnew run', command=self.tab1.StopStart).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='End\nthis run', command=self.tab1.Stop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Add\ndrop', command=self.tab2.AddDrop).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Reset\nlap', command=self.tab1.ResetLap).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(lf, text='Save &\nreset', command=self.SaveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Make window drag on the banner image
        img_panel.bind("<ButtonPress-1>", self._start_move)
        img_panel.bind("<ButtonRelease-1>", self._stop_move)
        img_panel.bind("<B1-Motion>", self._on_motion)

        # Register some hidden keybinds
        self.root.bind("<Delete>", lambda event: self._delete_selection())

        # Load save state
        self.LoadState(self.state)
        self._autosave_state()

        # Open the widget
        self.root.mainloop()

    def _autosave_state(self):
        self.SaveState()
        self.root.after(30000, self._autosave_state)

    def _delete_selection(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()
        idx = tabs.index(cur_tab)
        if idx == 1:
            self.tab2.delete()

    def _next_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        nxt_idx = tabs.index(cur_tab) + 1
        if nxt_idx >= len(tabs):
            nxt_idx = 0
        self.tabcontrol.select(tabs[nxt_idx])

    def _prev_tab(self):
        tabs = self.tabcontrol.tabs()
        cur_tab = self.tabcontrol.select()

        prev_idx = tabs.index(cur_tab) - 1
        if prev_idx < 0:
            prev_idx = len(tabs) - 1
        self.tabcontrol.select(tabs[prev_idx])

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _stop_move(self, event):
        self.x = None
        self.y = None

    def _on_motion(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
        except (TypeError, AttributeError):
            return
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))

    def load_state_file(self):
        if not os.path.isfile('mf_cache.json'):
            return dict()
        with open('mf_cache.json', 'r') as fo:
            state = json.load(fo)
        return state

    def SaveReset(self):
        xc = self.root.winfo_rootx() - self.root.winfo_width()//12
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3

        if not self.tab1.laps:
            self.tab1.ResetSession()
            self.tab2.m.delete(0, tk.END)
            if os.path.isfile('mf_cache.json'):
                os.remove('mf_cache.json')
            return
        save_session = tk_utils.mbox('Would you like to save and reset session?', b1='Yes', b2='No', coords=[xc, yc])
        if save_session:
            self.Save()
            self.tab1.ResetSession()
            self.tab2.m.delete(0, tk.END)
            if os.path.isfile('mf_cache.json'):
                os.remove('mf_cache.json')

    def LoadState(self, state):
        if not state.get('laps', None):
            return
        self.tab1.load_from_state(state)
        self.tab2.load_from_state(state)

    def Save(self):
        today = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        cfg_save_path = os.path.normpath(self.cfg.get('DEFAULT', 'logging_path'))
        if cfg_save_path in ['DEFAULT', '']:
            save_path = today
        else:
            save_path = os.path.join(cfg_save_path, today)
        with open(save_path + '.txt', 'wb') as savefile:
            to_write = [
                'Total session time: ' + str(self.tab1.session_time_str) + '\r\n',
                'Total run time:     ' + self.tab1._build_time_str(sum(self.tab1.laps)) + '\r\n'
                'Average run time:   ' + self.tab1._build_time_str(sum(self.tab1.laps) / len(self.tab1.laps)) + '\r\n',
                'Fastest run time:   ' + self.tab1._build_time_str(min(self.tab1.laps)) + '\r\n',
                'Percentage spent in runs: ' + str(
                    round(sum(self.tab1.laps) * 100 / self.tab1._sessiontime, 2)) + '%\r\n',
                '\r\n'
            ]
            for s in to_write:
                savefile.write(bytes(s, 'utf-8'))

            for n, lap in enumerate(self.tab1.laps, 1):
                str_n = ' ' * max(len(str(len(self.tab1.laps))) - len(str(n)), 0) + str(n)
                run_str = 'Run ' + str_n + ': ' + self.tab1._build_time_str(lap)
                drops = self.tab2.drops.get(n, '')
                if drops:
                    run_str += ' --- ' + ', '.join(drops)
                savefile.write(bytes(run_str + '\r\n', 'utf-8'))

    def SaveState(self):
        saved_state = self.tab1.SaveState()
        saved_state.update(dict(drops=self.tab2.save_state()))
        with open('mf_cache.json', 'w') as fo:
            json.dump(saved_state, fo, indent=2)

    def Quit(self):
        if self.tab1._running:
            self.tab1.Stop()
        # xc = self.root.winfo_rootx() - self.root.winfo_width() // 12
        # yc = self.root.winfo_rooty() + self.root.winfo_height() // 3
        # confirm_quit = tk_utils.mbox('Would you like to quit?', b1='Yes', b2='No', coords=[xc, yc])
        # if confirm_quit:
        self.UpdateConfig(self)
        self.SaveState()
        os._exit(0)


Main()
